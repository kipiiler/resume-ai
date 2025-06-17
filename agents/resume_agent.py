import re
from typing import TypedDict, Annotated, Sequence, Dict, Any, Callable, List, Optional
import operator
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from agents.base_agents import BaseAgentState
from agents.database_agent import DatabaseAgent
from job_scraper import JobInfo

class ResumeAgentState(BaseAgentState):
    """State for the Resume Agent."""
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    item_id: int  # Can be experience_id or project_id
    item_type: str  # "experience" or "project"
    item_data: str  # The formatted experience or project data
    ranking_reason: Optional[str]  # Reason from ranking agent
    job_info: Optional[JobInfo]  # Job information for context
    bullet_points: List[str]

class ResumeAgent(DatabaseAgent):
    """Agent for generating resume bullet points from experience or project data."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite", temperature: float = 1.0):
        super().__init__(model_name, temperature)
    
    def get_state_class(self) -> type:
        """Return the state class for this agent."""
        return ResumeAgentState
    
    def create_nodes(self) -> Dict[str, Callable]:
        """Create all nodes for the resume agent."""
        return {
            "query_data": self._create_data_query_node(),
            "generate_bullet_points": self._create_bullet_point_generator()
        }
    
    def define_edges(self) -> List[tuple]:
        """Define the edges between nodes."""
        return [
            ("query_data", "generate_bullet_points")
        ]
    
    def get_entry_point(self) -> str:
        """Return the entry point node name."""
        return "query_data"
    
    def query_experience_from_db(self, experience_id: int) -> str:
        """Query experience details from the database using ExperienceService."""
        try:
            experience_service = self._get_experience_service()
            experience = experience_service.get_experience(experience_id)
            
            if experience:
                # Format the experience data into a comprehensive description
                description = f"""
                Company: {experience.company_name} ({experience.company_location})
                Role/Position: {experience.role_title}
                Duration: {experience.start_date} to {experience.end_date}
                Description: {experience.long_description + " " + experience.short_description}
                Tech Stack: {', '.join(experience.tech_stack) if experience.tech_stack else 'Not specified'}
                """
                return description.strip()
            else:
                return f"Experience with ID {experience_id} not found"
        except Exception as e:
            return f"Error querying experience: {str(e)}"
    
    def query_project_from_db(self, project_id: int) -> str:
        """Query project details from the database using ProjectService."""
        try:
            # Import here to avoid circular imports
            from services.project import ProjectService
            project_service = ProjectService()
            project = project_service.get_project(project_id)
            
            if project:
                # Format the project data into a comprehensive description
                description = f"""
                Project Name: {project.project_name}
                Duration: {project.start_date} to {project.end_date}
                Description: {project.long_description + " " + project.short_description}
                Tech Stack: {', '.join(project.tech_stack) if project.tech_stack else 'Not specified'}
                """
                return description.strip()
            else:
                return f"Project with ID {project_id} not found"
        except Exception as e:
            return f"Error querying project: {str(e)}"
    
    def _create_data_query_node(self):
        """Create the data query node that handles both experiences and projects."""
        def data_query(state: ResumeAgentState) -> ResumeAgentState:
            item_id = state.get("item_id", 1)
            item_type = state.get("item_type", "experience")
            
            if item_type == "experience":
                item_data = self.query_experience_from_db(item_id)
            elif item_type == "project":
                item_data = self.query_project_from_db(item_id)
            else:
                item_data = f"Unknown item type: {item_type}"
            
            return {"item_data": item_data}
        return data_query
    
    def _parse_bullet_points(self, text: str) -> List[str]:
        """Parse bullet points from the LLM output, handling various formats."""
        # Remove any introductory text
        lines = text.split('\n')
        bullet_points = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Remove common bullet point markers and numbering
            cleaned_line = re.sub(r'^[\*\-\•\d\.\)\s]+', '', line).strip()
            
            # Skip lines that are too short or are introductory text
            if len(cleaned_line) > 20 and not cleaned_line.lower().startswith(('here are', 'the following', 'below are')):
                # Remove markdown formatting
                cleaned_line = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned_line)
                bullet_points.append(cleaned_line)
        
        # Return exactly 3 bullet points
        return bullet_points[:3] if len(bullet_points) >= 3 else bullet_points
    
    def _create_bullet_point_generator(self):
        """Create the bullet point generation node."""
        def generate_bullet_points(state: ResumeAgentState) -> ResumeAgentState:
            item_data = state["item_data"]
            item_type = state.get("item_type", "experience")
            ranking_reason = state.get("ranking_reason", "")
            job_info = state.get("job_info")
            
            # Create context-aware prompt based on item type
            if item_type == "project":
                context_prompt = self._create_project_bullet_prompt()
            else:
                context_prompt = self._create_experience_bullet_prompt()
            
            # Add ranking reason context if provided
            ranking_context = ""
            if ranking_reason:
                ranking_context = f"""
                \n\nRanking Context: This {item_type} was selected because: {ranking_reason}
                \nUse this context to emphasize the most relevant aspects in your bullet points.
                \nThere could be multiple reasons for the ranking, so you need to consider all of them.
                \nAn experience or project can have multiple things that make it relevant to the job. Only include the most relevant ones.
                \nYou need to generate 3 bullet points for the {item_type} based on the ranking context.
                """

            # Add job context if provided
            job_context = ""
            if job_info:
                job_context = f"\n\nJob Context:\n"
                job_context += f"Position: {job_info.job_title} at {job_info.company_name}\n"
                job_context += f"Location: {job_info.location}\n"
                job_context += f"Job Type: {job_info.job_type}\n"
                job_context += f"Description: {job_info.description[:500]}...\n"  # Truncate to avoid token limits
                job_context += f"Key Qualifications: {'; '.join(job_info.qualifications[:5])}\n"  # First 5 qualifications
                job_context += "Tailor the bullet points to highlight relevant skills and experiences that match this job posting and the ranking context."
            
            prompt_input = {
                "item_data": item_data,
                "item_type": item_type,
                "ranking_context": ranking_context,
                "job_context": job_context
            }
            
            chain = context_prompt | self.llm | StrOutputParser()
            bullet_points_text = chain.invoke(prompt_input)
            bullet_points_list = self._parse_bullet_points(bullet_points_text)
            
            # Ensure we have exactly 3 bullet points
            if len(bullet_points_list) < 3:
                # If we don't have enough, pad with generic ones
                while len(bullet_points_list) < 3:
                    if item_type == "project":
                        bullet_points_list.append(f"Developed innovative solution by applying technical expertise, which demonstrated problem-solving capabilities")
                    else:
                        bullet_points_list.append(f"Contributed to team success by applying technical skills, which enhanced project outcomes")
            
            return {"bullet_points": bullet_points_list[:3]}
        
        return generate_bullet_points
    
    def _create_experience_bullet_prompt(self):
        """Create prompt template for experience bullet points."""
        return self._create_prompt_template(
            system_message="""You are an expert resume writer for software engineers. Generate exactly 3 bullet points in the Google XYZ format for the given work experience.

