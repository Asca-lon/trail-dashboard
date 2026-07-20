import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "backend"))
os.environ.setdefault("USE_MOCK", "1")

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import api

app = api.app

app.mount("/assets", StaticFiles(directory=ROOT / "frontend" / "assets"), name="assets")
app.mount("/mock", StaticFiles(directory=ROOT / "mock"), name="mock")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(ROOT / "frontend" / "dashboard.html")


@app.get("/dashboard.js", include_in_schema=False)
def dashboard_js():
    return FileResponse(ROOT / "frontend" / "dashboard.js")


@app.get("/style.css", include_in_schema=False)
def style_css():
    return FileResponse(ROOT / "frontend" / "style.css")


app.mount("/", StaticFiles(directory=ROOT / "frontend"), name="frontend")
