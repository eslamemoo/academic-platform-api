from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
import json
import re

from app.core.database import get_db
from app.models import (
    Researcher as DBResearcher,
    Experience as DBExperience,
    Education as DBEducation,
    Publication as DBPublication,
    OptionalSection as DBOptionalSection
)
from app.schemas import FullProfile
from app.services.fieldClassifier import classify_to_main_field

router = APIRouter(tags=["Researchers"])

@router.get("/researchers/{researcher_id}")
def get_researcher(researcher_id: int, db: Session = Depends(get_db)):
    researcher = db.query(DBResearcher).filter(DBResearcher.id == researcher_id).first()
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")
    return {
        "researcher": researcher,
        "experiences": researcher.experiences,
        "educations": researcher.educations,
        "publications": researcher.publications,
        "optional_sections": researcher.optional_sections,
    }

@router.post("/researchers/", status_code=201)
def save_researcher(profile: FullProfile, db: Session = Depends(get_db)):
    researcher_data = profile.researcher.dict()
    
    if researcher_data.get('id'):
        db_researcher = db.query(DBResearcher).filter(DBResearcher.id == researcher_data['id']).first()
        if not db_researcher:
            raise HTTPException(status_code=404, detail="Researcher not found")
        for key, value in researcher_data.items():
            setattr(db_researcher, key, value)
        db.query(DBExperience).filter(DBExperience.researcher_id == db_researcher.id).delete()
        db.query(DBEducation).filter(DBEducation.researcher_id == db_researcher.id).delete()
        db.query(DBPublication).filter(DBPublication.researcher_id == db_researcher.id).delete()
        db.query(DBOptionalSection).filter(DBOptionalSection.researcher_id == db_researcher.id).delete()
        db.commit()
        db.refresh(db_researcher)
        researcher_id = db_researcher.id
    else:
        db_researcher = DBResearcher(**researcher_data)
        db.add(db_researcher)
        db.commit()
        db.refresh(db_researcher)
        researcher_id = db_researcher.id

    # Insert related data
    for exp in profile.experiences:
        db_exp = DBExperience(researcher_id=researcher_id, **exp.dict())
        db.add(db_exp)
    for edu in profile.educations:
        db_edu = DBEducation(researcher_id=researcher_id, **edu.dict())
        db.add(db_edu)
    
    # Process publications: extract year, classify main field and subfield
    for pub in profile.publications:
        pub_data = pub.dict()
        title = pub_data.get('title', '')
        # Extract year from title (e.g., "2023")
        year_match = re.search(r'\b(19|20)\d{2}\b', title)
        if year_match and not pub_data.get('year'):
            pub_data['year'] = int(year_match.group(0))
        # Classify main field and subfield using the hierarchical classifier
        main_field, subfield = classify_to_main_field(title)
        pub_data['main_field'] = main_field
        pub_data['subfield'] = subfield
        # Keep research_fields as JSON list of main_field for backward compatibility
        pub_data['research_fields'] = json.dumps([main_field]) if main_field else None
        
        db_pub = DBPublication(researcher_id=researcher_id, **pub_data)
        db.add(db_pub)
    
    for opt in profile.optional_sections:
        db_opt = DBOptionalSection(researcher_id=researcher_id, **opt.dict())
        db.add(db_opt)
    
    db.commit()
    return {"success": True, "researcherId": researcher_id}

@router.delete("/researchers/{researcher_id}")
def delete_researcher(researcher_id: int, db: Session = Depends(get_db)):
    researcher = db.query(DBResearcher).filter(DBResearcher.id == researcher_id).first()
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")
    db.delete(researcher)
    db.commit()
    return {"success": True, "message": f"Researcher {researcher_id} deleted"}

@router.get("/researchers/")
def list_researchers(db: Session = Depends(get_db)):
    researchers = db.query(DBResearcher.id, DBResearcher.full_name).all()
    return [{"id": r.id, "name": r.full_name} for r in researchers]

@router.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    file_size = len(contents)
    return {"filename": file.filename, "size": file_size}
