import json
from typing import TypedDict, Annotated, Sequence, Dict, Any, Callable, List
import operator
from langchain_core.messages import HumanMessage, AIMessage

from agents.base_agents import BaseAgentState
from agents.database_agent import DatabaseAgent
from agents.job_analysis_agent import JobAnalysisAgent

class RankingAgentState(BaseAgentState):
    """State for the Ranking Agent."""
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    job_posting_url: str
    job_info: Dict[str, Any]
    job_technical_skills: List[str]
    user_id: int
    experience_list: List[Any]  # List of ExperienceDB objects
    experience_skills_analysis: Dict[str, Any]
    ranked_experiences: List[str]

class RankingAgent(DatabaseAgent, JobAnalysisAgent):
    """Agent for ranking user experiences based on job posting relevance."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite", temperature: float = 0.4):
        # Initialize both parent classes
        DatabaseAgent.__init__(self, model_name, temperature)
        JobAnalysisAgent.__init__(self, model_name, temperature)
    
    def get_state_class(self) -> type:
        """Return the state class for this agent."""
        return RankingAgentState
    
    def create_nodes(self) -> Dict[str, Callable]:
        """Create all nodes for the ranking agent."""
        return {
            "extract_job": self._create_job_extraction_node(),
            "extract_skills": self._create_technical_skills_extraction_node(),
            "query_experiences": self._create_experience_query_node(),
            "analyze_skills": self._create_skills_analysis_node(),
            "rank_experiences": self._create_experience_ranking_node()
        }
    
    def define_edges(self) -> List[tuple]:
        """Define the edges between nodes."""
        return [
            ("extract_job", "extract_skills"),
            ("extract_skills", "query_experiences"),
            ("query_experiences", "analyze_skills"),
            ("analyze_skills", "rank_experiences")
        ]
    
    def get_entry_point(self) -> str:
        """Return the entry point node name."""
        return "extract_job"
    
    def query_all_user_experiences(self, user_id: int) -> List[Any]:
        """Query all experiences for a specific user from the database."""
        try:
            experience_service = self._get_experience_service()
            experiences = experience_service.get_user_experiences(user_id)
            return experiences
        except Exception as e:
            print(f"Error querying user experiences: {e}")
            return []
    
    def _create_job_extraction_node(self):
        """Create node to extract job information from URL."""
        def job_extraction(state: RankingAgentState) -> RankingAgentState:
            try:
                job_url = state["job_posting_url"]
                job_info = self._extract_job_information(job_url)
                return {"job_info": job_info}
            except Exception as e:
                return {"error": f"Failed to extract job information: {str(e)}"}
        return job_extraction
    
    def _create_technical_skills_extraction_node(self):
        """Create node to extract technical skills from job posting."""
        def extract_technical_skills(state: RankingAgentState) -> RankingAgentState:
            if state.get("error"):
                return state  # Pass through error state
            
            job_info = state["job_info"]
            try:
                skills = self._extract_technical_skills(job_info)
                return {"job_technical_skills": skills}
            except Exception as e:
                print(f"Error extracting technical skills: {e}")
                return {"job_technical_skills": []}
        
        return extract_technical_skills
    
    def _create_experience_query_node(self):
        """Create node to query all user experiences."""
        def experience_query(state: RankingAgentState) -> RankingAgentState:
            if state.get("error"):
                return state  # Pass through error state
            
            try:
                user_id = state["user_id"]
                experiences = self.query_all_user_experiences(user_id)
                return {"experience_list": experiences}
            except Exception as e:
                return {"error": f"Failed to query user experiences: {str(e)}"}
        return experience_query
    
    def _create_skills_analysis_node(self):
        """Create node to analyze skill matches between job and experiences using LLM."""
        def analyze_skills(state: RankingAgentState) -> RankingAgentState:
            if state.get("error"):
                return state  # Pass through error state
            
            job_skills = state.get("job_technical_skills", [])
            experiences = state.get("experience_list", [])
            
            if not experiences:
                return {"experience_skills_analysis": {}}
            
            analysis = {
                "job_skills": job_skills,
                "experience_analyses": []
            }
            
            # Create skill matching prompt
            prompt = self._create_prompt_template(
                system_message="""You are a technical recruiter expert at analyzing skill matches between job requirements and candidate experience.

Your task is to analyze how well each candidate's experience matches the required technical skills from a job posting.

Job Required Technical Skills: {job_skills}

For each experience provided, you need to:
1. Identify all technical skills mentioned in the experience (from description and tech stack)
2. Match these skills against the job requirements
3. Consider related/equivalent technologies (e.g., React.js ≈ React, PyTorch ≈ TensorFlow for ML)
4. Calculate a skill match percentage
5. Identify direct matches, related matches, and missing skills

Return your analysis as a JSON object with this exact structure:
{{
    "experience_analyses": [
        {{
            "experience_id": 1,
            "company": "Company Name",
            "experience_skills": ["skill1", "skill2", "skill3"],
            "direct_matches": ["exact skill matches"],
            "related_matches": ["job_skill ≈ experience_skill"],
            "match_percentage": 75.5,
            "missing_skills": ["skills not found in experience"]
        }}
    ]
}}

