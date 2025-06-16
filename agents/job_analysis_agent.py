import json
from typing import Dict, Any, List, TypedDict, Annotated, Sequence, Callable
import operator
from langchain_core.messages import HumanMessage, AIMessage

from agents.base_agents import BaseAgent, BaseAgentState
from job_scraper import extract_job_info, JobInfo

class JobAnalysisState(BaseAgentState):
    """State for the Job Analysis Agent."""
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    job_posting_url: str
    job_info: JobInfo
    job_technical_skills: List[str]

class JobAnalysisAgent(BaseAgent):
    """Agent for analyzing job postings and extracting structured job information."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite", temperature: float = 0.7):
        super().__init__(model_name, temperature)
    
    def get_state_class(self) -> type:
        """Return the state class for this agent."""
        return JobAnalysisState
    
    def create_nodes(self) -> Dict[str, Callable]:
        """Create all nodes for the job analysis agent."""
        return {
            "extract_job_info": self._create_job_extraction_node(),
            "extract_technical_skills": self._create_technical_skills_extraction_node()
        }
    
    def define_edges(self) -> List[tuple]:
        """Define the edges between nodes."""
        return [
            ("extract_job_info", "extract_technical_skills")
        ]
    
    def get_entry_point(self) -> str:
        """Return the entry point node name."""
        return "extract_job_info"
    
    def _create_job_extraction_node(self):
        """Create node to extract job information from URL."""
        def job_extraction(state: JobAnalysisState) -> JobAnalysisState:
            try:
                job_url = state["job_posting_url"]
                job_info_dict = self._extract_job_information(job_url)
                
                if job_info_dict.get("error"):
                    return {"error": job_info_dict["error"]}
                
                # Convert dict to JobInfo object
                job_info = JobInfo(**job_info_dict)
                return {"job_info": job_info}
            except Exception as e:
                return {"error": f"Failed to extract job information: {str(e)}"}
        return job_extraction
    
    def _create_technical_skills_extraction_node(self):
        """Create node to extract technical skills from job posting."""
        def extract_technical_skills(state: JobAnalysisState) -> JobAnalysisState:
            if state.get("error"):
                return state  # Pass through error state
            
            job_info = state["job_info"]
            try:
                # Convert JobInfo to dict for the skills extraction method
                job_info_dict = job_info.dict()
                skills = self._extract_technical_skills(job_info_dict)
                return {"job_technical_skills": skills}
            except Exception as e:
                print(f"Error extracting technical skills: {e}")
                return {"job_technical_skills": []}
        
        return extract_technical_skills
    
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
    
    def analyze_job(self, job_posting_url: str) -> Dict[str, Any]:
        """Main method to analyze a job posting and extract structured information."""
        initial_state = {
            "messages": [],
            "job_posting_url": job_posting_url,
            "job_info": None,
            "job_technical_skills": [],
            "error": ""
        }
        
        result = self.run(initial_state)
        return result
    
    def get_job_analysis_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a summary of the job analysis results."""
        if result.get("error"):
            return {"error": result["error"]}
        
        job_info = result.get("job_info")
        if not job_info:
            return {"error": "No job information found"}
        
        # Convert JobInfo to dict if it's a JobInfo object
        if hasattr(job_info, 'dict'):
            job_info_dict = job_info.dict()
        else:
            job_info_dict = job_info
        
        summary = {
            "company_name": job_info_dict.get("company_name", "Unknown"),
            "job_title": job_info_dict.get("job_title", "Unknown"),
            "location": job_info_dict.get("location", "Unknown"),
            "job_type": job_info_dict.get("job_type", "Unknown"),
            "technical_skills_extracted": result.get("job_technical_skills", []),
            "total_qualifications": len(job_info_dict.get("qualifications", [])),
            "job_info_object": result.get("job_info")  # Return the JobInfo object for use by other agents
        }
        
        return summary


# Legacy base class for backward compatibility
class JobAnalysisAgentBase(BaseAgent):
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
        # Same implementation as in JobAnalysisAgent
        job_analysis_agent = JobAnalysisAgent(self.model_name, self.temperature)
        return job_analysis_agent._extract_technical_skills(job_info) 