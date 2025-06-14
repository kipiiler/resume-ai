from model.schema import Project, ProjectDB
from model.database import Database
from typing import List, Optional

class ProjectService:
    def __init__(self):
        self.db = Database.get_instance()

    def create_project(self, project: Project) -> ProjectDB:
        with self.db as session:
            db_project = ProjectDB(
                user_id=project.user_id,
                project_name=project.project_name,
                start_date=project.start_date,
                end_date=project.end_date,
                long_description=project.long_description,
                short_description=project.short_description,
                tech_stack=project.tech_stack,
                team_size=project.team_size
            )
            session.add(db_project)
            session.commit()
            session.refresh(db_project)
            return db_project

    def get_project(self, project_id: int) -> Optional[ProjectDB]:
        with self.db as session:
            return session.query(ProjectDB).filter(ProjectDB.id == project_id).first()

    def get_user_projects(self, user_id: int) -> List[ProjectDB]:
        with self.db as session:
            return session.query(ProjectDB).filter(ProjectDB.user_id == user_id).all()

    def update_project(self, project_id: int, project_data: Project) -> Optional[ProjectDB]:
        with self.db as session:
            db_project = session.query(ProjectDB).filter(ProjectDB.id == project_id).first()
            if db_project:
                for key, value in project_data.dict(exclude_unset=True).items():
                    setattr(db_project, key, value)
                session.commit()
                session.refresh(db_project)
            return db_project

    def delete_project(self, project_id: int) -> bool:
        with self.db as session:
            db_project = session.query(ProjectDB).filter(ProjectDB.id == project_id).first()
            if db_project:
                session.delete(db_project)
                session.commit()
                return True
            return False 