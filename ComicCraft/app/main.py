from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
# Prefer the conventional project-level .env. The secondary location supports
# the existing IDE setup while keeping environment variables supplied by the OS
# as the highest-priority values.
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR / "env" / "new.env", override=False)

app = FastAPI(title="ComicCraft - AI Comic Story Creator", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

from app.routes import router
app.include_router(router)
