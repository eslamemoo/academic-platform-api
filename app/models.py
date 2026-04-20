from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Researcher(Base):
    __tablename__ = "researchers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    job_title = Column(String)
    profile_desc = Column(Text)
    contact_address = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    google_scholar_url = Column(String)
    orcid_id = Column(String)
    scopus_id = Column(String)
    cu_scholar_url = Column(String)
    research_interests = Column(Text)
    skills = Column(Text)
    dept_name = Column(String)
    faculty_name = Column(String)
    profile_photo = Column(Text)  # We'll store the photo as a base64 string
    dept_logo = Column(Text)      # Store the logo as a base64 string
    created_at = Column(DateTime, server_default=func.now())

    # These define relationships to other tables (not columns in this table)
    experiences = relationship("Experience", back_populates="researcher", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="researcher", cascade="all, delete-orphan")
    publications = relationship("Publication", back_populates="researcher", cascade="all, delete-orphan")
    optional_sections = relationship("OptionalSection", back_populates="researcher", cascade="all, delete-orphan")

class Experience(Base):
    __tablename__ = "experiences"
    id = Column(Integer, primary_key=True, index=True)
    researcher_id = Column(Integer, ForeignKey("researchers.id", ondelete="CASCADE"))
    title = Column(String)
    company = Column(String)
    period = Column(String)
    description = Column(Text)
    researcher = relationship("Researcher", back_populates="experiences")

class Education(Base):
    __tablename__ = "educations"
    id = Column(Integer, primary_key=True, index=True)
    researcher_id = Column(Integer, ForeignKey("researchers.id", ondelete="CASCADE"))
    degree = Column(String)
    institution = Column(String)
    details = Column(Text)  # This stores the 'year' and other details
    researcher = relationship("Researcher", back_populates="educations")

class Publication(Base):
    __tablename__ = "publications"
    id = Column(Integer, primary_key=True, index=True)
    researcher_id = Column(Integer, ForeignKey("researchers.id", ondelete="CASCADE"))
    title = Column(String)
    authors = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    journal = Column(String, nullable=True)
    doi = Column(String, nullable=True)
    source = Column(String, nullable=True)
    research_fields = Column(String, nullable=True)   # JSON string (legacy)
    main_field = Column(String, nullable=True)        # NEW
    subfield = Column(String, nullable=True)          # NEW
    citation_count = Column(Integer, nullable=True)
    imported_at = Column(DateTime, server_default=func.now())
    researcher = relationship("Researcher", back_populates="publications")
    
class OptionalSection(Base):
    __tablename__ = "optional_sections"
    id = Column(Integer, primary_key=True, index=True)
    researcher_id = Column(Integer, ForeignKey("researchers.id", ondelete="CASCADE"))
    section_type = Column(String)
    content = Column(Text)
    researcher = relationship("Researcher", back_populates="optional_sections")
