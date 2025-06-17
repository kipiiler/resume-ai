from typing import List
from services.user import UserService
from services.experience import ExperienceService

class ResumeWriter:
    def __init__(self, template_path: str = "template/my_resume.tex"):
        self.template_path = template_path
    
    def _get_user_data(self, user_id: int):
        user_service = UserService()
        user = user_service.get_user(user_id)
        return user
    
    def _write_experience_with_bullet_points(self, experience_id: int, bullet_points: List[str]) -> str:
        result = ""
        experience_service = ExperienceService()
        experience = experience_service.get_experience(experience_id)

        result += "\n"
        
        
        for bullet_point in bullet_points:
            result += f"• {bullet_point}\n"
        
        result += "\n"
        
        return result

    def write_resume(self, user_id: int):
        pass

    def _load_template(self):
        with open(self.template_path, "r") as file:
            return file.read()
        
        