import json
from typing import TypedDict, Annotated, Sequence, Dict, Any, Callable, List, Tuple
import operator
from langchain_core.messages import HumanMessage, AIMessage

from agents.base_agents import BaseAgentState
from agents.database_agent import DatabaseAgent
from job_scraper import JobInfo

class RankingAgentState(BaseAgentState):
    """State for the Ranking Agent."""
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    job_info: JobInfo
    job_technical_skills: List[str]
    user_id: int
    experience_list: List[Any]  # List of ExperienceDB objects
    project_list: List[Any]  # List of ProjectDB objects
    experience_skills_analysis: Dict[str, Any]
    project_skills_analysis: Dict[str, Any]
    ranked_experiences: List[Tuple[int, str]]
    ranked_projects: List[Tuple[int, str]]
    ranking_type: str  # "experiences", "projects", or "both"

class RankingAgent(DatabaseAgent):
    """Agent for ranking user experiences and projects based on job posting relevance."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite", temperature: float = 0.4):
        super().__init__(model_name, temperature)
    
    def get_state_class(self) -> type:
        """Return the state class for this agent."""
        return RankingAgentState
    
    def create_nodes(self) -> Dict[str, Callable]:
        """Create all nodes for the ranking agent."""
        return {
            "extract_skills": self._create_technical_skills_extraction_node(),
            "query_data": self._create_data_query_node(),
            "analyze_skills": self._create_skills_analysis_node(),
            "rank_items": self._create_ranking_node()
        }
    
    def define_edges(self) -> List[tuple]:
        """Define the edges between nodes."""
        return [
            ("extract_skills", "query_data"),
            ("query_data", "analyze_skills"),
            ("analyze_skills", "rank_items")
        ]
    
    def get_entry_point(self) -> str:
        """Return the entry point node name."""
        return "extract_skills"
    
    def query_all_user_experiences(self, user_id: int) -> List[Any]:
        """Query all experiences for a specific user from the database."""
        try:
            experience_service = self._get_experience_service()
            experiences = experience_service.get_user_experiences(user_id)
            return experiences
        except Exception as e:
            print(f"Error querying user experiences: {e}")
            return []
    
    def query_all_user_projects(self, user_id: int) -> List[Any]:
        """Query all projects for a specific user from the database."""
        try:
            # Import here to avoid circular imports
            from services.project import ProjectService
            project_service = ProjectService()
            projects = project_service.get_user_projects(user_id)
            return projects
        except Exception as e:
            print(f"Error querying user projects: {e}")
            return []
    
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
    
    def _extract_technical_skills(self, job_info: JobInfo) -> List[str]:
        """Extract technical skills from job information using LLM."""
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
        qualifications_text = "\n".join(job_info.qualifications)
        
        formatted_prompt = prompt.format(
            company_name=job_info.company_name,
            job_title=job_info.job_title,
            description=job_info.description,
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
            text_to_search = f"{job_info.description} {qualifications_text}".lower()
            
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
    
    def _create_data_query_node(self):
        """Create node to query user experiences and/or projects based on ranking type."""
        def data_query(state: RankingAgentState) -> RankingAgentState:
            if state.get("error"):
                return state  # Pass through error state
            
            try:
                user_id = state["user_id"]
                ranking_type = state.get("ranking_type", "experiences")
                
                result = {}
                
                if ranking_type in ["experiences", "both"]:
                    experiences = self.query_all_user_experiences(user_id)
                    result["experience_list"] = experiences
                
                if ranking_type in ["projects", "both"]:
                    projects = self.query_all_user_projects(user_id)
                    result["project_list"] = projects
                
                return result
            except Exception as e:
                return {"error": f"Failed to query user data: {str(e)}"}
        return data_query
    
    def _create_skills_analysis_node(self):
        """Create node to analyze skill matches between job and experiences/projects using LLM."""
        def analyze_skills(state: RankingAgentState) -> RankingAgentState:
            if state.get("error"):
                return state  # Pass through error state
            
            job_skills = state.get("job_technical_skills", [])
            ranking_type = state.get("ranking_type", "experiences")
            
            result = {}
            
            # Analyze experiences if requested
            if ranking_type in ["experiences", "both"]:
                experiences = state.get("experience_list", [])
                if experiences:
                    exp_analysis = self._analyze_experience_skills(experiences, job_skills)
                    result["experience_skills_analysis"] = exp_analysis
            
            # Analyze projects if requested
            if ranking_type in ["projects", "both"]:
                projects = state.get("project_list", [])
                if projects:
                    proj_analysis = self._analyze_project_skills(projects, job_skills)
                    result["project_skills_analysis"] = proj_analysis
            
            return result
        
        return analyze_skills
    
    def _analyze_experience_skills(self, experiences: List[Any], job_skills: List[str]) -> Dict[str, Any]:
        """Analyze skill matches for experiences."""
        analysis = {
            "job_skills": job_skills,
            "experience_analyses": []
        }
        
        # Create skill matching prompt for experiences
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
            
        except Exception as e:
            print(f"Error in LLM experience skill analysis: {e}")
            # Fallback: Simple string-based matching
            print("Falling back to simple experience skill matching...")
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
        
        return analysis
    
    def _analyze_project_skills(self, projects: List[Any], job_skills: List[str]) -> Dict[str, Any]:
        """Analyze skill matches for projects."""
        analysis = {
            "job_skills": job_skills,
            "project_analyses": []
        }
        
        # Create skill matching prompt for projects
        prompt = self._create_prompt_template(
            system_message="""You are a technical recruiter expert at analyzing skill matches between job requirements and candidate projects.

