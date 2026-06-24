from pathlib import Path

# __file__ is app/core/config.py
# .parent is app/core/
# .parent.parent is app/
# .parent.parent.parent is the Project Root
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Define other global paths based on BASE_DIR
UPLOAD_DIR = BASE_DIR / "uploads"
PROFILE_PHOTOS_DIR = UPLOAD_DIR / "profile_photos"
CUSTOM_DEPT_LOGO_DIR = UPLOAD_DIR / "custom_dept_logos"

DATABASE_URL = f"sqlite:///{BASE_DIR}/data/cv_database.db"
