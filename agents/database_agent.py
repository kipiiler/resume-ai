from typing import Any
from agents.base_agents import BaseAgent
from services.experience import ExperienceService
from services.user import UserService

class DatabaseAgent(BaseAgent):
    """Base agent class for agents that need database access."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite", temperature: float = 0.7):
        super().__init__(model_name, temperature)
        self._experience_service = None
        self._user_service = None
    
    def _get_experience_service(self) -> ExperienceService:
        """Get or create ExperienceService instance."""
        if self._experience_service is None:
            self._experience_service = ExperienceService()
        return self._experience_service
    
    def _get_user_service(self) -> UserService:
        """Get or create UserService instance."""
        if self._user_service is None:
            self._user_service = UserService()
        return self._user_service
    
    def get_user_experiences(self, user_id: int) -> list:
        """Get all experiences for a user."""
        try:
            experience_service = self._get_experience_service()
            return experience_service.get_user_experiences(user_id)
        except Exception as e:
            print(f"Error getting user experiences: {e}")
            return []
    
    def get_experience(self, experience_id: int) -> Any:
        """Get a specific experience by ID."""
        try:
            experience_service = self._get_experience_service()
            return experience_service.get_experience(experience_id)
        except Exception as e:
            print(f"Error getting experience: {e}")
            return None 