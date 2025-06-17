from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv
import json
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup
import re

# Load environment variables
load_dotenv()

# Get API key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

# Define the job information model
class JobInfo(BaseModel):
    company_name: str = Field(description="The name of the company")
    job_title: str = Field(description="The title of the position")
    location: str = Field(description="The job location")
    job_type: str = Field(description="The type of employment (e.g., Full-time, Internship)")
    description: str = Field(description="The job description")
    qualifications: list[str] = Field(description="List of required qualifications and requirements, each as a separate string")

def setup_driver():
    """Set up and return a configured Chrome WebDriver."""
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")  # Updated headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--log-level=3")  # Suppress logging
        
        # Use webdriver_manager to handle driver installation
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)  # Set page load timeout
        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        raise

def has_text_content(element):
    """Check if an element or its children contain any text content."""
    # Get all text from the element and its children
    text = element.get_text(strip=True)
    # Check if there's any non-whitespace text
    return bool(text and not text.isspace())

def clean_html(html_content):
    """Extract only text content from HTML, removing all tags and cleaning up whitespace."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for element in soup.find_all(['script', 'style']):
        element.decompose()
    
    # Get text content
    text = soup.get_text(separator='\n', strip=True)
    
    # Clean up whitespace
    # Remove multiple newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    # Remove leading/trailing whitespace from each line
    text = '\n'.join(line.strip() for line in text.split('\n'))
    # Remove empty lines
    text = '\n'.join(line for line in text.split('\n') if line.strip())
    
    return text

def clean_json_response(response_text):
    """Clean the LLM response to ensure it's valid JSON."""
    # Remove markdown code block indicators if present
    response_text = response_text.replace('```json', '').replace('```', '').strip()
    return response_text

def extract_job_info(url):
    """Extract job information from the given URL."""
    driver = None
    try:
        driver = setup_driver()
        
        # Load the page
        print("Loading page...")
        driver.get(url)
        
        # Wait for page to load and JavaScript to execute
        print("Waiting for page to load...")
        time.sleep(5)  # Give time for dynamic content to load
        
        # Get the root div content
        print("Extracting content...")
        root_div = driver.find_element(By.TAG_NAME, "body")
        page_content = root_div.get_attribute('innerHTML')
        
        # Clean the HTML content
        cleaned_content = clean_html(page_content)
        print("Raw content extracted. Processing with LLM...")
        
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            temperature=0,
            google_api_key=GOOGLE_API_KEY
        )
        
        # Set up the output parser
        parser = PydanticOutputParser(pydantic_object=JobInfo)
        
        # Create the prompt template
        prompt = PromptTemplate(
            template="""
            Given the following text content from a job listing page, extract the job information.
            
            {format_instructions}
            
            Text Content:
            {text_content}

            For description:
            1. Extract the description of the job
            2. Make sure to include the key responsibilities for the job as well
            
            For qualifications:
            1. Extract each qualification as a separate item in the list
            2. Include both required and preferred qualifications
            3. Each qualification should be a complete, standalone statement
            4. Include qualifications from sections like "Requirements", "Qualifications", "Nice to Have", etc.
            5. Make sure each qualification is clear and specific
            """,
            input_variables=["text_content"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Format the prompt
        formatted_prompt = prompt.format(text_content=cleaned_content)
        
        # Get structured response from LLM
        print("Processing with LLM...")
        response = llm.invoke(formatted_prompt)
        
        # Parse the response
        try:
            job_info = parser.parse(response.content)
            return job_info.dict()
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            print("Raw response:", response.content)
            return None
            
    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        return None
    finally:
        if driver:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error closing driver: {e}")

if __name__ == "__main__":
    url = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Software-Research-Intern--AI-Networking-Team---Fall-2025_JR1998253?jobFamilyGroup=0c40f6bd1d8f10ae43ffda1e8d447e94&locationHierarchy1=2fcb99c455831013ea52fb338f2932d8"
    print("Starting job scraping...")
    job_info = extract_job_info(url)
    print(job_info)
    
    if job_info:
        print("\nJob Information:")
        print(f"Company: {job_info.get('company_name')}")
        print(f"Title: {job_info.get('job_title')}")
        print(f"Location: {job_info.get('location')}")
        print(f"Type: {job_info.get('job_type')}")
        print("\nDescription:")
        print(job_info.get('description'))
        print("\nQualifications:")
        print(job_info.get('qualifications'))
    else:
        print("Failed to extract job information.") 