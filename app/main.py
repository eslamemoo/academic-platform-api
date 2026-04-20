import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.database import engine
from app.models import Base

# Import the new modular routers
from app.api.routers import researchers, publications, analytics, latex

# --- Create the database tables on startup ---
Base.metadata.create_all(bind=engine)

# --- Create the FastAPI app ---
app = FastAPI(title="Academic Profile API")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include API Routers ---
app.include_router(researchers.router)
app.include_router(publications.router)
app.include_router(analytics.router)
app.include_router(latex.router)

# --- STATIC FILES (must be last) ---
# Ensure public directory exists if statically serving
STATIC_DIR = pathlib.Path(__file__).parent.parent / "public"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="public")