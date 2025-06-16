from model.schema import Company, CompanyDB
from model.database import Database
from typing import List, Optional

class CompanyService:
    def __init__(self):
        self.db = Database.get_instance()

    def create_company(self, company: Company) -> CompanyDB:
        with self.db as session:
            db_company = CompanyDB(
                name=company.name,
                mission=company.mission,
                location=company.location,
                website=company.website,
                industry=company.industry,
                description=company.description
            )
            session.add(db_company)
            session.commit()
            session.refresh(db_company)
            return db_company

    def get_company(self, company_id: int) -> Optional[CompanyDB]:
        with self.db as session:
            return session.query(CompanyDB).filter(CompanyDB.id == company_id).first()

    def get_company_by_name(self, name: str) -> Optional[CompanyDB]:
        with self.db as session:
            return session.query(CompanyDB).filter(CompanyDB.name == name).first()

    def get_all_companies(self) -> List[CompanyDB]:
        with self.db as session:
            return session.query(CompanyDB).all()

    def update_company(self, company_id: int, company_data: Company) -> Optional[CompanyDB]:
        with self.db as session:
            db_company = session.query(CompanyDB).filter(CompanyDB.id == company_id).first()
            if db_company:
                for key, value in company_data.dict(exclude_unset=True).items():
                    setattr(db_company, key, value)
                session.commit()
                session.refresh(db_company)
            return db_company

    def delete_company(self, company_id: int) -> bool:
        with self.db as session:
            db_company = session.query(CompanyDB).filter(CompanyDB.id == company_id).first()
            if db_company:
                session.delete(db_company)
                session.commit()
                return True
            return False 