Your task is to analyze how well each candidate's project matches the required technical skills from a job posting.

Job Required Technical Skills: {job_skills}

For each project provided, you need to:
1. Identify all technical skills mentioned in the project (from description and tech stack)
2. Match these skills against the job requirements
3. Consider related/equivalent technologies (e.g., React.js ≈ React, PyTorch ≈ TensorFlow for ML)
4. Calculate a skill match percentage
5. Identify direct matches, related matches, and missing skills

Return your analysis as a JSON object with this exact structure:
{{
    "project_analyses": [
        {{
            "project_id": 1,
            "project_name": "Project Name",
            "project_skills": ["skill1", "skill2", "skill3"],
            "direct_matches": ["exact skill matches"],
            "related_matches": ["job_skill ≈ project_skill"],
            "match_percentage": 75.5,
            "missing_skills": ["skills not found in project"]
        }}
    ]
}}

Guidelines for skill matching:
- Direct match: Exact same technology (Python = Python)
- Related match: Similar/equivalent technologies (React ≈ React.js, TensorFlow ≈ PyTorch for ML)
- Consider context: "machine learning" project matches "AI", "deep learning", "neural networks"
- Programming languages: Consider similar languages as partial matches
- Frameworks: Consider similar frameworks in same domain as related
- Calculate percentage: (direct_matches + related_matches * 0.7) / total_job_skills * 100

Be comprehensive in identifying skills from project descriptions, not just tech_stack lists.""",
            human_message="""Analyze skill matches for these projects:

{projects_data}

Remember to look for technical skills mentioned in both the tech stack AND the project descriptions."""
        )
        
        # Format projects data for analysis
        projects_data = []
        for i, proj in enumerate(projects):
            proj_data = f"""
