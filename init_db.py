from sqlalchemy import create_engine
from model.schema import Base
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///resume.db"

def init_db():
    """Initialize the database by creating all tables."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()
