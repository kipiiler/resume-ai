from typing import TypedDict, Optional
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph
from model.database import Database
from model.schema import CompanyDB
import json
import os
import time
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Get API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

class CompanyInfoState(TypedDict):
    company_name: str
    search_results: Optional[str]
    structured_data: Optional[dict]
    error: Optional[str]

# Initialize tools and models
search_tool = DuckDuckGoSearchRun()
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",  # Updated model name
        temperature=0,
        google_api_key=GOOGLE_API_KEY
    )
except Exception as e:
    raise ValueError(f"Failed to initialize Google AI model: {str(e)}")

db = Database.get_instance()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def perform_search(query: str) -> str:
    """Perform a search with retry logic."""
    time.sleep(2)  # Add delay between searches
    return search_tool.run(query)

def search_node(state: CompanyInfoState) -> CompanyInfoState:
    """Search for company information using DuckDuckGo."""
    try:
        # Multiple targeted searches to gather comprehensive information
        searches = [
            f"{state['company_name']} company mission and vision",
            f"{state['company_name']} headquarters location address",
            f"{state['company_name']} official website domain",
            f"{state['company_name']} industry sector market",
            f"{state['company_name']} company description overview history"
        ]
        
        all_results = []
        for query in searches:
            try:
                result = perform_search(query)
                if result:
                    all_results.append(result)
                    print(f"Successfully retrieved results for: {query}")
            except Exception as e:
                print(f"Warning: Search failed for query '{query}': {str(e)}")
                continue
        
        if not all_results:
            return {**state, "error": "No search results found"}
            
        # Combine all results with clear separation
        combined_results = "\n\n---\n\n".join(all_results)
        print(f"Total search results retrieved: {len(all_results)} out of {len(searches)}")
        return {**state, "search_results": combined_results}
    except Exception as e:
        return {**state, "error": f"Search failed: {str(e)}"}

def extract_node(state: CompanyInfoState) -> CompanyInfoState:
    """Extract structured data from search results using LLM."""
    if state.get("error"):
        return state

    prompt = f"""
Given the following comprehensive search results about a company, extract detailed information and return it as a JSON object with these exact fields:
- name (string): The full company name
- mission (string): The complete mission statement, including vision and values if available
- location (string): The full headquarters location with city and state/country
- website (string): The complete company website URL
- industry (string): The primary industry sector and any notable sub-sectors
- description (string): A detailed description of the company (3-4 sentences) including history, main products/services, and market position

IMPORTANT:
1. Do not truncate any information with "..."
2. Provide complete sentences and full details
3. If information is not available, use null instead of truncating
4. Combine information from multiple search results to create a comprehensive profile
5. Ensure the description includes historical context, current focus, and market position

Example format:
{{
    "name": "Example Corp",
    "mission": "To innovate and lead in technology while creating sustainable solutions for global challenges. Our vision is to be the world's most trusted technology partner.",
    "location": "San Francisco, California, United States",
    "website": "https://example.com",
    "industry": "Technology, Enterprise Software, Cloud Computing",
    "description": "A leading technology company specializing in artificial intelligence and cloud computing solutions. Founded in 2010, the company has grown to become a market leader in enterprise software solutions. With over 10,000 employees worldwide, Example Corp serves Fortune 500 companies across multiple industries, providing innovative solutions that drive digital transformation."
}}

Search Results:
{state['search_results']}

IMPORTANT: Return ONLY the JSON object, nothing else. No additional text or explanation.
"""
    try:
        response = llm.invoke(prompt)
        if not response or not response.content:
            return {**state, "error": "Empty response from LLM"}
            
        try:
            # Clean the response content to ensure it's valid JSON
            content = response.content.strip()
            # Remove any markdown code block indicators if present
            content = content.replace('```json', '').replace('```', '').strip()
            
            structured = json.loads(content)
            required_fields = ['name', 'mission', 'location', 'website', 'industry', 'description']
            missing_fields = [field for field in required_fields if field not in structured]
            
            if missing_fields:
                return {**state, "error": f"Missing required fields: {', '.join(missing_fields)}"}
            
            # Validate that no fields contain truncated text
            for field, value in structured.items():
                if value and isinstance(value, str) and "..." in value:
                    return {**state, "error": f"Field '{field}' contains truncated text"}
                
            return {**state, "structured_data": structured}
        except json.JSONDecodeError as e:
            print(f"Raw LLM response: {content}")  # Debug print
            return {**state, "error": f"Failed to parse LLM response as JSON: {str(e)}"}
            
    except Exception as e:
        return {**state, "error": f"LLM processing failed: {str(e)}"}

def store_node(state: CompanyInfoState) -> CompanyInfoState:
    """Store company information in the database."""
    if state.get("error"):
        return state

    try:
        with db as session:
            # Check if company already exists
            existing_company = session.query(CompanyDB).filter(
                CompanyDB.name == state['structured_data']['name']
            ).first()

            if existing_company:
                # Update existing company
                for key, value in state['structured_data'].items():
                    setattr(existing_company, key, value)
                session.commit()
                session.refresh(existing_company)
            else:
                # Create new company
                company = CompanyDB(**state['structured_data'])
                session.add(company)
                session.commit()
                session.refresh(company)

        return state
    except Exception as e:
        return {**state, "error": f"Database operation failed: {str(e)}"}

def create_company_workflow() -> StateGraph:
    """Create and configure the company information workflow."""
    graph = StateGraph(CompanyInfoState)

    # Add nodes
    graph.add_node("search", search_node)
    graph.add_node("extract", extract_node)
    graph.add_node("store", store_node)

    # Configure workflow
    graph.set_entry_point("search")
    graph.add_edge("search", "extract")
    graph.add_edge("extract", "store")

    return graph.compile()

def search_and_store_company(company_name: str) -> dict:
    """Search for company information and store it in the database."""
    # First check if company exists in database using case-insensitive partial match
    try:
        with db as session:
            # Convert company_name to lowercase for case-insensitive comparison
            search_term = f"%{company_name.lower()}%"
            existing_company = session.query(CompanyDB).filter(
                CompanyDB.name.ilike(search_term)
            ).first()
            
            if existing_company:
                print(f"Company '{company_name}' found in database as '{existing_company.name}'. Returning existing record.")
                return {
                    "name": existing_company.name,
                    "mission": existing_company.mission,
                    "location": existing_company.location,
                    "website": existing_company.website,
                    "industry": existing_company.industry,
                    "description": existing_company.description
                }
    except Exception as e:
        print(f"Warning: Database check failed: {str(e)}")
    
    # If not found in database, proceed with search and store
    print(f"Company '{company_name}' not found in database. Performing search...")
    workflow = create_company_workflow()
    result = workflow.invoke({"company_name": company_name})
    
    if result.get("error"):
        print(f"Error: {result['error']}")
        return None
    
    return result.get("structured_data")

if __name__ == "__main__":
    # Example usage
    company_info = search_and_store_company("Google")
    if company_info:
        print("\nCompany Information:")
        print(f"Name: {company_info.get('name')}")
        print(f"Mission: {company_info.get('mission')}")
        print(f"Location: {company_info.get('location')}")
        print(f"Website: {company_info.get('website')}")
        print(f"Industry: {company_info.get('industry')}")
        print(f"Description: {company_info.get('description')}")


