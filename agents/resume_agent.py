import re
from typing import TypedDict, Annotated, Sequence, Dict, Any, Callable, List
import operator
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from agents.base_agents import BaseAgentState
from agents.database_agent import DatabaseAgent

class ResumeAgentState(BaseAgentState):
    """State for the Resume Agent."""
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    experience_id: int
    experience: str
    bullet_points: List[str]

class ResumeAgent(DatabaseAgent):
    """Agent for generating resume bullet points from experience data."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite", temperature: float = 1.0):
        super().__init__(model_name, temperature)
    
    def get_state_class(self) -> type:
        """Return the state class for this agent."""
        return ResumeAgentState
    
    def create_nodes(self) -> Dict[str, Callable]:
        """Create all nodes for the resume agent."""
        return {
            "query_experience": self._create_experience_query_node(),
            "generate_bullet_points": self._create_bullet_point_generator()
        }
    
    def define_edges(self) -> List[tuple]:
        """Define the edges between nodes."""
        return [
            ("query_experience", "generate_bullet_points")
        ]
    
    def get_entry_point(self) -> str:
        """Return the entry point node name."""
        return "query_experience"
    
    def query_experience_from_db(self, experience_id: int) -> str:
        """Query experience details from the database using ExperienceService."""
        try:
            experience_service = self._get_experience_service()
            experience = experience_service.get_experience(experience_id)
            
            if experience:
                # Format the experience data into a comprehensive description
                description = f"""
                Company: {experience.company_name} ({experience.company_location})
                Duration: {experience.start_date} to {experience.end_date}
                Description: {experience.long_description + " " + experience.short_description}
                Tech Stack: {', '.join(experience.tech_stack) if experience.tech_stack else 'Not specified'}
                """
                return description.strip()
            else:
                return f"Experience with ID {experience_id} not found"
        except Exception as e:
            return f"Error querying experience: {str(e)}"
    
    def _create_experience_query_node(self):
        """Create the experience query node."""
        def experience_query(state: ResumeAgentState) -> ResumeAgentState:
            experience_id = state.get("experience_id", 1)  # Default to ID 1 if not provided
            experience = self.query_experience_from_db(experience_id)
            return {"experience": experience}
        return experience_query
    
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
        prompt = self._create_prompt_template(
            system_message="""You are an expert resume writer. Generate exactly 3 bullet points in the Google XYZ format for the given experience.

The XYZ format is: Accomplished [X] by implementing [Y], which led to [Z].

Rules:
1. Generate EXACTLY 3 bullet points
2. Each bullet point should be on a separate line
3. Start each bullet point with an action verb
4. Include specific metrics and achievements when possible
5. Make each bullet point impactful and measurable
6. Do not include any introductory text or explanations
7. Do not use bullet point symbols (*, -, •) - just write the text
8. The bullet points should focus on technical details (using specific technologies, algorithms, etc.)

Example format:
Led a team of 5 developers by implementing microservices architecture, which resulted in 40% improved system performance
Managed full software development lifecycle by establishing CI/CD pipelines, which led to 50% faster deployment cycles
Optimized database queries by implementing caching strategies, which achieved 60% reduction in response time""",
            human_message="Generate 3 bullet points for this experience: {experience}"
        )
        
        chain = prompt | self.llm | StrOutputParser()
        
        def generate_bullet_points(state: ResumeAgentState) -> ResumeAgentState:
            experience = state["experience"]
            bullet_points_text = chain.invoke({"experience": experience})
            bullet_points_list = self._parse_bullet_points(bullet_points_text)
            
            # Ensure we have exactly 3 bullet points
            if len(bullet_points_list) < 3:
                # If we don't have enough, pad with generic ones
                while len(bullet_points_list) < 3:
                    bullet_points_list.append(f"Contributed to team success by applying technical skills, which enhanced project outcomes")
            
            return {"bullet_points": bullet_points_list[:3]}
        
        return generate_bullet_points
    
    def generate_bullet_points(self, experience_id: int) -> Dict[str, Any]:
        """Main method to generate bullet points for an experience."""
        initial_state = {
            "messages": [],
            "experience_id": experience_id,
            "experience": "",
            "bullet_points": [],
            "error": ""
        }
        
        result = self.run(initial_state)
        return result
    
    def generate_multiple_experiences(self, experience_ids: List[int]) -> Dict[int, Dict[str, Any]]:
        """Generate bullet points for multiple experiences."""
        results = {}
        for exp_id in experience_ids:
            try:
                results[exp_id] = self.generate_bullet_points(exp_id)
            except Exception as e:
                results[exp_id] = {"error": f"Failed to process experience {exp_id}: {str(e)}"}
        return results 