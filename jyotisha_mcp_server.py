
"""Jyotisha MCP Server — Vedic Astrology Compute & Knowledge Engine.

Exposes chart computation, horoscope file management, and Q&A tools
for Wibey AI commands and IDE integration.

Start:  python jyotisha_mcp_server.py
        (or via launchers/jyotisha-mcp.sh)

Transport: stdio (default for Wibey IDE integration)
"""
from __future__ import annotations
import json, os, re, sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from mcp.server.fastmcp import FastMCP
from scripts.compute_chart_cli import compute_full_chart

# ── MCP server ────────────────────────────────────────────────────────────────
mcp = FastMCP(
    "jyotisha",
    instructions=(
        "Jyotisha is a Swiss Ephemeris-backed Vedic astrology engine. "
        "Use compute_chart for arc-second accurate planetary positions, "
        "Vimshottari Dashas, D9 Navamsha, Yogas, and aspects. "
        "Use get_recent_horoscopes to load existing horoscope files as style reference. "
        "Always compute first — never guess planetary positions."
    ),
)

JYOTISHA_DIR = ROOT


# ─────────────────────────────────────────────────────────────────────────────
# Tool 1 — compute_chart
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
def compute_chart(
    name: str,
    dob: str,
    tob: str,
    utc_offset: float,
    lat: float,
    lon: float,
) -> dict:
    """Compute a complete Vedic horoscope chart using Swiss Ephemeris.

    Returns arc-second accurate data for:
    - D1 (Rāśi) chart: all 9 grahas + Lagna with sign, house, nakshatra, pada, state
    - D9 (Navāṁśa) chart: all grahas with sign, house, dignity, Darakaraka, Vargottama
    - Vimshottari Mahādaśā timeline (120 years) with current MD/AD/PD
    - House lords: lord planet, placement sign/house, dignity for all 12 houses
    - Special aspects (Parashari): Mars 4/7/8, Jupiter 5/7/9, Saturn 3/7/10
    - Yoga checks: Gajakesari, Budha-Āditya, Pancha-Mahāpuruṣa, Chandra-Maṅgala
    - Combustion flags with degree separation from Sun
    - Retrograde flags

    Args:
        name:       Person's full name (for labelling output)
        dob:        Date of birth in YYYY-MM-DD format
        tob:        Time of birth in HH:MM format (local time)
        utc_offset: UTC offset in hours (5.5 for IST, -5.0 for EST, 0 for UTC)
        lat:        Latitude of birth place in decimal degrees (N positive)
        lon:        Longitude of birth place in decimal degrees (E positive)

    Returns:
        dict with keys: meta, d1, d9, house_lords, aspects, yogas, dashas, current_dasha
    """
    try:
        return compute_full_chart(
            name=name, dob=dob, tob=tob,
            utc_offset=utc_offset, lat=lat, lon=lon,
        )
    except Exception as exc:
        return {"error": str(exc), "name": name, "dob": dob}


# ─────────────────────────────────────────────────────────────────────────────
# Tool 2 — get_recent_horoscopes
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
def get_recent_horoscopes(n: int = 3, person_name: Optional[str] = None) -> dict:
    """Get the most recently created horoscope MD files as style reference.

    Finds *_Jyotish_Part*.md, *_Forecast_Part*.md, and *_Jyotish.md files,
    groups them by person, and returns the N most recent persons' files.

    Args:
        n:           Number of recent persons to return (default 3)
        person_name: Optional filter — return only files matching this name

    Returns:
        dict with 'persons' list, each with name, files (path + content preview),
        and modification timestamp.
    """
    md_files = []
    patterns = ["*_Jyotish_Part*.md", "*_Forecast_Part*.md",
                "*_Jyotish.md", "*_Jyotish_*.md"]

    seen: set[str] = set()
    for pat in patterns:
        for f in JYOTISHA_DIR.glob(pat):
            if f.name not in seen and ".bak." not in f.name:
                seen.add(f.name)
                md_files.append(f)

    # Group by person (strip Part suffix)
    person_map: dict[str, list[Path]] = {}
    for f in md_files:
        stem   = f.stem
        person = re.sub(r'_(?:Part\d+|Jyotish.*|Forecast.*)$', '', stem, flags=re.IGNORECASE)
        person = re.sub(r'_(?:Part\d+|D\d+.*|Karmic.*|Dasha.*|Forecast.*|8Week.*)$', '', person)
        person = person.strip("_")
        if person_name and person_name.lower() not in person.lower():
            continue
        person_map.setdefault(person, []).append(f)

    # Sort persons by most-recent file mtime
    def person_mtime(item):
        return max(f.stat().st_mtime for f in item[1])

    sorted_persons = sorted(person_map.items(), key=person_mtime, reverse=True)[:n]

    result = {"persons": []}
    for person, files in sorted_persons:
        files_sorted = sorted(files, key=lambda f: f.name)
        person_data = {
            "name":      person,
            "last_modified": datetime.fromtimestamp(
                max(f.stat().st_mtime for f in files)
            ).strftime("%Y-%m-%d %H:%M"),
            "files": [],
        }
        for f in files_sorted:
            try:
                content = f.read_text(encoding="utf-8")
                person_data["files"].append({
                    "filename": f.name,
                    "path":     str(f),
                    "size_kb":  round(f.stat().st_size / 1024, 1),
                    "content":  content,          # full content for LLM style reference
                })
            except Exception:
                pass
        result["persons"].append(person_data)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Tool 3 — list_horoscope_files
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
def list_horoscope_files() -> dict:
    """List all horoscope MD files in the jyotisha directory.

    Returns a catalogue grouped by person with file names, sizes, and dates.
    Use this to discover available horoscopes before reading them.
    """
    md_files = list(JYOTISHA_DIR.glob("*.md"))
    md_files = [f for f in md_files if not f.name.startswith(("Jyotish_", "Shad_", "Marriage_"))]

    entries = []
    for f in sorted(md_files, key=lambda x: x.stat().st_mtime, reverse=True):
        entries.append({
            "filename":  f.name,
            "size_kb":   round(f.stat().st_size / 1024, 1),
            "modified":  datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
        })

    return {"files": entries, "count": len(entries), "directory": str(JYOTISHA_DIR)}


