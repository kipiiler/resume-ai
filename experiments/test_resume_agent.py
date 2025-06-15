import os
import sys
import re
from dotenv import load_dotenv
from langgraph.graph import Graph
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import TypedDict, Annotated, Sequence
import operator
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import Graph, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Add the parent directory to the path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from service.experience import ExperienceService
from service.user import UserService

# Define the state type
class AgentState(TypedDict):
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    experience_id: int
    experience: str
    bullet_points: list[str]

# Real database query tool using ExperienceService
@tool
def query_experience_from_db(experience_id: int) -> str:
    """Query experience details from the database using ExperienceService."""
    try:
        experience_service = ExperienceService()
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

# Create the experience query node
def create_experience_query_node():
    def experience_query(state: AgentState) -> AgentState:
        experience_id = state.get("experience_id", 1)  # Default to ID 1 if not provided
        experience = query_experience_from_db.invoke({"experience_id": experience_id})
        return {"experience": experience}
    return experience_query

# Custom output parser for bullet points
def parse_bullet_points(text: str) -> list[str]:
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

# Create the bullet point generation node
def create_bullet_point_generator():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=1
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert resume writer. Generate exactly 3 bullet points in the Google XYZ format for the given experience.

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
Optimized database queries by implementing caching strategies, which achieved 60% reduction in response time"""),
        ("human", "Generate 3 bullet points for this experience: {experience}")
    ])
    
    chain = prompt | llm | StrOutputParser()
    
    def generate_bullet_points(state: AgentState) -> AgentState:
        experience = state["experience"]
        bullet_points_text = chain.invoke({"experience": experience})
        bullet_points_list = parse_bullet_points(bullet_points_text)
        
        # Ensure we have exactly 3 bullet points
        if len(bullet_points_list) < 3:
            # If we don't have enough, pad with generic ones
            while len(bullet_points_list) < 3:
                bullet_points_list.append(f"Contributed to team success by applying technical skills, which enhanced project outcomes")
        
        return {"bullet_points": bullet_points_list[:3]}
    
    return generate_bullet_points

# Create the main graph
def create_resume_agent_graph():
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("query_experience", create_experience_query_node())
    workflow.add_node("generate_bullet_points", create_bullet_point_generator())
    
    # Add edges
    workflow.add_edge("query_experience", "generate_bullet_points")
    workflow.set_entry_point("query_experience")
    
    # Compile the graph
    return workflow.compile()

# Test the resume agent
def test_resume_agent():
    # Create the graph
    graph = create_resume_agent_graph()
    
    # Test with a specific experience ID (you can change this)
    experience_id = 5
    
    # Run the graph
    result = graph.invoke({
        "messages": [],
        "experience_id": experience_id,
        "experience": "",
        "bullet_points": []
    })

    print(f"\n=== Resume Agent Test Results ===")
    print(f"Experience ID: {experience_id}")
    print(f"\nExperience Details:")
    print(result["experience"])
    print(f"\nGenerated Bullet Points ({len(result['bullet_points'])}):")
    for i, point in enumerate(result["bullet_points"], 1):
        print(f"{i}. {point}")
    
    # Assertions
    assert "experience" in result
    assert "bullet_points" in result
    assert len(result["bullet_points"]) == 3, f"Expected 3 bullet points, got {len(result['bullet_points'])}"
    assert all(isinstance(point, str) and len(point.strip()) > 0 for point in result["bullet_points"]), "All bullet points should be non-empty strings"
    
    print(f"\n✅ Test passed! Generated {len(result['bullet_points'])} bullet points successfully.")
    return result

# Function to test with different experience IDs
def test_multiple_experiences():
    """Test the agent with multiple experience IDs to see different results."""
    experience_service = ExperienceService()
    
    # Get all available experiences (limit to first 3 for testing)
    try:
        # This is a simple way to test - you might want to get actual user experiences
        for exp_id in range(1, 4):  # Test with IDs 1, 2, 3
            print(f"\n{'='*50}")
            print(f"Testing with Experience ID: {exp_id}")
            print(f"{'='*50}")
            
            try:
                graph = create_resume_agent_graph()
                result = graph.invoke({
                    "messages": [],
                    "experience_id": exp_id,
                    "experience": "",
                    "bullet_points": []
                })
                
                print(f"Experience: {result['experience'][:200]}...")
                print(f"Bullet Points:")
                for i, point in enumerate(result['bullet_points'], 1):
                    print(f"  {i}. {point}")
                    
            except Exception as e:
                print(f"Error testing experience ID {exp_id}: {str(e)}")
                
    except Exception as e:
        print(f"Error in test_multiple_experiences: {str(e)}")

if __name__ == "__main__":
    load_dotenv()
    
    # Run single test
    test_resume_agent()
    
    # Uncomment to test multiple experiences
    # test_multiple_experiences() 