from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from sqlalchemy.orm import Session
import shutil
from pathlib import Path
import json
import re
from fastapi.responses import FileResponse
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
from app.core.config import BASE_DIR, UPLOAD_DIR, PROFILE_PHOTOS_DIR, CUSTOM_DEPT_LOGO_DIR

router = APIRouter(tags=["Researchers"])


@router.get("/get/researcher/{researcher_uuid}")
def get_researcher(researcher_uuid: str, db: Session = Depends(get_db)):
    # Query using the secure UUID token instead of integer IDs
    researcher = db.query(DBResearcher).filter(DBResearcher.uuid == researcher_uuid).first()
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")
    return {
        "researcher": researcher,
        "experiences": researcher.experiences,
        "educations": researcher.educations,
        "publications": researcher.publications,
        "optional_sections": researcher.optional_sections,
    }


@router.post("/add/researcher/", status_code=201)
def save_researcher(profile: FullProfile, researcher_uuid: str = None, db: Session = Depends(get_db)):
    # Convert Pydantic model to dict, excluding unset fields
    researcher_data = profile.researcher.model_dump(exclude_unset=True)

    # --- 1. Process Main Researcher Record ---
    # Fallback checking: check URL parameter first, then fallback to payload dictionary
    uuid_to_check = researcher_uuid or researcher_data.get('uuid')

    if uuid_to_check:
        # Secure update using the explicit UUID token validation
        db_researcher = db.query(DBResearcher).filter(DBResearcher.uuid == uuid_to_check).first()

        if db_researcher:
            for key, value in researcher_data.items():
                if key not in ['id', 'uuid', 'created_at']:  # Protect keys from being modified
                    setattr(db_researcher, key, value)

            # Clean up existing related records to prevent duplication
            db.query(DBExperience).filter(DBExperience.researcher_id == db_researcher.id).delete()
            db.query(DBEducation).filter(DBEducation.researcher_id == db_researcher.id).delete()
            db.query(DBPublication).filter(DBPublication.researcher_id == db_researcher.id).delete()
            db.query(DBOptionalSection).filter(DBOptionalSection.researcher_id == db_researcher.id).delete()

            researcher_id = db_researcher.id
            final_uuid = db_researcher.uuid
        else:
            # If a UUID was passed but not found on server, create fresh or raise an exception
            db_researcher = DBResearcher(**researcher_data)
            db.add(db_researcher)
            db.flush()
            researcher_id = db_researcher.id
            final_uuid = db_researcher.uuid
    else:
        # Create a completely new researcher entry
        db_researcher = DBResearcher(**researcher_data)
        db.add(db_researcher)
        db.flush()
        researcher_id = db_researcher.id
        final_uuid = db_researcher.uuid

    # --- 2. Process Related Collections (Stays identical) ---
    for exp in profile.experiences:
        db.add(DBExperience(researcher_id=researcher_id, **exp.model_dump(exclude={'id'})))
    for edu in profile.educations:
        db.add(DBEducation(researcher_id=researcher_id, **edu.model_dump(exclude={'id'})))
    for pub in profile.publications:
        pub_data = pub.model_dump(exclude={'id'})
        title = pub_data.get('title', '')
        year_match = re.search(r'\b(19|20)\d{2}\b', title)
        if year_match and not pub_data.get('year'):
            pub_data['year'] = int(year_match.group(0))
        main_field, subfield = classify_to_main_field(title)
        pub_data['main_field'] = main_field
        pub_data['subfield'] = subfield
        pub_data['research_fields'] = json.dumps([main_field]) if main_field else None
        db.add(DBPublication(researcher_id=researcher_id, **pub_data))
    for opt in profile.optional_sections:
        db.add(DBOptionalSection(researcher_id=researcher_id, **opt.model_dump(exclude={'id'})))

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

    return {"success": True, "researcherUuid": final_uuid}


@router.post("/upload-profile-photo/{researcher_uuid}")
async def upload_profile_photo(researcher_uuid: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Verify researcher identity securely using UUID
    researcher = db.query(DBResearcher).filter(DBResearcher.uuid == researcher_uuid).first()
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")
    Path(PROFILE_PHOTOS_DIR).mkdir(parents=True, exist_ok=True)

    # Generate unique filename using internal sequential ID for disk organization
    file_extension = Path(file.filename).suffix
    file_name = f"researcher_{researcher.uuid}{file_extension}"
    file_location = PROFILE_PHOTOS_DIR / file_name

    # Save binary stream to filesystem
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save relative disk path string to database
    researcher.profile_photo = str(file_name)
    db.commit()

    return {"status": "success", "path": str(file_location)}


@router.post("/upload-dept-logo/{researcher_uuid}")
async def upload_dept_logo(researcher_uuid: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Verify researcher identity securely using UUID
    researcher = db.query(DBResearcher).filter(DBResearcher.uuid == researcher_uuid).first()
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")

    Path(CUSTOM_DEPT_LOGO_DIR).mkdir(parents=True, exist_ok=True)

    # Generate unique filename using internal sequential ID for disk organization
    file_extension = Path(file.filename).suffix
    file_name = f"dept_{researcher.uuid}{file_extension}"
    file_location = CUSTOM_DEPT_LOGO_DIR / file_name

    # Save binary stream to filesystem
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save relative disk path string to database
    researcher.dept_logo = str(file_name)
    db.commit()

    return {"status": "success", "path": str(file_name)}


@router.delete("/researchers/{researcher_uuid}")
def delete_researcher(researcher_uuid: str, db: Session = Depends(get_db)):
    researcher = db.query(DBResearcher).filter(DBResearcher.uuid == researcher_uuid).first()
    if not researcher:
        raise HTTPException(status_code=404, detail="Researcher not found")
    db.delete(researcher)
    db.commit()
    return {"success": True, "message": f"Researcher profile deleted successfully"}


@router.get("/researchers/")
def list_researchers(db: Session = Depends(get_db)):
    # Return secure uuid mapping properties to the listing layouts
    researchers = db.query(DBResearcher.uuid, DBResearcher.full_name).all()
    return [{"id": r.uuid, "name": r.full_name} for r in researchers]


@router.get("/researcher/{researcher_uuid}/photo")
def get_researcher_photo(researcher_uuid: str, db: Session = Depends(get_db)):
    researcher = db.query(DBResearcher).filter(DBResearcher.uuid == researcher_uuid).first()
    if not researcher or not researcher.profile_photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    path = Path(PROFILE_PHOTOS_DIR) / researcher.profile_photo
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(str(path))


@router.get("/researcher/{researcher_uuid}/logo")
def get_department_logo(researcher_uuid: str, db: Session = Depends(get_db)):
    researcher = db.query(DBResearcher).filter(DBResearcher.uuid == researcher_uuid).first()
    if not researcher or not researcher.dept_logo:
        raise HTTPException(status_code=404, detail="Logo not found")

    path = Path(CUSTOM_DEPT_LOGO_DIR) / researcher.dept_logo
    if not path.exists():
        raise HTTPException(status_code=404, detail="File missing on server")

    return FileResponse(str(path))
