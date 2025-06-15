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
    user_id: int
    experience_list: List[ExperienceDB]
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

def create_experience_ranking_node():
    """Create node to rank experiences based on job relevance."""
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3
    )
    
    def experience_ranking(state: AgentState) -> AgentState:
        if state.get("error"):
            return state  # Pass through error state
        
        job_info = state["job_info"]
        experiences = state["experience_list"]
        
        if not experiences:
            return {"ranked_experiences": [], "error": "No experiences found for user"}
        
        # Format experiences for ranking
        experience_descriptions = []
        for i, exp in enumerate(experiences):
            exp_text = f"""
Experience {i+1}:
Company: {exp.company_name} ({exp.company_location})
Duration: {exp.start_date} to {exp.end_date}
Description: {exp.long_description} {exp.short_description}
Tech Stack: {', '.join(exp.tech_stack) if exp.tech_stack else 'Not specified'}
"""
            experience_descriptions.append(exp_text.strip())
        
        # Create ranking prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a hiring manager at {company_name} looking to fill the position of {job_title}.

Your task is to rank the candidate's experiences based on their relevance to this job posting.

Job Details:
- Company: {company_name}
- Position: {job_title}
- Location: {location}
- Job Type: {job_type}
- Description: {description}
- Required Qualifications: {qualifications}

Instructions:
1. Analyze each experience against the job requirements
2. Consider technical skills, relevant experience, industry alignment, and transferable skills
3. Rank experiences from most relevant (1) to least relevant
4. Return ONLY a JSON list of strings in ranked order
5. Each string should be a brief summary of why that experience is relevant

Format your response as a JSON array like this:
["Experience 1: Most relevant because...", "Experience 2: Second most relevant because...", "Experience 3: Least relevant because..."]

Do not include any other text or explanation outside the JSON array."""),
            ("human", "Here are the candidate's experiences to rank:\n\n{experiences}")
        ])
        
        # Format the prompt with job and experience data
        formatted_prompt = prompt.format(
            company_name=job_info.get("company_name", "Unknown Company"),
            job_title=job_info.get("job_title", "Unknown Position"),
            location=job_info.get("location", "Unknown Location"),
            job_type=job_info.get("job_type", "Unknown Type"),
            description=job_info.get("description", "No description available"),
            qualifications=", ".join(job_info.get("qualifications", [])),
            experiences="\n\n".join(experience_descriptions)
        )
        
        try:
            # Get ranking from LLM
            response = llm.invoke(formatted_prompt)
            response_text = response.content.strip()
            
            # Clean and parse JSON response
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            ranked_list = json.loads(response_text)
            
            if not isinstance(ranked_list, list):
                raise ValueError("Response is not a list")
            
            return {"ranked_experiences": ranked_list}
            
        except Exception as e:
            print(f"Error in ranking: {e}")
            print(f"Raw response: {response.content}")
            # Fallback: return simple ranking
            fallback_ranking = [f"Experience {i+1}: {exp.company_name} - {exp.short_description}" 
                              for i, exp in enumerate(experiences)]
            return {"ranked_experiences": fallback_ranking}
    
    return experience_ranking

def create_ranking_agent_graph():
    """Create the main ranking agent graph."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extract_job", create_job_extraction_node())
    workflow.add_node("query_experiences", create_experience_query_node())
    workflow.add_node("rank_experiences", create_experience_ranking_node())
    
    # Add edges
    workflow.add_edge("extract_job", "query_experiences")
    workflow.add_edge("query_experiences", "rank_experiences")
    workflow.set_entry_point("extract_job")
    
    return workflow.compile()

def test_experience_ranking():
    """Test the experience ranking agent."""
    load_dotenv()
    
    # Test with a sample job posting URL
    # You can replace this with any job posting URL
    job_url = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Software-Research-Intern--AI-Networking-Team---Fall-2025_JR1998253"
    user_id = 1
    
    print(f"🚀 Starting Experience Ranking Agent Test")
    print(f"Job URL: {job_url}")
    print(f"User ID: {user_id}")
    print("="*60)
    
    # Create and run the graph
    graph = create_ranking_agent_graph()
    
    result = graph.invoke({
        "messages": [],
        "job_posting_url": job_url,
        "job_info": {},
        "user_id": user_id,
        "experience_list": [],
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
    
    print(f"\n📊 Found {len(result.get('experience_list', []))} experiences for user {user_id}")
    
    print(f"\n🏆 Experience Ranking (Most to Least Relevant):")
    ranked_experiences = result.get("ranked_experiences", [])
    for i, ranking in enumerate(ranked_experiences, 1):
        print(f"  {i}. {ranking}")
    
    # Assertions for testing
    assert "job_info" in result, "Job info should be extracted"
    assert "experience_list" in result, "Experience list should be queried"
    assert "ranked_experiences" in result, "Experiences should be ranked"
    assert len(result["ranked_experiences"]) > 0, "Should have at least one ranked experience"
    
    print(f"\n✅ Test completed successfully!")
    return result

def test_with_custom_url(job_url: str, user_id: int = 1):
    """Test the ranking agent with a custom job URL."""
    load_dotenv()
    
    print(f"🚀 Testing with custom URL")
    print(f"Job URL: {job_url}")
    print(f"User ID: {user_id}")
    print("="*60)
    
    graph = create_ranking_agent_graph()
    
    result = graph.invoke({
        "messages": [],
        "job_posting_url": job_url,
        "job_info": {},
        "user_id": user_id,
        "experience_list": [],
        "ranked_experiences": [],
        "error": ""
    })
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return result
    
    print("✅ Results:")
    print(f"Job: {result['job_info'].get('job_title', 'N/A')} at {result['job_info'].get('company_name', 'N/A')}")
    print(f"Experiences found: {len(result.get('experience_list', []))}")
    print("Rankings:")
    for i, ranking in enumerate(result.get("ranked_experiences", []), 1):
        print(f"  {i}. {ranking}")
    
    return result

if __name__ == "__main__":
    # Run the test
    test_experience_ranking()
    
    # Uncomment to test with a different URL
    # test_with_custom_url("YOUR_JOB_URL_HERE")




