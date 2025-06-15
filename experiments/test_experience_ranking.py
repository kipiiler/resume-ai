import os
import sys
import re
from dotenv import load_dotenv
from langgraph.graph import Graph
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, TypedDict, Annotated, Sequence, Dict, Any
import operator
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

# Add the parent directory to the path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.schema import Experience, ExperienceDB
from service.experience import ExperienceService
from job_scraper import JobInfo, extract_job_info

class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    job_posting_url: str
    job_info: Dict[str, Any]
    job_technical_skills: List[str]
    user_id: int
    experience_list: List[ExperienceDB]
    experience_skills_analysis: Dict[str, Any]
    ranked_experiences: List[str]
    error: str

@tool
def query_all_user_experiences(user_id: int) -> List[ExperienceDB]:
    """Query all experiences for a specific user from the database."""
    try:
        experience_service = ExperienceService()
        experiences = experience_service.get_user_experiences(user_id)
        return experiences
    except Exception as e:
        print(f"Error querying user experiences: {e}")
        return []

@tool
def extract_job_information(job_url: str) -> Dict[str, Any]:
    """Extract job information from a job posting URL."""
    try:
        job_info = extract_job_info(job_url)
        if job_info is None:
            raise Exception("Failed to extract job information")
        return job_info
    except Exception as e:
        print(f"Error extracting job info: {e}")
        raise e

def create_job_extraction_node():
    """Create node to extract job information from URL."""
    def job_extraction(state: AgentState) -> AgentState:
        try:
            job_url = state["job_posting_url"]
            job_info = extract_job_information.invoke({"job_url": job_url})
            return {"job_info": job_info}
        except Exception as e:
            return {"error": f"Failed to extract job information: {str(e)}"}
    return job_extraction

def create_technical_skills_extraction_node():
    """Create node to extract technical skills from job posting."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.1
    )
    
    def extract_technical_skills(state: AgentState) -> AgentState:
        if state.get("error"):
            return state  # Pass through error state
        
        job_info = state["job_info"]
        
        # Create skills extraction prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a technical recruiter expert at identifying technical skills from job postings.

Your task is to extract ALL technical skills mentioned in the job posting, including:
- Programming languages (Python, Java, C++, JavaScript, etc.)
- Frameworks and libraries (React, Django, TensorFlow, etc.)
- Databases (MySQL, PostgreSQL, MongoDB, etc.)
- Cloud platforms (AWS, Azure, GCP, etc.)
- Tools and technologies (Docker, Kubernetes, Git, etc.)
- Operating systems (Linux, Windows, etc.)
- Methodologies (Agile, DevOps, CI/CD, etc.)
- Domain-specific technologies (AI/ML, networking, security, etc.)

Instructions:
1. Extract technical skills from job title, description, and qualifications
2. Include both required and preferred skills
3. Normalize skill names (e.g., "Javascript" → "JavaScript")
4. Return ONLY a JSON array of strings
5. Each skill should be a single technology/tool name
6. Avoid duplicates and be comprehensive

Format your response as a JSON array like this:
["Python", "Machine Learning", "TensorFlow", "AWS", "Docker", "Git"]

Do not include any other text or explanation outside the JSON array."""),
            ("human", """Extract technical skills from this job posting:

Job Title: {job_title}
Company: {company_name}
Description: {description}
Qualifications: {qualifications}""")
        ])
        
        # Format the prompt with job data
        qualifications_text = "\n".join(job_info.get("qualifications", []))
        formatted_prompt = prompt.format(
            job_title=job_info.get("job_title", ""),
            company_name=job_info.get("company_name", ""),
            description=job_info.get("description", ""),
            qualifications=qualifications_text
        )
        
        try:
            # Get skills from LLM
            response = llm.invoke(formatted_prompt)
            response_text = response.content.strip()
            
            # Clean and parse JSON response
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            skills_list = json.loads(response_text)
            
            if not isinstance(skills_list, list):
                raise ValueError("Response is not a list")
            
            # Clean and normalize skills
            normalized_skills = []
            for skill in skills_list:
                if isinstance(skill, str) and skill.strip():
                    normalized_skills.append(skill.strip())
            
            return {"job_technical_skills": normalized_skills}
            
        except Exception as e:
            print(f"Error extracting technical skills: {e}")
            print(f"Raw response: {response.content}")
            # Fallback: extract from tech_stack if available
            fallback_skills = []
            if "qualifications" in job_info:
                # Simple keyword extraction as fallback
                common_skills = ["Python", "Java", "JavaScript", "React", "Node.js", "SQL", "AWS", "Docker", "Git", "Linux"]
                text_content = " ".join(job_info["qualifications"]).lower()
                for skill in common_skills:
                    if skill.lower() in text_content:
                        fallback_skills.append(skill)
            
            return {"job_technical_skills": fallback_skills}
    
    return extract_technical_skills

