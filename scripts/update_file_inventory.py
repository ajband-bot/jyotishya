"""Incrementally regenerate docs/file-inventory.md's per-file AST-derived
sections (line counts + class/function signatures) from the real source
tree, WITHOUT touching hand-curated prose.

Why "incremental" and not "full regeneration from a blank page": every
`## \\`dir/\\`` section header's intro paragraph, and every individual file's
description paragraph, was originally hand-composed (not purely mechanical)
-- rewriting all of that from scratch on every run would either require
re-doing that editorial judgment programmatically (bad) or silently
drifting the prose away from what a human actually meant (worse, and
exactly the kind of silent drift AGENTS.md/this codebase's own conventions
warn against). So this script:

  1. Parses the CURRENT doc to recover every section's intro paragraph and
     every already-documented file's description paragraph (both are
     preserved verbatim).
  2. Walks the real `app/`, `scripts/`, `tests/` trees (+ jyotisha_mcp_server.py)
     for every in-scope .py file.
  3. For each of the known section prefixes, regenerates the `_N lines_`
     count and the class/function signature code block FRESH via `ast`
     (this is the part that goes stale every time code changes and is
     safe to regenerate mechanically) -- reusing the preserved description
     if the file was already documented, or synthesizing one from the
     module docstring's first paragraph if it's brand new.
  4. Splices the regenerated section bodies back into the doc, leaving
     every directory header, intro paragraph, and the separate
     "Non-Python assets" section (YAML/Jinja/data glob entries -- not
     ast-parseable) completely untouched.

Root-level `app/__init__.py` / `app/fixtures.py` / `app/main.py` have no
existing section (they were missing entirely from the original doc); this
script adds one `## \\`app/\\` (root package modules)` section for them if
it does not already exist.

Run after any change that adds/removes/renames a first-party Python file
or a top-level class/function within one -- same "run before merge" spirit
as `tests/run_suite.py`, though not currently wired into that gate.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = ROOT / "docs" / "file-inventory.md"

TARGET_SECTIONS = [
    "app/api/", "app/api/v2/", "app/db/", "app/derived/", "app/engine/",
    "app/rules/", "scripts/", "tests/unit/",
]
ROOT_APP_FILES = ["app/__init__.py", "app/fixtures.py", "app/main.py"]
ROOT_SECTION_HEADER = "## `app/` (root package modules)"
ROOT_SECTION_INTRO = (
    "Root-level `app` package files -- FastAPI process entrypoint, chart-fixture loader, and the "
    "package marker. Not grouped under any subpackage since they sit directly in `app/`."
)


def _first_line(node: ast.AST) -> str:
    ds = ast.get_docstring(node, clean=True)
    return ds.strip().split("\n")[0].strip() if ds else ""


def _render_function(node: ast.FunctionDef | ast.AsyncFunctionDef, base_indent: str = "") -> list[str]:
    lines = []
    prefix = "async def " if isinstance(node, ast.AsyncFunctionDef) else "def "
    for dec in node.decorator_list:
        lines.append(f"{base_indent}@{ast.unparse(dec)}")
    def_indent = base_indent + ("    " if node.decorator_list else "")
    args_src = ast.unparse(node.args)
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    sig = f"{def_indent}{prefix}{node.name}({args_src}){returns}"
    fl = _first_line(node)
    if fl:
        sig += f"  # {fl}"
    lines.append(sig)
    return lines


def _render_class(node: ast.ClassDef) -> list[str]:
    bases = ", ".join(ast.unparse(b) for b in node.bases)
    header = f"class {node.name}({bases}):" if bases else f"class {node.name}:"
    fl = _first_line(node)
    if fl:
        header += f"  # {fl}"
    lines = [header]
    body_lines: list[str] = []
    for stmt in node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            body_lines.append(f"    {stmt.target.id}: {ast.unparse(stmt.annotation)}")
        elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            body_lines.extend(_render_function(stmt, base_indent="    "))
    lines.extend(body_lines or ["    ..."])
    return lines


def _module_description(tree: ast.Module, max_len: int = 320) -> str:
    ds = ast.get_docstring(tree, clean=True)
    if not ds:
        return "(no module docstring)"
    paragraphs = [p.strip().replace("\n", " ") for p in re.split(r"\n\s*\n", ds) if p.strip()]
    combined = paragraphs[0] if paragraphs else ""
    i = 1
    while len(combined) < 200 and i < len(paragraphs):
        combined += " " + paragraphs[i]
        i += 1
    if len(combined) > max_len:
        cut = combined.rfind(" ", 0, max_len)
        combined = combined[: cut if cut != -1 else max_len].rstrip()
    return combined


def _generate_code_block_and_lines(relpath: str) -> tuple[int, str, ast.Module]:
    src = (ROOT / relpath).read_text()
    n_lines = len(src.splitlines())
    tree = ast.parse(src, filename=relpath)
    blocks = [
        "\n".join(_render_class(stmt)) if isinstance(stmt, ast.ClassDef) else "\n".join(_render_function(stmt))
        for stmt in tree.body
        if isinstance(stmt, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    code = "\n".join(blocks) if blocks else "(no top-level classes or functions)"
    return n_lines, code, tree


def _new_file_block(relpath: str) -> str:
    n_lines, code, tree = _generate_code_block_and_lines(relpath)
    return f"### `{relpath}`  _{n_lines} lines_\n\n{_module_description(tree)}\n\n```python\n{code}\n```\n"


def _refresh_file_block(relpath: str, old_description: str) -> str:
    n_lines, code, _tree = _generate_code_block_and_lines(relpath)
    return f"### `{relpath}`  _{n_lines} lines_\n\n{old_description}\n\n```python\n{code}\n```\n"


def _discover_python_files() -> list[str]:
    paths = []
    for base in ("app", "scripts", "tests"):
        for p in (ROOT / base).rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            paths.append(str(p.relative_to(ROOT)))
    return sorted(paths)


def regenerate() -> str:
    doc = DOC_PATH.read_text()

    section_header_re = re.compile(r"(?m)^## `([^`]+)`\n\n(.*?)(?=\n### `|\n---)", re.S)
    file_block_re = re.compile(r"### `([^`]+)`  _(\d+) lines?_\n\n(.*?)\n\n```python\n.*?\n```\n", re.S)

    sections: dict[str, dict] = {}
    for m in section_header_re.finditer(doc):
        sections[m.group(1)] = {"intro": m.group(2).rstrip(), "descriptions": {}}

    for m in file_block_re.finditer(doc):
        relpath, description = m.group(1), m.group(3).strip()
        if "*" in relpath or not relpath.endswith(".py"):
            continue
        owner = max((h for h in sections if relpath.startswith(h)), key=len, default=None)
        if owner:
            sections[owner]["descriptions"][relpath] = description

    all_py = _discover_python_files()
    headers_by_len_desc = sorted(sections.keys(), key=len, reverse=True)

    def owning_header(relpath: str) -> str | None:
        return next((h for h in headers_by_len_desc if relpath.startswith(h)), None)

    by_section: dict[str, list[str]] = {h: [] for h in sections}
    for relpath in all_py:
        h = owning_header(relpath)
        if h:
            by_section[h].append(relpath)

    for header in TARGET_SECTIONS:
        info = sections[header]
        blocks = [
            _refresh_file_block(rp, info["descriptions"][rp]) if rp in info["descriptions"] else _new_file_block(rp)
            for rp in sorted(by_section[header])
        ]
        new_body = f"## `{header}`\n\n{info['intro']}\n\n" + "\n".join(blocks)
        span_re = re.compile(r"(?m)^## `" + re.escape(header) + r"`\n\n.*?(?=\n---\n\n## )", re.S)
        m = span_re.search(doc)
        if not m:
            raise RuntimeError(f"could not locate existing span for section {header!r}")
        doc = doc[: m.start()] + new_body.rstrip() + "\n" + doc[m.end():]

    if ROOT_SECTION_HEADER not in doc:
        blocks = [_new_file_block(f) for f in ROOT_APP_FILES]
        section = f"{ROOT_SECTION_HEADER}\n\n{ROOT_SECTION_INTRO}\n\n" + "\n".join(blocks)
        marker = "## `app/api/`"
        idx = doc.index(marker)
        doc = doc[:idx] + section.rstrip() + "\n\n---\n\n" + doc[idx:]
    else:
        blocks = [_new_file_block(f) for f in ROOT_APP_FILES]  # always fresh, no prior description to preserve here
        new_body = f"{ROOT_SECTION_HEADER}\n\n{ROOT_SECTION_INTRO}\n\n" + "\n".join(blocks)
        span_re = re.compile(re.escape(ROOT_SECTION_HEADER) + r"\n\n.*?(?=\n---\n\n## )", re.S)
        m = span_re.search(doc)
        if m:
            doc = doc[: m.start()] + new_body.rstrip() + "\n" + doc[m.end():]

    total_files = len(re.findall(r"(?m)^### `[^`]+\.py`  _\d+ lines?_", doc))
    doc = re.sub(r"\*\*\d+ files\*\*(?= as of this writing)", f"**{total_files} files**", doc, count=1)

    return doc


if __name__ == "__main__":
    DOC_PATH.write_text(regenerate())
    print(f"Updated {DOC_PATH.relative_to(ROOT)}")
