# 🔧 API Reference

## AgentFactory
```python
from agents import AgentFactory

# Create agents with custom temperature
job_agent = AgentFactory.create_agent("job_analysis", temperature=0.7)
ranking_agent = AgentFactory.create_agent("ranking", temperature=0.4)
resume_agent = AgentFactory.create_agent("resume", temperature=1.0)

# Available agent types
available = AgentFactory.list_available_agents()
# Returns: ["resume", "ranking", "job_analysis"]
```

## Job Analysis Agent

### Basic Usage
```python
from agents.job_analysis_agent import JobAnalysisAgent

agent = JobAnalysisAgent()
result = agent.analyze_job("https://company.com/job-url")
print(result)
```

### Methods
- `analyze_job(url: str) -> Dict[str, Any]`: Analyze job posting from URL
- `get_job_analysis_summary(result: Dict) -> Dict`: Extract summary from analysis result

## Ranking Agent

### Basic Usage
```python
from agents.ranking_agent import RankingAgent

agent = RankingAgent()
result = agent.rank_experiences(job_info, user_id=1)
summary = agent.get_ranking_summary(result)
```

### Methods
- `rank_experiences(job_info: JobInfo, user_id: int) -> Dict`: Rank user experiences
- `rank_projects(job_info: JobInfo, user_id: int) -> Dict`: Rank user projects
- `get_ranking_summary(result: Dict) -> Dict`: Extract ranking summary

## Resume Agent

### Basic Usage
```python
from agents.resume_agent import ResumeAgent

agent = ResumeAgent()
result = agent.generate_bullet_points_for_experience(
    experience_id=5,
    ranking_reason="Strong Python skills match job requirements",
    job_info=job_info
)
```

### Methods
- `generate_bullet_points_for_experience(experience_id: int, ranking_reason: str, job_info: JobInfo) -> Dict`
- `generate_bullet_points_for_project(project_id: int, ranking_reason: str, job_info: JobInfo) -> Dict`
- `generate_multiple_items(items: List[Dict]) -> Dict`: Batch processing

## Service Layer APIs

### UserService
```python
from services.user import UserService

service = UserService()

# Create/update user
user = service.create_user(
    name="John Doe",
    email="john@example.com",
    education="University of Example",
    degree="Bachelor of Science",
    major="Computer Science"
)

# Get user
user = service.get_user(user_id=1)
```

### ExperienceService
```python
from services.experience import ExperienceService

service = ExperienceService()

# Add experience
experience = service.add_experience(
    user_id=1,
    company_name="Google",
    role_title="Software Engineer Intern",
    company_location="Mountain View, CA",
    start_date="2023-06",
    end_date="2023-08",
    short_description="Backend development",
    long_description="Developed microservices...",
    tech_stack=["Go", "Kubernetes"]
)

# Get experience
exp = service.get_experience(experience_id=1)

# List user experiences
experiences = service.get_user_experiences(user_id=1)
```

### ProjectService
```python
from services.project import ProjectService

service = ProjectService()

# Add project
project = service.add_project(
    user_id=1,
    project_name="AI Chatbot",
    start_date="2023-01",
    end_date="2023-05",
    short_description="Conversational AI",
    long_description="Built using transformers...",
    tech_stack=["Python", "PyTorch"],
    team_size=3
)

# Get project
proj = service.get_project(project_id=1)
```

### ResumeWriterService
```python
from services.resume_writer import ResumeWriterService

resume_writer = ResumeWriterService()

# Generate LaTeX resume
resume_writer = ResumeWriter(template_path="template/jake_resume.tex")
resume_writer.write_resume(1, "resume.tex", exp_list, proj_list)
```

## Configuration

### Agent Temperature Settings
```python
# Conservative for logical decisions
ranking_agent = RankingAgent(temperature=0.2)

# Balanced for analysis
job_agent = JobAnalysisAgent(temperature=0.7)

# Creative for content generation
resume_agent = ResumeAgent(temperature=1.0)
``` 