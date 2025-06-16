import json
from typing import Dict, Any, List
from agents.base_agents import BaseAgent
from job_scraper import extract_job_info

class JobAnalysisAgent(BaseAgent):
    """Base agent class for agents that need job posting analysis capabilities."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite", temperature: float = 0.7):
        super().__init__(model_name, temperature)
    
    def _extract_job_information(self, job_url: str) -> Dict[str, Any]:
        """Extract job information from a job posting URL."""
        try:
            return extract_job_info(job_url)
        except Exception as e:
            print(f"Error extracting job info: {e}")
            # Return early exit structure that matches extract_job_info behavior
            return {"error": f"Failed to extract job information: {str(e)}"}
    
    def _extract_technical_skills(self, job_info: Dict[str, Any]) -> List[str]:
        """Extract technical skills from job information using LLM."""
        if job_info.get("error"):
            return []
        
        # Create prompt for technical skills extraction
        prompt = self._create_prompt_template(
            system_message="""You are a technical recruiter expert at identifying technical skills from job postings.

Your task is to extract ONLY the technical skills, tools, technologies, and programming languages mentioned in the job posting.

Focus on:
- Programming languages (Python, JavaScript, Java, etc.)
- Frameworks and libraries (React, Django, TensorFlow, etc.)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- Cloud platforms (AWS, Azure, GCP, etc.)
- Development tools (Docker, Kubernetes, Git, etc.)
- Technical methodologies (Agile, DevOps, CI/CD, etc.)

Do NOT include:
- Soft skills (communication, leadership, etc.)
- General business skills
- Industry knowledge
- Educational requirements

Return ONLY a JSON array of technical skills as strings:
["skill1", "skill2", "skill3"]

If no technical skills are found, return an empty array: []""",
            human_message="""Extract technical skills from this job posting:

Company: {company_name}
Position: {job_title}
Description: {description}
Qualifications: {qualifications}"""
        )
        
        # Format job information for the prompt
        qualifications_text = "\n".join(job_info.get("qualifications", []))
        
        formatted_prompt = prompt.format(
            company_name=job_info.get("company_name", "Unknown"),
            job_title=job_info.get("job_title", "Unknown"),
            description=job_info.get("description", "No description available"),
            qualifications=qualifications_text
        )
        
        try:
            response_text = self._safe_llm_invoke(formatted_prompt, "[]")
            response_text = self._clean_json_response(response_text)
            skills_list = json.loads(response_text)
            
            if isinstance(skills_list, list):
                return [skill.strip() for skill in skills_list if isinstance(skill, str) and skill.strip()]
            else:
                print("LLM response is not a list, falling back to empty list")
                return []
                
        except Exception as e:
            print(f"Error extracting technical skills with LLM: {e}")
            
            # Fallback: Simple keyword extraction
            fallback_skills = []
            text_to_search = f"{job_info.get('description', '')} {qualifications_text}".lower()
            
            # Common technical keywords to look for
            tech_keywords = [
                "python", "javascript", "java", "react", "node.js", "sql", "postgresql", 
                "mongodb", "aws", "docker", "kubernetes", "git", "linux", "html", "css",
                "typescript", "angular", "vue", "django", "flask", "spring", "tensorflow",
                "pytorch", "machine learning", "ai", "data science", "devops", "ci/cd"
            ]
            
            for keyword in tech_keywords:
                if keyword in text_to_search:
                    fallback_skills.append(keyword.title())
            
            return fallback_skills 