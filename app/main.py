"""Jyotisha — Vedic Astrology Knowledge System. FastAPI entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.api.v2.routes import router as v2_router
from app.api.v2.chart_create import router as v2_chart_create_router
from app.api.v2.rules_browser import router as v2_rules_browser_router
from app.api.v2.db_browser import router as v2_db_browser_router
from app.api.v2.today import router as v2_today_router
from app.api.v2.marriage_compatibility import router as v2_marriage_compat_router

app = FastAPI(title="జ్యోతిష — Vedic Astrology System", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)
app.include_router(v2_router)
# Phase 8 workbench-catchup routers -- kept in their own modules (chart
# creation, rule-pack browsing, DB browsing) rather than growing
# app/api/v2/routes.py past a readable size.
app.include_router(v2_chart_create_router)
app.include_router(v2_rules_browser_router)
app.include_router(v2_db_browser_router)
app.include_router(v2_today_router)
app.include_router(v2_marriage_compat_router)