The XYZ format is: Accomplished [X] by implementing [Y], which led to [Z].

Rules:
1. Generate EXACTLY 3 bullet points
2. Each bullet point should be on a separate line
3. Start each bullet point with an action verb
4. Include specific metrics and achievements when possible
5. Make each bullet point impactful and measurable
6. Do not include any introductory text or explanations
7. Do not use bullet point symbols (*, -, •) - just write the text
8. Focus on technical details (using specific technologies, algorithms, etc.)
9. Emphasize professional impact and business value
10. If job context is provided, tailor bullet points to highlight relevant skills and technologies
11. Do not include write any generic bullet points (example: Contributed to technical documentation, planning, collaboration, etc...). Only include thing that is technical and relevant to the job.
12. Each bullet point should be short, concise, and to the point.
13. We want to save space, therefore, each bullet point should be around 100 characters. if it is too long, do around 200 characters to fill the space.

Example format:
Led a team of 5 developers by implementing microservices architecture, which resulted in 40% improved system performance
Managed full software development lifecycle by establishing CI/CD pipelines, which led to 50% faster deployment cycles
Optimized database queries by implementing caching strategies, which achieved 60% reduction in response time""",
            human_message="Generate 3 bullet points for this {item_type}: {item_data}{ranking_context}{job_context}"
        )
    
    def _create_project_bullet_prompt(self):
        """Create prompt template for project bullet points."""
        return self._create_prompt_template(
            system_message="""You are an expert resume writer for software engineers. Generate exactly 3 bullet points in the Google XYZ format for the given project.

