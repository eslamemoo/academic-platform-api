from pydantic import BaseModel
from typing import List, Optional

class ExperienceBase(BaseModel):
    title: str
    company: str
    period: str
    description: str

class EducationBase(BaseModel):
    degree: str
    institution: str
    details: str

class PublicationBase(BaseModel):
    title: str
    authors: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    source: Optional[str] = "manual"
    research_fields: Optional[List[str]] = None      # kept for compatibility
    main_field: Optional[str] = None                 # new
    subfield: Optional[str] = None                   # new
    citation_count: Optional[int] = 0

class OptionalSectionBase(BaseModel):
    section_type: str
    content: str

class ResearcherBase(BaseModel):
    id: Optional[int] = None
    full_name: Optional[str] = ""
    job_title: Optional[str] = ""
    profile_desc: Optional[str] = ""
    contact_address: Optional[str] = ""
    contact_email: Optional[str] = ""
    contact_phone: Optional[str] = ""
    google_scholar_url: Optional[str] = ""
    orcid_id: Optional[str] = ""
    scopus_id: Optional[str] = ""
    cu_scholar_url: Optional[str] = ""
    research_interests: Optional[str] = ""
    skills: Optional[str] = ""
    dept_name: Optional[str] = ""
    faculty_name: Optional[str] = ""
    profile_photo: Optional[str] = None
    dept_logo: Optional[str] = None

class FullProfile(BaseModel):
    researcher: ResearcherBase
    experiences: List[ExperienceBase]
    educations: List[EducationBase]
    publications: List[PublicationBase]
    optional_sections: List[OptionalSectionBase]
