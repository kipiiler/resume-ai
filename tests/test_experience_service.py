# update sys path to include the project root
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.schema import User, Experience
from services.user import UserService
from services.experience import ExperienceService
from model.database import Database, Base, engine

def init_test_db():
    """Initialize the test database"""
    Base.metadata.create_all(bind=engine)

def cleanup_test_db():
    """Clean up the test database"""
    Base.metadata.drop_all(bind=engine)

def test_experience_service():
    # Initialize database
    init_test_db()
    
    # Create service instances
    user_service = UserService()
    experience_service = ExperienceService()
    
    try:
        # First create a user to associate experiences with
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

        # Test 1: Create a new experience
        print("\nTest 1: Creating a new experience...")
        new_experience = Experience(
            user_id=created_user.id,
            company_name="Tech Corp",
            company_location="San Francisco",
            start_date="2020-01",
            end_date="2023-12",
            long_description="Worked on various projects including AI and cloud infrastructure",
            short_description="Senior Software Engineer",
            tech_stack=["Python", "AWS", "Docker", "Kubernetes"]
        )
        created_experience = experience_service.create_experience(new_experience)
        print(f"Created experience at {created_experience.company_name} with ID: {created_experience.id}")
        
        # Test 2: Get experience by ID
        print("\nTest 2: Getting experience by ID...")
        retrieved_experience = experience_service.get_experience(created_experience.id)
        print(f"Retrieved experience: {retrieved_experience.company_name}")
        
        # Test 3: Get user experiences
        print("\nTest 3: Getting user experiences...")
        user_experiences = experience_service.get_user_experiences(created_user.id)
        print(f"User has {len(user_experiences)} experiences")
        
        # Test 4: Update experience
        print("\nTest 4: Updating experience...")
        updated_data = Experience(
            user_id=created_user.id,
            company_name="Tech Corp",
            company_location="San Francisco",
            start_date="2020-01",
            end_date="2023-12",
            long_description="Led multiple AI and cloud infrastructure projects",
            short_description="Lead Software Engineer",  # Updated title
            tech_stack=["Python", "AWS", "Docker", "Kubernetes", "TensorFlow"]  # Added tech
        )
        updated_experience = experience_service.update_experience(created_experience.id, updated_data)
        print(f"Updated experience title: {updated_experience.short_description}")
        print(f"Updated tech stack: {updated_experience.tech_stack}")
        
        # Test 5: Delete experience
        print("\nTest 5: Deleting experience...")
        delete_result = experience_service.delete_experience(created_experience.id)
        print(f"Experience deletion {'successful' if delete_result else 'failed'}")
        
        # Verify deletion
        deleted_experience = experience_service.get_experience(created_experience.id)
        print(f"Experience exists after deletion: {deleted_experience is not None}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up the test database
        cleanup_test_db()

if __name__ == "__main__":
    print("Starting ExperienceService tests...")
    test_experience_service()
    print("\nAll tests completed!") 