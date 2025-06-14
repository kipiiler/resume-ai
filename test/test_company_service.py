# update sys path to include the project root
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.schema import Company
from service.company import CompanyService
from model.database import Base, engine

def init_test_db():
    """Initialize the test database"""
    Base.metadata.create_all(bind=engine)

def cleanup_test_db():
    """Clean up the test database"""
    Base.metadata.drop_all(bind=engine)

def test_company_service():
    # Initialize database
    init_test_db()
    
    # Create service instance
    company_service = CompanyService()
    
    try:
        # Test 1: Create a new company
        print("\nTest 1: Creating a new company...")
        new_company = Company(
            name="Tech Innovations Inc",
            mission="To revolutionize technology through innovation",
            location="Silicon Valley",
            website="https://techinnovations.com",
            industry="Technology",
            description="A leading technology company focused on AI and cloud solutions"
        )
        created_company = company_service.create_company(new_company)
        print(f"Created company: {created_company.name} with ID: {created_company.id}")
        
        # Test 2: Get company by ID
        print("\nTest 2: Getting company by ID...")
        retrieved_company = company_service.get_company(created_company.id)
        print(f"Retrieved company: {retrieved_company.name}")
        
        # Test 3: Get company by name
        print("\nTest 3: Getting company by name...")
        company_by_name = company_service.get_company_by_name("Tech Innovations Inc")
        print(f"Retrieved company by name: {company_by_name.name}")
        
        # Test 4: Get all companies
        print("\nTest 4: Getting all companies...")
        all_companies = company_service.get_all_companies()
        print(f"Total companies in database: {len(all_companies)}")
        
        # Test 5: Update company
        print("\nTest 5: Updating company...")
        updated_data = Company(
            name="Tech Innovations Inc",
            mission="To revolutionize technology through AI and cloud innovation",
            location="Silicon Valley",
            website="https://techinnovations.com",
            industry="Artificial Intelligence & Cloud Computing",
            description="A leading technology company specializing in AI and cloud solutions"
        )
        updated_company = company_service.update_company(created_company.id, updated_data)
        print(f"Updated company mission: {updated_company.mission}")
        print(f"Updated company industry: {updated_company.industry}")
        
        # Test 6: Delete company
        print("\nTest 6: Deleting company...")
        delete_result = company_service.delete_company(created_company.id)
        print(f"Company deletion {'successful' if delete_result else 'failed'}")
        
        # Verify deletion
        deleted_company = company_service.get_company(created_company.id)
        print(f"Company exists after deletion: {deleted_company is not None}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up the test database
        cleanup_test_db()

if __name__ == "__main__":
    print("Starting CompanyService tests...")
    test_company_service()
    print("\nAll tests completed!") 