Guidelines for skill matching:
- Direct match: Exact same technology (Python = Python)
- Related match: Similar/equivalent technologies (React ≈ React.js, TensorFlow ≈ PyTorch for ML)
- Consider context: "machine learning" experience matches "AI", "deep learning", "neural networks"
- Programming languages: Consider similar languages as partial matches
- Frameworks: Consider similar frameworks in same domain as related
- Calculate percentage: (direct_matches + related_matches * 0.7) / total_job_skills * 100

Be comprehensive in identifying skills from experience descriptions, not just tech_stack lists.""",
                human_message="""Analyze skill matches for these experiences:

{experiences_data}

Remember to look for technical skills mentioned in both the tech stack AND the experience descriptions."""
            )
            
            # Format experiences data for analysis
            experiences_data = []
            for i, exp in enumerate(experiences):
                exp_data = f"""
Experience {i+1}:
Company: {exp.company_name}
Tech Stack: {', '.join(exp.tech_stack) if exp.tech_stack else 'None listed'}
Description: {exp.long_description} {exp.short_description}
"""
                experiences_data.append(exp_data.strip())
            
            formatted_prompt = prompt.format(
                job_skills=', '.join(job_skills),
                experiences_data='\n\n'.join(experiences_data)
            )
            
            try:
                response_text = self._safe_llm_invoke(formatted_prompt, '{"experience_analyses": []}')
                response_text = self._clean_json_response(response_text)
                llm_analysis = json.loads(response_text)
                
                if "experience_analyses" in llm_analysis:
                    analysis["experience_analyses"] = llm_analysis["experience_analyses"]
                else:
                    raise ValueError("Invalid response structure")
                
                return {"experience_skills_analysis": analysis}
                
            except Exception as e:
                print(f"Error in LLM skill analysis: {e}")
                # Fallback: Simple string-based matching
                print("Falling back to simple skill matching...")
                for i, exp in enumerate(experiences):
                    exp_skills = exp.tech_stack if exp.tech_stack else []
                    
                    # Simple string matching as fallback
                    direct_matches = []
                    for job_skill in job_skills:
                        for exp_skill in exp_skills:
                            if job_skill.lower() == exp_skill.lower():
                                direct_matches.append(job_skill)
                    
                    # Calculate simple match percentage
                    match_percentage = (len(direct_matches) / len(job_skills) * 100) if job_skills else 0
                    
                    exp_analysis = {
                        "experience_id": i + 1,
                        "company": exp.company_name,
                        "experience_skills": exp_skills,
                        "direct_matches": direct_matches,
                        "related_matches": [],
                        "match_percentage": round(match_percentage, 1),
                        "missing_skills": [skill for skill in job_skills if skill.lower() not in [s.lower() for s in exp_skills]]
                    }
                    
                    analysis["experience_analyses"].append(exp_analysis)
                
                return {"experience_skills_analysis": analysis}
        
        return analyze_skills
    
    def _create_experience_ranking_node(self):
        """Create node to rank experiences based on holistic job relevance assessment."""
        def experience_ranking(state: RankingAgentState) -> RankingAgentState:
            if state.get("error"):
                return state  # Pass through error state
            
            job_info = state["job_info"]
            experiences = state["experience_list"]
            skills_analysis = state.get("experience_skills_analysis", {})
            
            if not experiences:
                return {"ranked_experiences": [], "error": "No experiences found for user"}
            
            # Format experiences with skill context for holistic ranking
            experience_descriptions = []
            for i, exp in enumerate(experiences):
                # Get skill analysis for this experience
                exp_analysis = None
                if skills_analysis and "experience_analyses" in skills_analysis:
                    exp_analysis = skills_analysis["experience_analyses"][i] if i < len(skills_analysis["experience_analyses"]) else None
                
                # Format skill information more naturally
                skill_context = ""
                if exp_analysis:
                    skill_context = f"""
Technical Background:
- Technologies Used: {', '.join(exp_analysis['experience_skills']) if exp_analysis['experience_skills'] else 'Not specified'}
- Relevant Skills for This Role: {', '.join(exp_analysis['direct_matches'] + exp_analysis['related_matches']) if (exp_analysis['direct_matches'] or exp_analysis['related_matches']) else 'Limited overlap'}
- Additional Context: {f"Strong match in {len(exp_analysis['direct_matches'])} core areas" if exp_analysis['direct_matches'] else "Transferable technical foundation"}"""
                
                exp_text = f"""
Experience {i+1}:
Company: {exp.company_name} ({exp.company_location})
Duration: {exp.start_date} to {exp.end_date}
Role Description: {exp.long_description}
Key Achievements: {exp.short_description}
{skill_context}
"""
                experience_descriptions.append(exp_text.strip())
            
            # Create holistic ranking prompt
            job_skills = skills_analysis.get("job_skills", [])
            prompt = self._create_prompt_template(
                system_message="""You are an experienced hiring manager at {company_name} evaluating candidates for the {job_title} position.

