# update sys path to include the project root
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from model.schema import User, Project
from service.user import UserService
from service.project import ProjectService
from model.database import Database, Base, engine


def init_test_db():
    """Initialize the test database"""
    Base.metadata.create_all(bind=engine)

def cleanup_test_db():
    """Clean up the test database"""
    Base.metadata.drop_all(bind=engine)

def test_project_service():
    # Initialize database
    init_test_db()
    
    # Create service instances
    user_service = UserService()
    project_service = ProjectService()
    
    try:
        # First create a user to associate projects with
        print("\nCreating test user...")
        test_user = User(
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            education="Bachelor's",
            major="Computer Science",
            location="New York",
            personality=["creative", "analytical"],
            grade="A",
            grad_year=2024
        )
        created_user = user_service.create_user(test_user)
        print(f"Created test user with ID: {created_user.id}")

        # Test 1: Create a new project
        print("\nTest 1: Creating a new project...")
        new_project = Project(
            user_id=created_user.id,
            project_name="AI Resume Builder",
            start_date="2023-01",
            end_date="2023-12",
            long_description="Developed an AI-powered resume builder that helps users create professional resumes",
            short_description="Lead Developer",
            tech_stack=["Python", "FastAPI", "React", "OpenAI"],
            team_size=5
        )
        created_project = project_service.create_project(new_project)
        print(f"Created project: {created_project.project_name} with ID: {created_project.id}")
        
        # Test 2: Get project by ID
        print("\nTest 2: Getting project by ID...")
        retrieved_project = project_service.get_project(created_project.id)
        print(f"Retrieved project: {retrieved_project.project_name}")
        
        # Test 3: Get user projects
        print("\nTest 3: Getting user projects...")
        user_projects = project_service.get_user_projects(created_user.id)
        print(f"User has {len(user_projects)} projects")
        
        # Test 4: Update project
        print("\nTest 4: Updating project...")
        updated_data = Project(
            user_id=created_user.id,
            project_name="AI Resume Builder",
            start_date="2023-01",
            end_date="2023-12",
            long_description="Led development of an AI-powered resume builder with advanced features",
            short_description="Technical Lead",  # Updated role
            tech_stack=["Python", "FastAPI", "React", "OpenAI", "Docker"],  # Added tech
            team_size=8  # Updated team size
        )
        updated_project = project_service.update_project(created_project.id, updated_data)
        print(f"Updated project role: {updated_project.short_description}")
        print(f"Updated team size: {updated_project.team_size}")
        print(f"Updated tech stack: {updated_project.tech_stack}")
        
        # Test 5: Delete project
        print("\nTest 5: Deleting project...")
        delete_result = project_service.delete_project(created_project.id)
        print(f"Project deletion {'successful' if delete_result else 'failed'}")
        
        # Verify deletion
        deleted_project = project_service.get_project(created_project.id)
        print(f"Project exists after deletion: {deleted_project is not None}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up the test database
        cleanup_test_db()

if __name__ == "__main__":
    print("Starting ProjectService tests...")
    test_project_service()
    print("\nAll tests completed!") 