# ⚙️ Configuration Guide

## Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key for AI functionality |

## Template Configuration
Place your LaTeX resume template in `template/jake_resume.tex` or specify a custom path during resume generation.

## Agent Configuration
Customize agent behavior in the code:
```python
# Temperature settings for different creativity levels
job_analysis_agent = AgentFactory.create_agent("job_analysis", temperature=0.7)
ranking_agent = AgentFactory.create_agent("ranking", temperature=0.4)
resume_agent = AgentFactory.create_agent("resume", temperature=1.0)
```

## Personal Information Setup
Update `config.py` with your personal information:

```python
# Personal Links
GITHUB_URL = "https://github.com/yourusername"
GITHUB_SHORT_HANDLE = "yourusername"
LINKEDIN_URL = "https://linkedin.com/in/yourprofile"
LINKEDIN_SHORT_HANDLE = "yourprofile"
PORTFOLIO_URL = "https://yourportfolio.com"  # Optional

# Skills Configuration
LANGUAGE_LIST = [
    "Python", "JavaScript", "Java", "C++", "Go", "Rust", 
    "TypeScript", "SQL", "Shell"
]

TECH_STACK_LIST = [
    "React", "Node.js", "PostgreSQL", "Docker", "Kubernetes", 
    "AWS", "PyTorch", "TensorFlow", "FastAPI", "Django"
]

# Resume Template Settings
DEFAULT_TEMPLATE_PATH = "template/jake_resume.tex"
OUTPUT_DIRECTORY = "data/"
```

## Database Configuration
The system uses SQLite by default. Configuration is handled in `model/database.py`:

```python
# Default database path
DATABASE_URL = "sqlite:///resume_ai.db"

## Model Temperature Settings
Different agents use different creativity levels:

- **Job Analysis Agent** (0.7): Balanced analysis of job requirements
- **Ranking Agent** (0.4): Conservative, logical ranking decisions  
- **Resume Agent** (1.0): Creative bullet point generation

## File Organization
The system automatically creates these directories:
- `data/` - Generated resumes and logs