def create_experience_query_node():
    """Create node to query all user experiences."""
    def experience_query(state: AgentState) -> AgentState:
        if state.get("error"):
            return state  # Pass through error state
        
        try:
            user_id = state["user_id"]
            experiences = query_all_user_experiences.invoke({"user_id": user_id})
            return {"experience_list": experiences}
        except Exception as e:
            return {"error": f"Failed to query user experiences: {str(e)}"}
    return experience_query

def create_skills_analysis_node():
    """Create node to analyze skill matches between job and experiences using LLM."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2
    )
    
    def analyze_skills(state: AgentState) -> AgentState:
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
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a technical recruiter expert at analyzing skill matches between job requirements and candidate experience.

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

Be comprehensive in identifying skills from experience descriptions, not just tech_stack lists."""),
            ("human", """Analyze skill matches for these experiences:

{experiences_data}

Remember to look for technical skills mentioned in both the tech stack AND the experience descriptions.""")
        ])
        
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
            # Get skill analysis from LLM
            response = llm.invoke(formatted_prompt)
            response_text = response.content.strip()
            
            # Clean and parse JSON response
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            llm_analysis = json.loads(response_text)
            
            if "experience_analyses" in llm_analysis:
                analysis["experience_analyses"] = llm_analysis["experience_analyses"]
            else:
                raise ValueError("Invalid response structure")
            
            return {"experience_skills_analysis": analysis}
            
        except Exception as e:
            print(f"Error in LLM skill analysis: {e}")
            print(f"Raw response: {response.content}")
            
            # Fallback: Simple string-based matching
            print("Falling back to simple skill matching...")
            for i, exp in enumerate(experiences):
                exp_skills = exp.tech_stack if exp.tech_stack else []
                
                # Simple string matching as fallback
                job_skills_lower = [skill.lower() for skill in job_skills]
                exp_skills_lower = [skill.lower() for skill in exp_skills]
                
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
                    "missing_skills": [skill for skill in job_skills if skill.lower() not in exp_skills_lower]
                }
                
                analysis["experience_analyses"].append(exp_analysis)
            
            return {"experience_skills_analysis": analysis}
    
    return analyze_skills

def create_experience_ranking_node():
    """Create node to rank experiences based on holistic job relevance assessment."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.4
    )
    
    def experience_ranking(state: AgentState) -> AgentState:
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
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an experienced hiring manager at {company_name} evaluating candidates for the {job_title} position.

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

Focus on the person's journey, achievements, and potential rather than just technical checklist matching."""),
            ("human", "Evaluate and rank these experiences for overall fit:\n\n{experiences}")
        ])
        
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
            # Get holistic ranking from LLM
            response = llm.invoke(formatted_prompt)
            response_text = response.content.strip()
            
            # Clean and parse JSON response
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            ranked_list = json.loads(response_text)
            
            if not isinstance(ranked_list, list):
                raise ValueError("Response is not a list")
            
            return {"ranked_experiences": ranked_list}
            
        except Exception as e:
            print(f"Error in holistic ranking: {e}")
            print(f"Raw response: {response.content}")
            
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