Project {i+1}:
Name: {proj.project_name}
Tech Stack: {', '.join(proj.tech_stack) if proj.tech_stack else 'None listed'}
Description: {proj.long_description} {proj.short_description}
"""
            projects_data.append(proj_data.strip())
        
        formatted_prompt = prompt.format(
            job_skills=', '.join(job_skills),
            projects_data='\n\n'.join(projects_data)
        )
        
        try:
            response_text = self._safe_llm_invoke(formatted_prompt, '{"project_analyses": []}')
            response_text = self._clean_json_response(response_text)
            llm_analysis = json.loads(response_text)
            
            if "project_analyses" in llm_analysis:
                analysis["project_analyses"] = llm_analysis["project_analyses"]
            else:
                raise ValueError("Invalid response structure")
            
        except Exception as e:
            print(f"Error in LLM project skill analysis: {e}")
            # Fallback: Simple string-based matching
            print("Falling back to simple project skill matching...")
            for i, proj in enumerate(projects):
                proj_skills = proj.tech_stack if proj.tech_stack else []
                
                # Simple string matching as fallback
                direct_matches = []
                for job_skill in job_skills:
                    for proj_skill in proj_skills:
                        if job_skill.lower() == proj_skill.lower():
                            direct_matches.append(job_skill)
                
                # Calculate simple match percentage
                match_percentage = (len(direct_matches) / len(job_skills) * 100) if job_skills else 0
                
                proj_analysis = {
                    "project_id": i + 1,
                    "project_name": proj.project_name,
                    "project_skills": proj_skills,
                    "direct_matches": direct_matches,
                    "related_matches": [],
                    "match_percentage": round(match_percentage, 1),
                    "missing_skills": [skill for skill in job_skills if skill.lower() not in [s.lower() for s in proj_skills]]
                }
                
                analysis["project_analyses"].append(proj_analysis)
        
        return analysis
    
    def _create_ranking_node(self):
        """Create node to rank experiences and/or projects based on holistic job relevance assessment."""
        def ranking(state: RankingAgentState) -> RankingAgentState:
            if state.get("error"):
                return state  # Pass through error state
            
            job_info = state["job_info"]
            ranking_type = state.get("ranking_type", "experiences")
            
            result = {}
            
            # Rank experiences if requested
            if ranking_type in ["experiences", "both"]:
                experiences = state.get("experience_list", [])
                exp_skills_analysis = state.get("experience_skills_analysis", {})
                if experiences:
                    ranked_exp = self._rank_experiences(job_info, experiences, exp_skills_analysis)
                    result["ranked_experiences"] = ranked_exp
            
            # Rank projects if requested
            if ranking_type in ["projects", "both"]:
                projects = state.get("project_list", [])
                proj_skills_analysis = state.get("project_skills_analysis", {})
                if projects:
                    ranked_proj = self._rank_projects(job_info, projects, proj_skills_analysis)
                    result["ranked_projects"] = ranked_proj
            
            return result
        
        return ranking
    
    def _rank_experiences(self, job_info: JobInfo, experiences: List[Any], skills_analysis: Dict[str, Any]) -> List[Tuple[int, str]]:
        """Rank experiences based on holistic job relevance assessment."""
        if not experiences:
            return []
        
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

Return ONLY a JSON array of arrays, where each inner array contains [experience_id, reasoning]:
[[1, "Best fit because [holistic reasoning about fit, growth, impact, and potential]"],
 [3, "Strong candidate due to [comprehensive assessment of relevant factors]"],
 [2, "Solid option with [balanced view of strengths and development areas]"]]

Each inner array should contain:
- First element: The experience number (1, 2, 3, etc. based on the order provided)
- Second element: Detailed reasoning for the ranking

Focus on the person's journey, achievements, and potential rather than just technical checklist matching.""",
            human_message="Evaluate and rank these experiences for overall fit:\n\n{experiences}"
        )
        
        # Format the prompt with job and experience data
        formatted_prompt = prompt.format(
            company_name=job_info.company_name,
            job_title=job_info.job_title,
            location=job_info.location,
            job_type=job_info.job_type,
            description=job_info.description,
            qualifications=", ".join(job_info.qualifications),
            technical_skills=", ".join(job_skills) if job_skills else "Various technical skills",
            experiences="\n\n".join(experience_descriptions)
        )
        
        try:
            response_text = self._safe_llm_invoke(formatted_prompt, "[]")
            response_text = self._clean_json_response(response_text)
            ranked_list = json.loads(response_text)
            
            if not isinstance(ranked_list, list):
                raise ValueError("Response is not a list")
            
            # Convert to list of tuples (id, reason)
            structured_rankings = []
            for item in ranked_list:
                if isinstance(item, list) and len(item) >= 2:
                    exp_id = item[0]
                    reason = item[1]
                    structured_rankings.append((exp_id, reason))
                else:
                    # Fallback for malformed responses
                    structured_rankings.append((len(structured_rankings) + 1, str(item)))
            
            return structured_rankings
            
        except Exception as e:
            print(f"Error in holistic experience ranking: {e}")
            
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
                
                reason = f"{exp.company_name} - {exp.short_description[:100]}...{skill_info}"
                fallback_ranking.append((i + 1, reason))
            
            return fallback_ranking
    
    def _rank_projects(self, job_info: JobInfo, projects: List[Any], skills_analysis: Dict[str, Any]) -> List[Tuple[int, str]]:
        """Rank projects based on holistic job relevance assessment."""
        if not projects:
            return []
        
        # Format projects with skill context for holistic ranking
        project_descriptions = []
        for i, proj in enumerate(projects):
            # Get skill analysis for this project
            proj_analysis = None
            if skills_analysis and "project_analyses" in skills_analysis:
                proj_analysis = skills_analysis["project_analyses"][i] if i < len(skills_analysis["project_analyses"]) else None
            
            # Format skill information more naturally
            skill_context = ""
            if proj_analysis:
                skill_context = f"""
Technical Background:
- Technologies Used: {', '.join(proj_analysis['project_skills']) if proj_analysis['project_skills'] else 'Not specified'}
- Relevant Skills for This Role: {', '.join(proj_analysis['direct_matches'] + proj_analysis['related_matches']) if (proj_analysis['direct_matches'] or proj_analysis['related_matches']) else 'Limited overlap'}
- Additional Context: {f"Strong match in {len(proj_analysis['direct_matches'])} core areas" if proj_analysis['direct_matches'] else "Transferable technical foundation"}"""
            
            proj_text = f"""
Project {i+1}:
Name: {proj.project_name}
Duration: {proj.start_date} to {proj.end_date}
Description: {proj.long_description}
Key Achievements: {proj.short_description}
{skill_context}
"""
            project_descriptions.append(proj_text.strip())
        
        # Create holistic ranking prompt for projects
        job_skills = skills_analysis.get("job_skills", [])
        prompt = self._create_prompt_template(
            system_message="""You are an experienced hiring manager at {company_name} evaluating candidate projects for the {job_title} position.

Your task is to rank the candidate's projects based on overall relevance and potential for success in this role.

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

1. **Problem-Solving Alignment**: How similar are the challenges solved to what this role requires?
2. **Technical Complexity**: Evidence of handling complex technical problems and architectures
3. **Impact & Innovation**: The scope, significance, and creativity of their solutions
4. **Technical Foundation**: Solid fundamentals demonstrated through project implementation
5. **Domain Relevance**: Project domain knowledge that transfers to this role
6. **Implementation Quality**: Evidence of good engineering practices and thorough execution

Instructions:
- Read each project holistically - consider the full context, not just skill checklists
- Look for evidence of technical depth, problem-solving ability, and innovation
- Consider how their project experience prepares them for this specific role
- Value complexity of implementation and demonstrated results over perfect skill alignment
- Think about technical capabilities and problem-solving approach demonstrated
- Rank from most relevant and impressive project to least relevant

Return ONLY a JSON array of arrays, where each inner array contains [project_id, reasoning]:
[[1, "Best fit because [holistic reasoning about technical relevance, complexity, and innovation]"],
 [3, "Strong relevance due to [comprehensive assessment of technical factors]"],
 [2, "Good option with [balanced view of technical strengths and applicability]"]]

Each inner array should contain:
- First element: The project number (1, 2, 3, etc. based on the order provided)
- Second element: Detailed reasoning for the ranking

Focus on technical execution, problem-solving approach, and relevance to the target role.""",
            human_message="Evaluate and rank these projects for overall relevance:\n\n{projects}"
        )
        
        # Format the prompt with job and project data
        formatted_prompt = prompt.format(
            company_name=job_info.company_name,
            job_title=job_info.job_title,
            location=job_info.location,
            job_type=job_info.job_type,
            description=job_info.description,
            qualifications=", ".join(job_info.qualifications),
            technical_skills=", ".join(job_skills) if job_skills else "Various technical skills",
            projects="\n\n".join(project_descriptions)
        )
        
        try:
            response_text = self._safe_llm_invoke(formatted_prompt, "[]")
            response_text = self._clean_json_response(response_text)
            ranked_list = json.loads(response_text)
            
            if not isinstance(ranked_list, list):
                raise ValueError("Response is not a list")
            
            # Convert to list of tuples (id, reason)
            structured_rankings = []
            for item in ranked_list:
                if isinstance(item, list) and len(item) >= 2:
                    proj_id = item[0]
                    reason = item[1]
                    structured_rankings.append((proj_id, reason))
                else:
                    # Fallback for malformed responses
                    structured_rankings.append((len(structured_rankings) + 1, str(item)))
            
            return structured_rankings
            
        except Exception as e:
            print(f"Error in holistic project ranking: {e}")
            
            # Fallback: Create balanced ranking considering multiple factors
            fallback_ranking = []
            for i, proj in enumerate(projects):
                # Create a balanced assessment
                skill_info = ""
                if skills_analysis and "project_analyses" in skills_analysis and i < len(skills_analysis["project_analyses"]):
                    proj_analysis = skills_analysis["project_analyses"][i]
                    if proj_analysis['direct_matches'] or proj_analysis['related_matches']:
                        skill_info = f" with relevant technical background in {', '.join((proj_analysis['direct_matches'] + proj_analysis['related_matches'])[:3])}"
                    else:
                        skill_info = " with transferable technical foundation"
                
                reason = f"{proj.project_name} - {proj.short_description[:100]}...{skill_info}"
                fallback_ranking.append((i + 1, reason))
            
            return fallback_ranking
    
    def rank_experiences(self, job_info: JobInfo, user_id: int) -> Dict[str, Any]:
        """Main method to rank user experiences based on a job posting."""
        initial_state = {
            "messages": [],
            "job_info": job_info,
            "job_technical_skills": [],
            "user_id": user_id,
            "experience_list": [],
            "project_list": [],
            "experience_skills_analysis": {},
            "project_skills_analysis": {},
            "ranked_experiences": [],
            "ranked_projects": [],
            "ranking_type": "experiences",
            "error": ""
        }
        
        result = self.run(initial_state)
        return result
    
    def rank_projects(self, job_info: JobInfo, user_id: int) -> Dict[str, Any]:
        """Main method to rank user projects based on a job posting."""
        initial_state = {
            "messages": [],
            "job_info": job_info,
            "job_technical_skills": [],
            "user_id": user_id,
            "experience_list": [],
            "project_list": [],
            "experience_skills_analysis": {},
            "project_skills_analysis": {},
            "ranked_experiences": [],
            "ranked_projects": [],
            "ranking_type": "projects",
            "error": ""
        }
        
        result = self.run(initial_state)
        return result
    
    def rank_both(self, job_info: JobInfo, user_id: int) -> Dict[str, Any]:
        """Main method to rank both user experiences and projects based on a job posting."""
        initial_state = {
            "messages": [],
            "job_info": job_info,
            "job_technical_skills": [],
            "user_id": user_id,
            "experience_list": [],
            "project_list": [],
            "experience_skills_analysis": {},
            "project_skills_analysis": {},
            "ranked_experiences": [],
            "ranked_projects": [],
            "ranking_type": "both",
            "error": ""
        }
        
        result = self.run(initial_state)
        return result
    
    def get_ranking_summary(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract a summary of the ranking results."""
        if result.get("error"):
            return {"error": result["error"]}
        
        job_info = result.get("job_info", {})
        exp_skills_analysis = result.get("experience_skills_analysis", {})
        proj_skills_analysis = result.get("project_skills_analysis", {})
        
        summary = {
            "job_title": job_info.job_title,
            "company": job_info.company_name,
            "technical_skills_required": result.get("job_technical_skills", []),
            "experiences_analyzed": len(result.get("experience_list", [])),
            "projects_analyzed": len(result.get("project_list", [])),
            "experience_rankings": result.get("ranked_experiences", []),
            "project_rankings": result.get("ranked_projects", [])
        }
        
        # Add experience skill match summary
        if exp_skills_analysis and "experience_analyses" in exp_skills_analysis:
            summary["experience_skill_matches"] = [
                {
                    "company": exp["company"],
                    "match_percentage": exp["match_percentage"],
                    "direct_matches": len(exp["direct_matches"]),
                    "related_matches": len(exp["related_matches"])
                }
                for exp in exp_skills_analysis["experience_analyses"]
            ]
        
        # Add project skill match summary
        if proj_skills_analysis and "project_analyses" in proj_skills_analysis:
            summary["project_skill_matches"] = [
                {
                    "project_name": proj["project_name"],
                    "match_percentage": proj["match_percentage"],
                    "direct_matches": len(proj["direct_matches"]),
                    "related_matches": len(proj["related_matches"])
                }
                for proj in proj_skills_analysis["project_analyses"]
            ]
        
        return summary
    
    # Backward compatibility methods for URL-based inputs
    def rank_experiences_from_url(self, job_posting_url: str, user_id: int) -> Dict[str, Any]:
        """Backward compatibility method to rank experiences from job posting URL."""
        try:
            # Import here to avoid circular imports
            from agents.job_analysis_agent import JobAnalysisAgent
            
            # Use JobAnalysisAgent to convert URL to JobInfo
            job_analysis_agent = JobAnalysisAgent(self.model_name, self.temperature)
            analysis_result = job_analysis_agent.analyze_job(job_posting_url)
            
            if analysis_result.get("error"):
                return {"error": f"Job analysis failed: {analysis_result['error']}"}
            
            job_info = analysis_result.get("job_info")
            if not job_info:
                return {"error": "Failed to extract job information"}
            
            # Use the new method with JobInfo
            return self.rank_experiences(job_info, user_id)
            
        except Exception as e:
            return {"error": f"Failed to process job URL: {str(e)}"}
    
    def rank_projects_from_url(self, job_posting_url: str, user_id: int) -> Dict[str, Any]:
        """Backward compatibility method to rank projects from job posting URL."""
        try:
            # Import here to avoid circular imports
            from agents.job_analysis_agent import JobAnalysisAgent
            
            # Use JobAnalysisAgent to convert URL to JobInfo
            job_analysis_agent = JobAnalysisAgent(self.model_name, self.temperature)
            analysis_result = job_analysis_agent.analyze_job(job_posting_url)
            
            if analysis_result.get("error"):
                return {"error": f"Job analysis failed: {analysis_result['error']}"}
            
            job_info = analysis_result.get("job_info")
            if not job_info:
                return {"error": "Failed to extract job information"}
            
            # Use the new method with JobInfo
            return self.rank_projects(job_info, user_id)
            
        except Exception as e:
            return {"error": f"Failed to process job URL: {str(e)}"}
    
    def rank_both_from_url(self, job_posting_url: str, user_id: int) -> Dict[str, Any]:
        """Backward compatibility method to rank both experiences and projects from job posting URL."""
        try:
            # Import here to avoid circular imports
            from agents.job_analysis_agent import JobAnalysisAgent
            
            # Use JobAnalysisAgent to convert URL to JobInfo
            job_analysis_agent = JobAnalysisAgent(self.model_name, self.temperature)
            analysis_result = job_analysis_agent.analyze_job(job_posting_url)
            
            if analysis_result.get("error"):
                return {"error": f"Job analysis failed: {analysis_result['error']}"}
            
            job_info = analysis_result.get("job_info")
            if not job_info:
                return {"error": "Failed to extract job information"}
            
            # Use the new method with JobInfo
            return self.rank_both(job_info, user_id)
            
        except Exception as e:
            return {"error": f"Failed to process job URL: {str(e)}"} 