# ─────────────────────────────────────────────────────────────────────────────
# Tool 4 — read_horoscope_file
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
def read_horoscope_file(filename: str) -> dict:
    """Read the full content of a specific horoscope MD file.

    Args:
        filename: Just the filename (e.g. 'Karthik_Agasthya_Jyotish_Part1.md')
                  or full absolute path.

    Returns:
        dict with filename, content (full markdown text), and metadata.
    """
    p = Path(filename)
    if not p.is_absolute():
        p = JYOTISHA_DIR / filename
    if not p.exists():
        return {"error": f"File not found: {filename}", "tried": str(p)}
    try:
        content = p.read_text(encoding="utf-8")
        return {
            "filename": p.name,
            "path":     str(p),
            "size_kb":  round(p.stat().st_size / 1024, 1),
            "modified": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "content":  content,
        }
    except Exception as exc:
        return {"error": str(exc)}


# ─────────────────────────────────────────────────────────────────────────────
# Tool 5 — save_horoscope_part
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
def save_horoscope_part(
    person_name: str,
    part_number: int,
    part_label: str,
    content: str,
) -> dict:
    """Save a generated horoscope part as a markdown file.

    File is saved to the jyotisha directory following the naming convention:
    {PersonName}_Jyotish_Part{N}_{Label}.md

    Args:
        person_name: Person's name (spaces replaced with underscores)
        part_number: Part number (1, 2, 3, ...)
        part_label:  Short label for the part (e.g. 'D1_Foundation', 'Dasha_Transit')
        content:     Full markdown content to save

    Returns:
        dict with saved path and size.
    """
    safe_name = person_name.replace(" ", "_").replace("/", "_")
    safe_label = part_label.replace(" ", "_")
    filename = f"{safe_name}_Jyotish_Part{part_number}_{safe_label}.md"
    out_path = JYOTISHA_DIR / filename
    try:
        out_path.write_text(content, encoding="utf-8")
        return {
            "saved":    str(out_path),
            "filename": filename,
            "size_kb":  round(out_path.stat().st_size / 1024, 1),
        }
    except Exception as exc:
        return {"error": str(exc)}


# ─────────────────────────────────────────────────────────────────────────────
# Tool 6 — get_reference_scriptures
# ─────────────────────────────────────────────────────────────────────────────
@mcp.tool()
def get_reference_scriptures() -> dict:
    """List available Vedic astrology reference books and learning materials.

    Returns the catalogue of scripture-backed reference files in the
    jyotisha project, including BPHS, Jaimini, learning guides, and process docs.
    """
    ref_dir = JYOTISHA_DIR / "Reference books"
    entries = []
    for f in sorted(ref_dir.iterdir()) if ref_dir.exists() else []:
        if f.is_file():
            entries.append({"filename": f.name, "size_kb": round(f.stat().st_size / 1024, 1)})

    # Also list internal learning/process guides
    guide_files = []
    for pat in ["Jyotish_Learning_Part*.md", "Jyotish_Process_Guide_Part*.md",
                "Shad_Darshana_Part*.md", "Marriage_Guide_Part*.md",
                "LLM_ZERO_BRAINSTORM.md", "CONTEXT.md"]:
        for f in JYOTISHA_DIR.glob(pat):
            guide_files.append({"filename": f.name, "size_kb": round(f.stat().st_size / 1024, 1)})

    # Also list the mandatory docs/ reference files (interpretive frameworks,
    # dosha registry, domain playbooks, nakshatra framework, validation spec)
    docs_dir = JYOTISHA_DIR / "docs"
    docs_files = []
    if docs_dir.exists():
        for f in sorted(docs_dir.glob("*.md")):
            docs_files.append({"filename": f"docs/{f.name}", "size_kb": round(f.stat().st_size / 1024, 1)})

    return {
        "reference_books":   entries,
        "internal_guides":   sorted(guide_files, key=lambda x: x["filename"]),
        "mandatory_docs":    docs_files,
        "rules_pack":        "app/rules/bphs_top20_rule_cards_v1.yaml",
        "rule_api_endpoint": "/api/rules/{chart_id}",
        "note":              "Read AGENTS.md first, then the files under 'mandatory_docs' in full before interpreting any chart.",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Entrypoint
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run(transport="stdio")