def create_ranking_agent_graph():
    """Create the main ranking agent graph with skills analysis."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extract_job", create_job_extraction_node())
    workflow.add_node("extract_skills", create_technical_skills_extraction_node())
    workflow.add_node("query_experiences", create_experience_query_node())
    workflow.add_node("analyze_skills", create_skills_analysis_node())
    workflow.add_node("rank_experiences", create_experience_ranking_node())
    
    # Add edges
    workflow.add_edge("extract_job", "extract_skills")
    workflow.add_edge("extract_skills", "query_experiences")
    workflow.add_edge("query_experiences", "analyze_skills")
    workflow.add_edge("analyze_skills", "rank_experiences")
    workflow.set_entry_point("extract_job")
    
    return workflow.compile()

def test_experience_ranking():
    """Test the experience ranking agent with skills analysis."""
    load_dotenv()
    
    # Test with a sample job posting URL
    # You can replace this with any job posting URL
    job_url = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Software-Research-Intern--AI-Networking-Team---Fall-2025_JR1998253"
    user_id = 1
    
    print(f"🚀 Starting Enhanced Experience Ranking Agent Test")
    print(f"Job URL: {job_url}")
    print(f"User ID: {user_id}")
    print("="*60)
    
    # Create and run the graph
    graph = create_ranking_agent_graph()
    
    result = graph.invoke({
        "messages": [],
        "job_posting_url": job_url,
        "job_info": {},
        "job_technical_skills": [],
        "user_id": user_id,
        "experience_list": [],
        "experience_skills_analysis": {},
        "ranked_experiences": [],
        "error": ""
    })
    
    # Check for errors
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return result
    
    # Display results
    print("✅ Job Information Extracted:")
    job_info = result.get("job_info", {})
    print(f"  Company: {job_info.get('company_name', 'N/A')}")
    print(f"  Position: {job_info.get('job_title', 'N/A')}")
    print(f"  Location: {job_info.get('location', 'N/A')}")
    print(f"  Type: {job_info.get('job_type', 'N/A')}")
    
    print(f"\n🔧 Technical Skills Required:")
    job_skills = result.get("job_technical_skills", [])
    for skill in job_skills:
        print(f"  • {skill}")
    
    print(f"\n📊 Found {len(result.get('experience_list', []))} experiences for user {user_id}")
    
    # Display skills analysis
    skills_analysis = result.get("experience_skills_analysis", {})
    if skills_analysis and "experience_analyses" in skills_analysis:
        print(f"\n🎯 Skills Match Analysis:")
        for exp_analysis in skills_analysis["experience_analyses"]:
            print(f"\n  Experience {exp_analysis['experience_id']} - {exp_analysis['company']}:")
            print(f"    • Skill Match: {exp_analysis['match_percentage']}%")
            print(f"    • Direct Matches: {', '.join(exp_analysis['direct_matches']) if exp_analysis['direct_matches'] else 'None'}")
            if exp_analysis['related_matches']:
                print(f"    • Related Matches: {', '.join(exp_analysis['related_matches'])}")
            if exp_analysis['missing_skills']:
                print(f"    • Missing Skills: {', '.join(exp_analysis['missing_skills'][:5])}{'...' if len(exp_analysis['missing_skills']) > 5 else ''}")
    
    print(f"\n🏆 Final Experience Ranking (Most to Least Relevant):")
    ranked_experiences = result.get("ranked_experiences", [])
    for i, ranking in enumerate(ranked_experiences, 1):
        print(f"  {i}. {ranking}")
    
    # Assertions for testing
    assert "job_info" in result, "Job info should be extracted"
    assert "job_technical_skills" in result, "Technical skills should be extracted"
    assert "experience_list" in result, "Experience list should be queried"
    assert "experience_skills_analysis" in result, "Skills analysis should be performed"
    assert "ranked_experiences" in result, "Experiences should be ranked"
    assert len(result["ranked_experiences"]) > 0, "Should have at least one ranked experience"
    
    print(f"\n✅ Enhanced test completed successfully!")
    return result

def test_with_custom_url(job_url: str, user_id: int = 1):
    """Test the ranking agent with a custom job URL."""
    load_dotenv()
    
    print(f"🚀 Testing Enhanced Agent with custom URL")
    print(f"Job URL: {job_url}")
    print(f"User ID: {user_id}")
    print("="*60)
    
    graph = create_ranking_agent_graph()
    
    result = graph.invoke({
        "messages": [],
        "job_posting_url": job_url,
        "job_info": {},
        "job_technical_skills": [],
        "user_id": user_id,
        "experience_list": [],
        "experience_skills_analysis": {},
        "ranked_experiences": [],
        "error": ""
    })
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return result
    
    print("✅ Results:")
    print(f"Job: {result['job_info'].get('job_title', 'N/A')} at {result['job_info'].get('company_name', 'N/A')}")
    print(f"Technical Skills: {', '.join(result.get('job_technical_skills', []))}")
    print(f"Experiences found: {len(result.get('experience_list', []))}")
    
    # Show skill analysis summary
    skills_analysis = result.get("experience_skills_analysis", {})
    if skills_analysis and "experience_analyses" in skills_analysis:
        print("\nSkill Match Summary:")
        for exp in skills_analysis["experience_analyses"]:
            print(f"  {exp['company']}: {exp['match_percentage']}% match")
    
    print("\nRankings:")
    for i, ranking in enumerate(result.get("ranked_experiences", []), 1):
        print(f"  {i}. {ranking}")
    
    return result

if __name__ == "__main__":
    # Run the test
    test_experience_ranking()
    
    # Uncomment to test with a different URL
    # test_with_custom_url("YOUR_JOB_URL_HERE")




