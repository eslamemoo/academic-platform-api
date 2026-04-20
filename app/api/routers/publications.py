from fastapi import APIRouter
from app.services.fieldClassifier import classify_publications

router = APIRouter(prefix="/publications", tags=["Publications"])

@router.post("/import/google-scholar")
async def import_google_scholar(profile_url: str, serp_api_key: str):
    # This is a placeholder. In reality you would call SerpAPI or scrape.
    # For demonstration, we return a dummy classified publication.
    dummy_publications = [
        {
            "title": "Machine Learning for Wind Speed Prediction Using WRF Model (2024)",
            "authors": "ElTaweel, M.H.",
            "year": 2024,
            "journal": "Meteorological Applications",
            "source": "google_scholar"
        }
    ]
    # Classify the dummy publications
    classified = classify_publications(dummy_publications)
    return classified
