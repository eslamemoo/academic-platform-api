from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db
from app.models import Publication as DBPublication

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/field-growth/{researcher_id}")
def get_field_growth(researcher_id: int, db: Session = Depends(get_db)):
    pubs = db.query(DBPublication).filter(DBPublication.researcher_id == researcher_id).all()
    growth = {}
    for pub in pubs:
        if not pub.year:
            continue
        year = str(pub.year)
        # Use main_field (if None, fallback to "Unclassified")
        field = pub.main_field if pub.main_field else "Unclassified"
        if year not in growth:
            growth[year] = {}
        growth[year][field] = growth[year].get(field, 0) + 1
    return growth

@router.get("/keyword-trends/{researcher_id}")
def get_keyword_trends(researcher_id: int, db: Session = Depends(get_db)):
    results = db.query(
        DBPublication.year,
        func.count(DBPublication.id).label('total')
    ).filter(DBPublication.researcher_id == researcher_id).group_by(DBPublication.year).all()
    return [{"year": r.year, "total": r.total} for r in results if r.year is not None]

@router.get("/global-fields")
def get_global_fields(db: Session = Depends(get_db)):
    results = db.query(
        DBPublication.main_field,
        func.count(DBPublication.id).label('count')
    ).filter(DBPublication.main_field.isnot(None)).group_by(DBPublication.main_field).all()
    return [{"field": r.main_field, "count": r.count} for r in results]
