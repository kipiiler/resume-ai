# 🏗️ Architecture Overview

## Agent-Based Design
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  JobAnalysis    │───▶│   Ranking       │───▶│     Resume      │
│     Agent       │    │    Agent        │    │     Agent       │
│                 │    │                 │    │                 │
│ • URL Scraping  │    │ • Experience    │    │ • Bullet Point  │
│ • Skill Extract │    │   Ranking       │    │   Generation    │
│ • DB Caching    │    │ • Project       │    │ • XYZ Format    │
│                 │    │   Ranking       │    │ • Job Context   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack
- **Backend**: Python 3.8+
- **AI/LLM**: Google Gemini (via LangChain)
- **Database**: SQLite with SQLAlchemy ORM
- **Web Scraping**: Custom job posting extractors
- **CLI**: Rich library for enhanced console UI
- **Workflow**: LangGraph for agent orchestration
- **Output**: LaTeX for professional resume formatting

## Database Schema
```sql
Users (id, name, email, education, degree, major, location, ...)
├── Experiences (id, user_id, company_name, role_title, start_date, ...)
├── Projects (id, user_id, project_name, tech_stack, team_size, ...)
└── JobPostings (id, url, company_name, job_title, technical_skills, ...)
```

## Core Components

### 1. Agent Framework (`agents/`)
- **BaseAgent**: Foundation for all AI agents with LangGraph integration
- **DatabaseAgent**: Database access layer with service injection
- **JobAnalysisAgent**: Extracts job requirements and technical skills
- **RankingAgent**: Ranks experiences/projects by relevance
- **ResumeAgent**: Generates XYZ format bullet points

### 2. Database Layer (`model/`)
- **Schema**: SQLAlchemy models for Users, Experiences, Projects, JobPostings
- **Database**: Connection management and initialization
- **Migrations**: Schema versioning and updates

### 3. Service Layer (`services/`)
- **UserService**: User profile management
- **ExperienceService**: Work experience CRUD operations
- **ProjectService**: Project management and retrieval
- **JobPostingService**: Job posting caching and retrieval
- **ResumeWriterService**: LaTeX generation and template management

### 4. Web Scraping (`experiments/job_scraper.py`)
- URL-based job posting extraction
- Support for multiple job sites
- Structured data extraction (title, company, requirements, skills)

## Data Flow

1. **Job URL Input** → JobAnalysisAgent scrapes and analyzes posting
2. **Job Analysis** → RankingAgent ranks user's experiences and projects
3. **Ranking Results** → ResumeAgent generates targeted bullet points
4. **Content Generation** → ResumeWriterService creates LaTeX resume
5. **Output** → Professional PDF resume tailored to job requirements

## File Structure
```
resume-ai/
├── agents/                     # AI agent implementations
│   ├── base_agents.py         # Base agent classes with conditional edges
│   ├── database_agent.py      # Database access layer
│   ├── job_analysis_agent.py  # Job posting analysis
│   ├── ranking_agent.py       # Experience/project ranking
│   └── resume_agent.py        # Bullet point generation
├── model/                     # Database models and schemas
│   ├── database.py           # Database connection and setup
│   └── schema.py             # SQLAlchemy models
├── services/                 # Business logic layer
│   ├── user.py              # User management
│   ├── experience.py        # Experience CRUD operations
│   ├── project.py           # Project CRUD operations
│   ├── job_posting.py       # Job posting management
│   └── resume_writer.py     # LaTeX resume generation
├── experiments/             # Testing and development scripts
├── template/               # Resume templates
└── tests/                 # Test files
``` 