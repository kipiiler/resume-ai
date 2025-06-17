from model.schema import JobPosting, JobPostingDB
from model.database import Database
from typing import List, Optional

class JobPostingService:
    def __init__(self):
        self.db = Database.get_instance()

    def create_job_posting(self, job_posting: JobPosting) -> JobPostingDB:
        with self.db as session:
            db_job_posting = JobPostingDB(
                job_posting_url=job_posting.job_posting_url,
                company_name=job_posting.company_name,
                job_title=job_posting.job_title,
                job_location=job_posting.job_location,
                job_type=job_posting.job_type,
                job_description=job_posting.job_description,
                job_qualifications=job_posting.job_qualifications,
                job_technical_skills=job_posting.job_technical_skills
            )
            session.add(db_job_posting)
            session.commit()
            session.refresh(db_job_posting)
            return db_job_posting
        
    def get_job_posting(self, job_posting_id: int) -> Optional[JobPostingDB]:
        with self.db as session:
            return session.query(JobPostingDB).filter(JobPostingDB.id == job_posting_id).first()
        
    def get_all_job_postings(self) -> List[JobPostingDB]:
        with self.db as session:
            return session.query(JobPostingDB).all()
        
    def get_job_posting_by_url(self, job_posting_url: str) -> Optional[JobPostingDB]:
        with self.db as session:
            return session.query(JobPostingDB).filter(JobPostingDB.job_posting_url == job_posting_url).first()