Your task is to rank the candidate's experiences based on overall fit and potential for success in this role.

Job Context:
- Company: {company_name}
- Position: {job_title}
- Location: {location}
- Job Type: {job_type}
- Role Description: {description}
- Key Requirements: {qualifications}
- Important Technical Areas: {technical_skills}

Evaluation Approach:
Rather than focusing solely on exact skill matches, consider the COMPLETE picture:

1. **Problem-Solving Alignment**: How similar are the challenges they've solved to what this role requires?
2. **Learning & Adaptability**: Evidence of picking up new technologies and growing in complexity
3. **Impact & Scale**: The scope and significance of their contributions
4. **Technical Foundation**: Solid fundamentals that enable learning required technologies
5. **Domain Relevance**: Industry knowledge and context that transfers to this role
6. **Leadership & Collaboration**: Ability to work effectively in team environments

Instructions:
- Read each experience holistically - consider the full context, not just skill checklists
- Look for evidence of growth, impact, and problem-solving ability
- Consider how their experience trajectory prepares them for this specific role
- Value depth of experience and demonstrated results over perfect skill alignment
- Think about potential and transferable capabilities, not just current exact matches
- Rank from most suitable overall candidate to least suitable

Return ONLY a JSON array of strings explaining your ranking decisions:
["Experience X: Best fit because [holistic reasoning about fit, growth, impact, and potential]",
 "Experience Y: Strong candidate due to [comprehensive assessment of relevant factors]",
 "Experience Z: Solid option with [balanced view of strengths and development areas]"]

Focus on the person's journey, achievements, and potential rather than just technical checklist matching.""",
                human_message="Evaluate and rank these experiences for overall fit:\n\n{experiences}"
            )
            
            # Format the prompt with job and experience data
            formatted_prompt = prompt.format(
                company_name=job_info.get("company_name", "Unknown Company"),
                job_title=job_info.get("job_title", "Unknown Position"),
                location=job_info.get("location", "Unknown Location"),
                job_type=job_info.get("job_type", "Unknown Type"),
                description=job_info.get("description", "No description available"),
                qualifications=", ".join(job_info.get("qualifications", [])),
                technical_skills=", ".join(job_skills) if job_skills else "Various technical skills",
                experiences="\n\n".join(experience_descriptions)
            )
            
            try:
                response_text = self._safe_llm_invoke(formatted_prompt, "[]")
                response_text = self._clean_json_response(response_text)
                ranked_list = json.loads(response_text)
                
                if not isinstance(ranked_list, list):
                    raise ValueError("Response is not a list")
                
                return {"ranked_experiences": ranked_list}
                
            except Exception as e:
                print(f"Error in holistic ranking: {e}")
                
                # Fallback: Create balanced ranking considering multiple factors
                fallback_ranking = []
                for i, exp in enumerate(experiences):
                    # Create a balanced assessment
                    skill_info = ""
                    if skills_analysis and "experience_analyses" in skills_analysis and i < len(skills_analysis["experience_analyses"]):
                        exp_analysis = skills_analysis["experience_analyses"][i]
                        if exp_analysis['direct_matches'] or exp_analysis['related_matches']:
                            skill_info = f" with relevant technical background in {', '.join((exp_analysis['direct_matches'] + exp_analysis['related_matches'])[:3])}"
                        else:
                            skill_info = " with transferable technical foundation"
                    
                    fallback_ranking.append(
                        f"Experience {i+1}: {exp.company_name} - {exp.short_description[:100]}...{skill_info}"
                    )
                
                return {"ranked_experiences": fallback_ranking}
        
        return experience_ranking
    
    def rank_experiences(self, job_posting_url: str, user_id: int) -> Dict[str, Any]:
        """Main method to rank user experiences based on a job posting."""
        initial_state = {
            "messages": [],
            "job_posting_url": job_posting_url,
            "job_info": {},
            "job_technical_skills": [],
            "user_id": user_id,
            "experience_list": [],
            "experience_skills_analysis": {},
            "ranked_experiences": [],
            "error": ""
        }
        
        result = self.run(initial_state)
        return result
    
    def get_ranking_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a summary of the ranking results."""
        if result.get("error"):
            return {"error": result["error"]}
        
        job_info = result.get("job_info", {})
        skills_analysis = result.get("experience_skills_analysis", {})
        
        summary = {
            "job_title": job_info.get("job_title", "Unknown"),
            "company": job_info.get("company_name", "Unknown"),
            "technical_skills_required": result.get("job_technical_skills", []),
            "experiences_analyzed": len(result.get("experience_list", [])),
            "rankings": result.get("ranked_experiences", [])
        }
        
        # Add skill match summary
        if skills_analysis and "experience_analyses" in skills_analysis:
            summary["skill_matches"] = [
                {
                    "company": exp["company"],
                    "match_percentage": exp["match_percentage"],
                    "direct_matches": len(exp["direct_matches"]),
                    "related_matches": len(exp["related_matches"])
                }
                for exp in skills_analysis["experience_analyses"]
            ]
        
        return summary 