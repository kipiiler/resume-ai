from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import JSON, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from model.database import Base

class Experience(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    company_name: str
    company_location: str
    start_date: str
    end_date: str
    long_description: str
    short_description: str
    tech_stack: Optional[List[str]] = None

class Project(BaseModel):
    id: Optional[int] = None
    user_id: Optional[int] = None
    project_name: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    long_description: str
    short_description: str
    tech_stack: Optional[List[str]] = None
    team_size: Optional[int] = 1

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str
    phone: str
    personality: Optional[List[str]] = None
    education: str
    major: str
    grade: Optional[str] = None
    location: str
    grad_year: Optional[str] = None
    experiences: Optional[List[Experience]] = None
    projects: Optional[List[Project]] = None

class Company(BaseModel):
    name: str
    mission: str
    location: str
    website: str
    industry: str
    description: str

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    personality = Column(JSON)
    education = Column(String)
    major = Column(String)
    grade = Column(String, nullable=True)
    location = Column(String)
    grad_year = Column(String, nullable=True)
    experiences = relationship("ExperienceDB", back_populates="rel_user")
    projects = relationship("ProjectDB", back_populates="rel_user")

class ExperienceDB(Base):
    __tablename__ = "experiences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    company_name = Column(String)
    company_location = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    long_description = Column(String)
    short_description = Column(String)
    tech_stack = Column(JSON)
    rel_user = relationship("UserDB", back_populates="experiences")

class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    project_name = Column(String)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    long_description = Column(String)
    short_description = Column(String)
    tech_stack = Column(JSON)
    team_size = Column(Integer, nullable=True)
    rel_user = relationship("UserDB", back_populates="projects")


class CompanyDB(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    mission = Column(String)
    location = Column(String)
    website = Column(String)
    industry = Column(String)
    description = Column(String)

class JobPosting(BaseModel):
    job_posting_url: str
    company_name: str
    job_title: str
    job_location: str
    job_type: str
    job_description: str
    job_qualifications: List[str]
    job_technical_skills: List[str]

class JobPostingDB(Base):
    __tablename__ = "job_postings"

    id=Column(Integer, primary_key=True, index=True)
    job_posting_url=Column(String)
    company_name=Column(String)
    job_title=Column(String)
    job_location=Column(String)
    job_type=Column(String)
    job_description=Column(String)
    job_qualifications=Column(JSON)
    job_technical_skills=Column(JSON)
