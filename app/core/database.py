from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# --- Database Setup ---
# Ensure the database file points to an external ../data/cv_database.db path
# Note: we use an absolute path representation to avoid issues depending on where uvicorn is run
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "cv_database.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# The 'check_same_thread' argument is needed for SQLite to work with FastAPI's async nature.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Helper function to get a database session ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
