import json
from typing import Dict, Any, List, Optional, TypedDict, Annotated, Sequence, Callable
import operator
from langchain_core.messages import HumanMessage, AIMessage

from agents.base_agents import BaseAgent, BaseAgentState
from experiments.job_scraper import extract_job_info, JobInfo
from model.schema import JobPosting, JobPostingDB
from services.job_posting import JobPostingService

class JobAnalysisState(BaseAgentState):
    """State for the Job Analysis Agent."""
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    job_posting_url: str
    job_info: JobInfo
    job_technical_skills: List[str]
    job_exists_in_db: bool
    existing_job_posting: Optional[JobPostingDB]
    error: str

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
            "check_job_exists": self._create_job_exists_check_node(),
            "extract_job_info": self._create_job_extraction_node(),
            "load_existing_job": self._create_load_existing_job_node(),
            "extract_technical_skills": self._create_technical_skills_extraction_node(),
            "save_job_to_db": self._create_save_job_to_db_node()
        }
    
    def define_edges(self) -> List[tuple]:
        """Define the edges between nodes."""
        return [
            # Conditional edge: if job exists, load it; otherwise extract it
            ("check_job_exists", 
             self._create_binary_condition_func("job_exists_in_db", "load_existing_job", "extract_job_info"),
             {"load_existing_job": "load_existing_job", "extract_job_info": "extract_job_info"}),
            
            # Extract technical skills
            ("extract_job_info", "extract_technical_skills"),

            # save job to db
            ("extract_technical_skills", "save_job_to_db"),
        ]
    
    def get_entry_point(self) -> str:
        """Return the entry point node name."""
        return "check_job_exists"
    
    def _check_if_job_posting_exists(self, job_posting_url: str) -> Optional[JobPostingDB]:
        """Check if a job posting exists in the database."""
        job_posting_service = JobPostingService()
        return job_posting_service.get_job_posting_by_url(job_posting_url)
    
    def _save_job_to_db(self, job_posting: JobPostingDB):
        """Save a job posting to the database."""
        job_posting_service = JobPostingService()
        job_posting_service.create_job_posting(
            JobPosting(
                job_posting_url=job_posting.job_posting_url,
                company_name=job_posting.company_name,
                job_title=job_posting.job_title,
                job_location=job_posting.job_location,
                job_type=job_posting.job_type,
                job_description=job_posting.job_description,
                job_qualifications=job_posting.job_qualifications,
                job_technical_skills=job_posting.job_technical_skills
            )
        )
        return job_posting
    
    def _create_save_job_to_db_node(self):
        """Create node to save a job posting to the database."""
        def save_job_to_db(state: JobAnalysisState) -> JobAnalysisState:
            return self._save_job_to_db(
                JobPosting(
                    job_posting_url=state["job_posting_url"],
                    company_name=state["job_info"].company_name,
                    job_title=state["job_info"].job_title,
                    job_location=state["job_info"].location,
                    job_type=state["job_info"].job_type,
                    job_description=state["job_info"].description,
                    job_qualifications=state["job_info"].qualifications,
                    job_technical_skills=state["job_technical_skills"]
                )
            )
        return save_job_to_db

    
    def _create_job_exists_check_node(self):
        """Create node to check if a job posting exists in the database."""
        def check_job_exists(state: JobAnalysisState) -> JobAnalysisState:
            job_posting_url = state["job_posting_url"]
            existing_job = self._check_if_job_posting_exists(job_posting_url)
            
            if existing_job:
                return {
                    "job_exists_in_db": True,
                    "existing_job_posting": existing_job
                }
            else:
                return {
                    "job_exists_in_db": False,
                    "existing_job_posting": None
                }
        return check_job_exists
    
    def _create_load_existing_job_node(self):
        """Create node to load existing job data from database."""
        def load_existing_job(state: JobAnalysisState) -> JobAnalysisState:
            existing_job = state["existing_job_posting"]
            print(f"Loading existing job: {existing_job}")
            
            if existing_job:
                # Convert existing job posting to JobInfo object
                job_info = JobInfo(
                    company_name=existing_job.company_name,
                    job_title=existing_job.job_title,
                    location=existing_job.job_location,
                    job_type=existing_job.job_type,
                    description=existing_job.job_description,
                    qualifications=existing_job.job_qualifications if existing_job.job_qualifications else []
                )
                
                return {
                    "job_info": job_info,
                    "job_technical_skills": existing_job.job_technical_skills if existing_job.job_technical_skills else []
                }
            else:
                return {"error": "No existing job posting found"}
        
        return load_existing_job
    
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
            
            # If skills were already loaded from database, skip extraction
            if state.get("job_technical_skills") and len(state["job_technical_skills"]) > 0:
                print("Using existing technical skills from database")
                return {"job_technical_skills": state["job_technical_skills"]}
            
            job_info = state["job_info"]
            try:
                # Convert JobInfo to dict for the skills extraction method
                job_info_dict = job_info.model_dump()
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
            "job_exists_in_db": False,
            "existing_job_posting": None,
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