The XYZ format is: Accomplished [X] by implementing [Y], which led to [Z].

Rules:
1. Generate EXACTLY 3 bullet points
2. Each bullet point should be on a separate line
3. Start each bullet point with an action verb
4. Include specific metrics and achievements when possible
5. Make each bullet point impactful and measurable
6. Do not include any introductory text or explanations
7. Do not use bullet point symbols (*, -, •) - just write the text
8. Focus on technical implementation details and innovation
9. Emphasize problem-solving skills and technical expertise
10. Highlight learning outcomes and technical growth
11. If job context is provided, tailor bullet points to highlight relevant skills and technologies
12. Do not include write any generic bullet points (example: Contributed to technical documentation, planning, collaboration, etc...). Only include thing that is technical and relevant to the job.
13. Each bullet point should be short, concise, and to the point.
14. We want to save space, therefore, each bullet point should be around 100 characters. if it is too long, do around 200 characters to fill the space.

Example format:
Developed machine learning model by implementing neural networks in TensorFlow, which achieved 95% accuracy in classification tasks
Built full-stack web application by integrating React frontend with Node.js backend, which demonstrated end-to-end development skills
Designed scalable database architecture by implementing MongoDB with Redis caching, which supported 10,000+ concurrent users""",
            human_message="Generate 3 bullet points for this {item_type}: {item_data}{ranking_context}{job_context}"
        )
    
    def generate_bullet_points_for_experience(self, experience_id: int, ranking_reason: Optional[str] = None, job_info: Optional[JobInfo] = None) -> Dict[str, Any]:
        """Main method to generate bullet points for an experience."""
        initial_state = {
            "messages": [],
            "item_id": experience_id,
            "item_type": "experience",
            "item_data": "",
            "ranking_reason": ranking_reason,
            "job_info": job_info,
            "bullet_points": [],
            "error": ""
        }
        
        result = self.run(initial_state)
        return result
    
    def generate_bullet_points_for_project(self, project_id: int, ranking_reason: Optional[str] = None, job_info: Optional[JobInfo] = None) -> Dict[str, Any]:
        """Main method to generate bullet points for a project."""
        initial_state = {
            "messages": [],
            "item_id": project_id,
            "item_type": "project",
            "item_data": "",
            "ranking_reason": ranking_reason,
            "job_info": job_info,
            "bullet_points": [],
            "error": ""
        }
        
        result = self.run(initial_state)
        return result
    
    def generate_bullet_points(self, item_id: int, item_type: str = "experience", ranking_reason: Optional[str] = None, job_info: Optional[JobInfo] = None) -> Dict[str, Any]:
        """Generic method to generate bullet points for either experience or project."""
        if item_type == "project":
            return self.generate_bullet_points_for_project(item_id, ranking_reason, job_info)
        else:
            return self.generate_bullet_points_for_experience(item_id, ranking_reason, job_info)
    
    def generate_multiple_items(self, items: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate bullet points for multiple experiences/projects.
        
        Args:
            items: List of dicts with keys: 'id', 'type', 'ranking_reason' (optional)
        """
        results = {}
        for item in items:
            item_id = item.get('id')
            item_type = item.get('type', 'experience')
            ranking_reason = item.get('ranking_reason')
            
            try:
                key = f"{item_type}_{item_id}"
                results[key] = self.generate_bullet_points(item_id, item_type, ranking_reason)
            except Exception as e:
                results[key] = {"error": f"Failed to process {item_type} {item_id}: {str(e)}"}
        
        return results
    
    # Backward compatibility methods
    def generate_bullet_points_legacy(self, experience_id: int) -> Dict[str, Any]:
        """Legacy method for backward compatibility."""
        return self.generate_bullet_points_for_experience(experience_id)
    
    def generate_multiple_experiences(self, experience_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Legacy method for backward compatibility."""
        results = {}
        for exp_id in experience_ids:
            try:
                results[exp_id] = self.generate_bullet_points_for_experience(exp_id)
            except Exception as e:
                results[exp_id] = {"error": f"Failed to process experience {exp_id}: {str(e)}"}
        return results 