import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
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
    
    def _escape_latex(self, text: str) -> str:
        # escape latex special characters
        # escape "%"
        text = text.replace("%", "\%")
        # escape "_"
        text = text.replace("_", "\_")
        # escape "{"
        text = text.replace("{", "\{")
        # escape "}"
        text = text.replace("}", "\}")
        # escape "|"
        text = text.replace("|", "\|")
        # escape "&"
        text = text.replace("&", "\&")
        # escape "#"
        text = text.replace("#", "\#")
        # escape "$"
        text = text.replace("$", "\$")
        return text
    
    def _write_experience_with_bullet_points(self, experience_id: int, bullet_points: List[str]) -> str:
        result = ""
        experience_service = ExperienceService()
        experience = experience_service.get_experience(experience_id)

        result += "\n"
        title = self._escape_latex(experience.role_title)
        start_date = datetime.strptime(experience.start_date, "%Y-%m").strftime("%b %Y")
        end_date = datetime.strptime(experience.end_date, "%Y-%m").strftime("%b %Y")
        company_name = self._escape_latex(experience.company_name)
        company_location = self._escape_latex(experience.company_location)

        result += "\t\\resumeSubheading\n"
        result += f"\t\t{{{title}}}{{{start_date} -- {end_date}}}\n"
        result += f"\t\t{{{company_name}}}{{{company_location}}}\n"
        result += "\t\t\\resumeItemListStart\n"

        for bullet_point in bullet_points:
            result += f"\t\t\t\\resumeItem{{{self._escape_latex(bullet_point)}}}\n"
        
        result += "\t\t\\resumeItemListEnd\n"
        result += "\n"
        
        return result

    def write_resume(self, user_id: int):
        pass

    def _load_template(self):
        with open(self.template_path, "r") as file:
            return file.read()
        

    def test_write_experience_with_bullet_points(self):
        """Test writing experience with bullet points from sample data."""
        import json
        
        # Load sample test data
        with open("tests/sample_process_result.json", "r") as f:
            test_data = json.load(f)
            
        # Get first result's bullet points
        sample_result = test_data[0]
        bullet_points = sample_result["bullet_points"]
        
        # Write experience with bullet points
        result = self._write_experience_with_bullet_points(4, bullet_points)
        
        # Print result for verification
        print("\nGenerated LaTeX output:")
        print(result)


if __name__ == "__main__":
    resume_writer = ResumeWriter()
    resume_writer.test_write_experience_with_bullet_points()