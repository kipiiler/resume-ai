import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Tuple
from services.user import UserService
from services.experience import ExperienceService
from services.project import ProjectService
import config

class ResumeWriter:
    def __init__(self, template_path: str = "template/my_resume.tex"):
        self.template_path = template_path
    
    def _get_user_data(self, user_id: int):
        user_service = UserService()
        user = user_service.get_user(user_id)
        return user
    
    def _write_header(self, user_id: int):
        user_data = self._get_user_data(user_id)

        result = "\n"
        result += "\t\\begin{center}\n"
        result += f"\t\t\\textbf{{\Huge \\scshape {user_data.name}}} \\\\ \\vspace{{1pt}} \n"
        # \small 123-456-7890 $|$ \href{mailto:x@x.com}{\underline{jake@su.edu}} $|$
        result += f"\t\t\\small {self._format_phone_number(user_data.phone)} $|$ \href{{mailto:{user_data.email}}}{{\\underline{{{user_data.email}}}}} $|$ "
        result += f"\\href{{{config.GITHUB_URL}}}{{\\underline{{github.com/{config.GITHUB_SHORT_HANDLE}}}}} $|$ "
        result += f"\\href{{{config.LINKEDIN_URL}}}{{\\underline{{linkedin.com/in/{config.LINKEDIN_SHORT_HANDLE}}}}}"
        if config.PORTFOLIO_URL:
            result += f" $|$ \\href{{{config.PORTFOLIO_URL}}}{{\\underline{{{config.PORTFOLIO_SHORT_HANDLE}}}}}\n"
        else:
            result += "\n"
        result += "\t\\end{center}\n"
        result += "\n"
        return result

    def _write_education(self, user_id: int):
        user_data = self._get_user_data(user_id)
        result = "\n"
        result += "\section{Education}\n"

        result += "\t\\resumeSubHeadingListStart\n"
        result += "\t\t\\resumeSubheading\n"
        if user_data.grad_year:
            if int(user_data.grad_year[-4:]) >= datetime.now().year:
                result += f"\t\t\t{{{user_data.education}}}{{Expected {user_data.grad_year}}}\n"
            else:
                result += f"\t\t\t{{{user_data.education}}}{{Graduated {user_data.grad_year}}}\n"
        else:
            result += f"\t\t\t{{{user_data.education}}}{{}}"
        result += f"\t\t\t{{{user_data.degree} in {user_data.major}}}{{{'GPA : ' + user_data.grade if user_data.grade else ''}}}"
        result += "\t\\resumeSubHeadingListEnd\n"
        result += "\n"
        return result
    
    def _write_skills(self):
        result = "\n"
        result += "\\vspace{-13pt}\\section{Skills}\n"
        result += " \\begin{itemize}[leftmargin=0.15in, label={}]\n"
        result += "    \\footnotesize{\\item{\n"
        result += f"     \\textbf{{Languages}}{{: {', '.join(config.LANGUAGE_LIST)}}} \\\\\n"
        result += f"     \\textbf{{Frameworks and Libraries}}{{: {', '.join(config.TECH_STACK_LIST)}}} \\\\\n"
        result += "     \n"
        result += "    }}\n"
        result += " \\end{itemize}\n"
        result += "\n"
        return result

    
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
    

    def _write_project_with_bullet_points(self, project_id: int, bullet_points: List[str]) -> str:
        result = ""
        project_service = ProjectService()
        project = project_service.get_project(project_id)

        project_name = self._escape_latex(project.project_name)
        tech_stack = self._escape_latex(", ".join(project.tech_stack))
        if project.start_date and project.end_date:
            start_date = datetime.strptime(project.start_date, "%Y-%m").strftime("%b %Y")
            end_date = datetime.strptime(project.end_date, "%Y-%m").strftime("%b %Y")
        else:
            start_date = ""
            end_date = ""

        result += "\n"
        result += "\t\\resumeProjectHeading\n"
        # {\textbf{Gitlytics} $|$ \emph{Python, Flask, React, PostgreSQL, Docker}}{June 2020 -- Present}
        result += f"\t{{\\textbf{{{project_name}}} $|$ \\emph{{{tech_stack}}}}}{{{start_date} {'--' if start_date and end_date else ''} {end_date}}}\n"
        
        result += "\t\\resumeItemListStart\n"
        for bullet_point in bullet_points:
            result += f"\t\t\t\\resumeItem{{{self._escape_latex(bullet_point)}}}\n"
        
        result += "\t\t\\resumeItemListEnd\n"
        result += "\n"

        return result
    
    def _format_phone_number(self, phone_number: str) -> str:
        # format phone number to be 123-456-7890
        return f"{phone_number[:3]}-{phone_number[3:6]}-{phone_number[6:]}"

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
    
    def _write_experience_section(self, exp: List[Tuple[int, List[str]]]):
        result = "\n"
        result += "\section{Experience}\n"
        result += "\t\\resumeSubHeadingListStart\n"
        for exp_id, bullet_points in exp:
            result += self._write_experience_with_bullet_points(exp_id, bullet_points)
        result += "\t\\resumeSubHeadingListEnd\n"
        result += "\n"
        return result
    
    def _write_project_section(self, proj: List[Tuple[int, List[str]]]):
        result = "\n"
        result += "\section{Projects}\n"
        result += "\t\\resumeSubHeadingListStart\n"
        for proj_id, bullet_points in proj:
            result += self._write_project_with_bullet_points(proj_id, bullet_points)
        result += "\t\\resumeSubHeadingListEnd\n"
        result += "\n"
        return result

    def write_resume(self, user_id: int, file_path: str, exp: List[Tuple[int, List[str]]], proj: List[Tuple[int, List[str]]]):
        """
        Write resume to file
        """                 
        # copy and write template to file
        template = self._load_template()
        with open(file_path, "w") as file:
            file.write(template)
            file.write("\n")
            file.write("\\begin{document}")
        
        # write header
        header_str = self._write_header(user_id)
        with open(file_path, "a") as file:
            file.write(header_str)

        # write education
        education_str = self._write_education(user_id)
        with open(file_path, "a") as file:
            file.write(education_str)
        
        # write skills
        skills_str = self._write_skills()
        with open(file_path, "a") as file:
            file.write(skills_str)
        
        # write experience
        exp_str = self._write_experience_section(exp)
        with open(file_path, "a") as file:
            file.write(exp_str)

        # write project
        proj_str = self._write_project_section(proj)
        with open(file_path, "a") as file:
            file.write(proj_str)

        # close file
        with open(file_path, "a") as file:
            file.write("\n")
            file.write("\\end{document}")
        

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

        return result

    def test_write_project_with_bullet_points(self):
        """Test writing project with bullet points from sample data."""
        import json
        
        # Load sample test data
        with open("tests/sample_process_result.json", "r") as f:
            test_data = json.load(f)
            
        # Get first result's bullet points
        sample_result = test_data[0]
        bullet_points = sample_result["bullet_points"]
        
        # Write project with bullet points
        result = self._write_project_with_bullet_points(4, bullet_points)

        return result
    
    def test_write_header(self):
        result = self._write_header(1)
        return result
    
    def test_write_education(self):
        result = self._write_education(1)
        return result

    def test_write_skills(self):
        result = self._write_skills()
        return result

if __name__ == "__main__":
    resume_writer = ResumeWriter()
    exp_result = resume_writer.test_write_experience_with_bullet_points()
    proj_result = resume_writer.test_write_project_with_bullet_points()
    header_result = resume_writer.test_write_header()
    education_result = resume_writer.test_write_education()
    skills_result = resume_writer.test_write_skills()
    print(exp_result)
    print(proj_result)
    print(header_result)
    print(education_result)
    print(skills_result)