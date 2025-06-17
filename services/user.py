from model.schema import User, UserDB
from model.database import Database
from typing import List, Optional

class UserService:
    def __init__(self):
        self.db = Database.get_instance()

    def create_user(self, user: User) -> UserDB:
        with self.db as session:
            db_user = UserDB(
                name=user.name,
                email=user.email,
                phone=user.phone,
                personality=user.personality,
                education=user.education,
                degree=user.degree,
                major=user.major,
                grade=user.grade,
                location=user.location,
                grad_year=user.grad_year
            )
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user

    def get_user(self, user_id: int) -> Optional[UserDB]:
        with self.db as session:
            return session.query(UserDB).filter(UserDB.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[UserDB]:
        with self.db as session:
            return session.query(UserDB).filter(UserDB.email == email).first()

    def get_all_users(self) -> List[UserDB]:
        with self.db as session:
            return session.query(UserDB).all()

    def update_user(self, user_id: int, user_data: User) -> Optional[UserDB]:
        with self.db as session:
            db_user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if db_user:
                for key, value in user_data.dict(exclude_unset=True).items():
                    setattr(db_user, key, value)
                session.commit()
                session.refresh(db_user)
            return db_user

    def delete_user(self, user_id: int) -> bool:
        with self.db as session:
            db_user = session.query(UserDB).filter(UserDB.id == user_id).first()
            if db_user:
                session.delete(db_user)
                session.commit()
                return True
            return False
