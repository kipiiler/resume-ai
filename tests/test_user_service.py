# update sys path to include the project root
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.schema import User
from services.user import UserService
from model.database import Database, Base, engine

def init_test_db():
    """Initialize the test database"""
    Base.metadata.create_all(bind=engine)

def cleanup_test_db():
    """Clean up the test database"""
    Base.metadata.drop_all(bind=engine)

def test_user_service():
    # Initialize database
    init_test_db()
    
    # Create user service instance
    user_service = UserService()
    
    try:
        # Test 1: Create a new user
        print("\nTest 1: Creating a new user...")
        new_user = User(
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
        created_user = user_service.create_user(new_user)
        print(f"Created user: {created_user.name} with ID: {created_user.id}")
        
        # Test 2: Get user by ID
        print("\nTest 2: Getting user by ID...")
        retrieved_user = user_service.get_user(created_user.id)
        print(f"Retrieved user: {retrieved_user.name}")
        
        # Test 3: Get user by email
        print("\nTest 3: Getting user by email...")
        user_by_email = user_service.get_user_by_email("john@example.com")
        print(f"Retrieved user by email: {user_by_email.name}")
        
        # Test 4: Update user
        print("\nTest 4: Updating user...")
        updated_data = User(
            name="John Doe",
            email="john@example.com",
            phone="1234567890",
            education="Bachelor's",
            major="Computer Science",
            location="Boston",  # Updated location
            personality=["creative", "analytical", "detail-oriented"],  # Updated personality
            grade="A+",  # Updated grade
            grad_year=2024
        )
        updated_user = user_service.update_user(created_user.id, updated_data)
        print(f"Updated user location: {updated_user.location}")
        print(f"Updated user personality: {updated_user.personality}")
        print(f"Updated user grade: {updated_user.grade}")
        
        # Test 5: Get all users
        print("\nTest 5: Getting all users...")
        all_users = user_service.get_all_users()
        print(f"Total users in database: {len(all_users)}")
        
        # Test 6: Delete user
        print("\nTest 6: Deleting user...")
        delete_result = user_service.delete_user(created_user.id)
        print(f"User deletion {'successful' if delete_result else 'failed'}")
        
        # Verify deletion
        deleted_user = user_service.get_user(created_user.id)
        print(f"User exists after deletion: {deleted_user is not None}")
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        # Clean up the test database
        cleanup_test_db()

if __name__ == "__main__":
    print("Starting UserService tests...")
    test_user_service()
    print("\nAll tests completed!") 