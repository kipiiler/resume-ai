from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import JSON, Column, Integer, String
from model.database import Base

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
    grad_year: Optional[int] = None


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
    grad_year = Column(Integer, nullable=True)
