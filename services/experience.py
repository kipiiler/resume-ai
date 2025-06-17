from model.schema import Experience, ExperienceDB
from model.database import Database
from typing import List, Optional

class ExperienceService:
    def __init__(self):
        self.db = Database.get_instance()

    def create_experience(self, experience: Experience) -> ExperienceDB:
        with self.db as session:
            db_experience = ExperienceDB(
                user_id=experience.user_id,
                company_name=experience.company_name,
                role_title=experience.role_title,
                company_location=experience.company_location,
                start_date=experience.start_date,
                end_date=experience.end_date,
                long_description=experience.long_description,
                short_description=experience.short_description,
                tech_stack=experience.tech_stack
            )
            session.add(db_experience)
            session.commit()
            session.refresh(db_experience)
            return db_experience

    def get_experience(self, experience_id: int) -> Optional[ExperienceDB]:
        with self.db as session:
            return session.query(ExperienceDB).filter(ExperienceDB.id == experience_id).first()

    def get_user_experiences(self, user_id: int) -> List[ExperienceDB]:
        with self.db as session:
            return session.query(ExperienceDB).filter(ExperienceDB.user_id == user_id).all()

    def update_experience(self, experience_id: int, experience_data: Experience) -> Optional[ExperienceDB]:
        with self.db as session:
            db_experience = session.query(ExperienceDB).filter(ExperienceDB.id == experience_id).first()
            if db_experience:
                for key, value in experience_data.dict(exclude_unset=True).items():
                    setattr(db_experience, key, value)
                session.commit()
                session.refresh(db_experience)
            return db_experience

    def delete_experience(self, experience_id: int) -> bool:
        with self.db as session:
            db_experience = session.query(ExperienceDB).filter(ExperienceDB.id == experience_id).first()
            if db_experience:
                session.delete(db_experience)
                session.commit()
                return True
            return False 