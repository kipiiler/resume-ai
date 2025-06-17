# 🚀 Resume AI - Intelligent Resume Generation System

A sophisticated AI-powered resume generation system that analyzes job postings, ranks your experiences and projects, and generates tailored bullet points using Large Language Models (LLMs).

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Examples](#examples)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [Future Roadmap](#future-roadmap)
- [License](#license)

## 🎯 Overview

Resume AI is a complete end-to-end system that helps job seekers create highly targeted resumes. The system uses AI agents to:

1. **Analyze job postings** from URLs to extract requirements and technical skills
2. **Rank your experiences and projects** based on relevance to specific jobs
3. **Generate optimized bullet points** using the Google XYZ format
4. **Create LaTeX resumes** with professional formatting

### Key Innovation
Unlike traditional resume builders, Resume AI understands job context and dynamically tailors your resume content to match specific job requirements, significantly improving your chances of getting noticed by recruiters and ATS systems.

## ✨ Features

### 🤖 AI-Powered Workflow
- **Job Analysis Agent**: Extracts job requirements, technical skills, and company information
- **Ranking Agent**: Intelligently ranks your experiences/projects by relevance
- **Resume Agent**: Generates impactful bullet points in XYZ format
- **Conditional Edge Processing**: Smart workflow routing based on database state

### 📊 Data Management
- **SQLite Database**: Stores user profiles, experiences, and projects
- **JSON Import/Export**: Backup and restore your data
- **Database Caching**: Avoids re-scraping previously analyzed jobs
- **Migration Support**: Database schema updates with backward compatibility

### 🎨 Resume Generation
- **LaTeX Output**: Professional, ATS-friendly PDF generation
- **Template System**: Customizable resume templates
- **Skill Extraction**: Automatic technical skill identification
- **Context-Aware Content**: Bullet points tailored to specific job requirements

### 🖥️ User Interface
- **Interactive CLI**: Rich console interface with progress indicators
- **File Organization**: Automatic organization in `data/` directory
- **Result Management**: List, reuse, and manage previous generations
- **Error Handling**: Comprehensive error messages and recovery

## 🏗️ Architecture

### Agent-Based Design
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

### Technology Stack
- **Backend**: Python 3.8+
- **AI/LLM**: Google Gemini (via LangChain)
- **Database**: SQLite with SQLAlchemy ORM
- **Web Scraping**: Custom job posting extractors
- **CLI**: Rich library for enhanced console UI
- **Workflow**: LangGraph for agent orchestration
- **Output**: LaTeX for professional resume formatting

### Database Schema
```sql
Users (id, name, email, education, degree, major, location, ...)
├── Experiences (id, user_id, company_name, role_title, start_date, ...)
├── Projects (id, user_id, project_name, tech_stack, team_size, ...)
└── JobPostings (id, url, company_name, job_title, technical_skills, ...)
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Google API key for Gemini
- Git (for cloning the repository)

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/resume-ai.git
cd resume-ai
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### Step 5: Initialize Database
```bash
python -c "from model.database import init_db; init_db()"
```

### Step 6: Configure Personal Information
Edit `config.py` with your details:
```python
# Personal Links
GITHUB_URL = "https://github.com/yourusername"
GITHUB_SHORT_HANDLE = "yourusername"
LINKEDIN_URL = "https://linkedin.com/in/yourprofile"
LINKEDIN_SHORT_HANDLE = "yourprofile"
PORTFOLIO_URL = "https://yourportfolio.com"  # Optional

# Skills (customize these lists)
LANGUAGE_LIST = ["Python", "JavaScript", "Java", "C++"]
TECH_STACK_LIST = ["React", "Node.js", "PostgreSQL", "Docker"]
```

## ⚙️ Configuration

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Google Gemini API key for AI functionality |

### Template Configuration
Place your LaTeX resume template in `template/jake_resume.tex` or specify a custom path during resume generation.

### Agent Configuration
Customize agent behavior in the code:
```python
# Temperature settings for different creativity levels
job_analysis_agent = AgentFactory.create_agent("job_analysis", temperature=0.7)
ranking_agent = AgentFactory.create_agent("ranking", temperature=0.4)
resume_agent = AgentFactory.create_agent("resume", temperature=1.0)
```

## 🎮 Usage

### Starting the CLI
```bash
python user_manage.py
```

### Main Menu Options
```
1. Add Experience          - Add work experiences
2. Add Project            - Add personal/academic projects  
3. Edit Experience        - Modify existing experiences
4. Edit Project          - Modify existing projects
5. View My Experiences   - Display all experiences
6. View My Projects      - Display all projects
7. View All My Data      - Display complete profile
8. Load Data from JSON   - Import data from file
9. Export Data to JSON   - Export data to file
10. Delete All My Data   - Clear all data (with confirmation)
11. Generate Resume from Job URL  - Main AI workflow
12. List Generated Results - View/reuse previous generations
13. Exit                 - Close application
```

### Complete Workflow Example

#### 1. Add Your Background
```bash
# First time setup
python user_manage.py
# Choose: 1. Add Experience
# Choose: 2. Add Project
```

#### 2. Generate Targeted Resume
```bash
# Choose: 11. Generate Resume from Job URL
# Enter job URL: https://company.com/job-posting
# Specify number of experiences: 3
# Specify number of projects: 2
```

#### 3. Generate LaTeX Resume
The system will automatically offer to generate a LaTeX file, or you can:
```bash
# Choose: 12. List Generated Results
# Select a previous analysis
# Generate LaTeX resume
```

### Command Line Usage (Advanced)
```bash
# Direct script execution
python experiments/workflow_test.py  # Test the complete workflow
python experiments/resume_write.py   # Generate resume from existing results
```

## 📁 File Structure

```
resume-ai/
├── agents/                     # AI agent implementations
│   ├── __init__.py
│   ├── base_agents.py         # Base agent classes with conditional edges
│   ├── database_agent.py      # Database access layer
│   ├── job_analysis_agent.py  # Job posting analysis
│   ├── ranking_agent.py       # Experience/project ranking
│   └── resume_agent.py        # Bullet point generation
├── data/                      # Generated files (auto-created)
│   ├── resume_generation_*.log      # Detailed logs
│   ├── resume_generation_results_*.json  # Reusable results
│   ├── resume_*.tex          # Generated LaTeX resumes
│   └── resume_data_*.json    # Exported user data
├── experiments/              # Testing and development scripts
│   ├── agent_viz.py         # Agent workflow visualization
│   ├── workflow_test.py     # End-to-end workflow testing
│   └── resume_write.py      # LaTeX generation testing
├── model/                   # Database models and schemas
│   ├── __init__.py
│   ├── database.py         # Database connection and setup
│   └── schema.py           # SQLAlchemy models
├── services/               # Business logic layer
│   ├── __init__.py
│   ├── user.py            # User management
│   ├── experience.py      # Experience CRUD operations
│   ├── project.py         # Project CRUD operations
│   ├── job_posting.py     # Job posting management
│   └── resume_writer.py   # LaTeX resume generation
├── template/              # Resume templates
│   └── jake_resume.tex   # Default LaTeX template
├── tests/                # Test files
│   ├── test_agents.py   # Agent functionality tests
│   └── sample_data/     # Test data files
├── .env                 # Environment variables
├── .gitignore          # Git ignore rules
├── config.py           # Personal configuration
├── job_scraper.py      # Web scraping utilities
├── requirements.txt    # Python dependencies
├── user_manage.py      # Main CLI application
└── README.md          # This file
```

## 📚 Examples

### Example 1: Adding Experience
```
Company Name: Google
Role/Position Title: Software Engineer Intern
Company Location: Mountain View, CA
Start Date: 2023-06
End Date: 2023-08
Short Description: Backend development intern
Detailed Description: Developed microservices for search infrastructure using Go and Protocol Buffers
Technologies/Skills: Go, Protocol Buffers, Kubernetes, gRPC
```

### Example 2: Job Analysis Output
```
✓ Job analyzed: Full Stack Developer at TechCorp
✓ Ranked 5 experiences and 3 projects
✓ Generated bullet points for top 3 experiences and 2 projects

Files saved:
- data/resume_generation_20240115_143022.log
- data/resume_generation_results_20240115_143022.json
- data/resume_20240115_143022.tex
```

### Example 3: Generated Bullet Points
```
Experience: Software Engineer Intern at Google
1. Optimized search indexing pipeline by implementing Go microservices with Protocol Buffers, which reduced query latency by 25%
2. Developed distributed caching system using Redis and Kubernetes, which improved system throughput by 40%
3. Built automated testing framework with comprehensive unit tests, which decreased bug reports by 60%
```

## 🔧 API Reference

### AgentFactory
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

### Job Analysis
```python
# Analyze job posting
result = job_agent.analyze_job("https://company.com/job-url")
summary = job_agent.get_job_analysis_summary(result)

# Access extracted information
job_info = summary["job_info_object"]
technical_skills = summary["technical_skills_extracted"]
```

### Experience Ranking
```python
# Rank experiences for a job
result = ranking_agent.rank_experiences(job_info, user_id=1)
summary = ranking_agent.get_ranking_summary(result)

# Get ranked results
ranked_experiences = summary["experience_rankings"]
# Returns: [(exp_id, ranking_reason), ...]
```

### Resume Generation
```python
# Generate bullet points
result = resume_agent.generate_bullet_points_for_experience(
    experience_id=5,
    ranking_reason="Strong Python skills match job requirements",
    job_info=job_info
)

bullet_points = result["bullet_points"]
# Returns: ["Optimized...", "Developed...", "Built..."]
```

## 🤝 Contributing

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/

# Run specific test
python tests/test_agents.py
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings for public methods
- Keep functions focused and small

### Adding New Features
1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Submit pull request** with clear description

### Adding New Job Sites
To add support for new job posting sites:
1. Extend `job_scraper.py` with new extraction logic
2. Add URL pattern matching
3. Test with various job postings from the site
4. Update documentation

## 🎯 Example Showcase

Here's a real example of Resume AI in action, analyzing an NVIDIA Developer Technology Engineer position and generating a tailored resume:

### Input Job Posting
**NVIDIA - Developer Technology Engineer, Public Sector**
- Location: Santa Clara, CA
- Focus: GPU-accelerate applications in federal ecosystem
- Key Requirements: CUDA C/C++, parallel programming, performance optimization

### AI Analysis Results
The system intelligently:
1. **Ranked experiences** by relevance to GPU programming and performance optimization
2. **Selected top projects** demonstrating technical depth and domain relevance  
3. **Generated targeted bullet points** using the XYZ format with quantified impact

### Generated Resume Output

#### Experience Section (AI-Generated Bullet Points)
```latex
\resumeSubheading
    {Software Engineer Intern}{Jun 2024 -- Sep 2024}
    {Visual Concepts}{Seattle, WA}
    \resumeItemListStart
        \resumeItem{Developed CUDA kernels for BVH construction by employing warp-level parallelization, which boosted build times.}
        \resumeItem{Engineered a mesh compression system by implementing custom vector quantization, which decreased 3D model memory usage by 50\%.}
        \resumeItem{Built an OpenGL + CUDA profiling tool for character rendering pipelines, which improved rendering performance analysis in NBA2K.}
    \resumeItemListEnd

\resumeSubheading
    {Research Assistant}{Dec 2024 -- May 2025}
    {Efeslab University of Washington}{Seattle, WA}
    \resumeItemListStart
        \resumeItem{Developed GPU anomaly detection pipelines using CUDA, optimizing for 9.5\% higher F1 scores, showcasing parallel processing proficiency.}
        \resumeItem{Implemented custom DAG schedulers for efficient workload execution on consumer GPUs, enhancing resource utilization and performance.}
        \resumeItem{Utilized Python and vLLM to process 1M+ logs for cloud reliability, demonstrating AI and LLM expertise in a research context.}
    \resumeItemListEnd
```

#### Projects Section (AI-Selected & Optimized)
```latex
\resumeProjectHeading
{\textbf{Lung Cancer Detection} $|$ \emph{Pytorch, Python, OpenCV}}{  }
\resumeItemListStart
        \resumeItem{Developed four U-Net CNN architectures for 3D MRI image segmentation using PyTorch, which achieved 78\% accuracy on validation.}
        \resumeItem{Preprocessed and augmented a dataset of 63 MRI scans using OpenCV to improve generalization, which enhanced model robustness for lung cancer detection.}
        \resumeItem{Iterated on model design and training strategies within a team, which improved outcomes and demonstrated collaborative problem-solving skills for the federal ecosystem.}
    \resumeItemListEnd

\resumeProjectHeading
{\textbf{Bored Game Engine} $|$ \emph{C++, CMake, OpenGL, GLSL, ImGui, LLVM, Computer Graphics}}{  }
\resumeItemListStart
        \resumeItem{Engineered real-time 3D rendering pipeline using OpenGL and GLSL, which improved visual fidelity and demonstrated proficiency in graphics programming.}
        \resumeItem{Designed modular game engine with ECS architecture in C++, which improved code maintainability and enabled future GPU acceleration.}
    \resumeItemListEnd
```

### Key AI Insights

**🎯 Smart Ranking Logic**
- Visual Concepts experience ranked #1 due to direct CUDA/GPU programming alignment
- Research Assistant role ranked #2 for GPU anomaly detection and parallel processing
- Lung Cancer Detection project prioritized for federal ecosystem relevance

**📊 Quantified Impact**
- Every bullet point follows XYZ format: "Accomplished [X] by implementing [Y], which resulted in [Z]"
- Specific metrics: 50% memory reduction, 9.5% F1 score improvement, 1M+ logs processed
- Technical depth: CUDA kernels, warp-level parallelization, custom vector quantization

**🔧 Context Awareness**
- Emphasized "federal ecosystem" relevance for medical imaging project
- Highlighted "parallel processing proficiency" and "GPU acceleration" capabilities
- Tailored technical terminology to match job requirements

### Generated Files
```
data/
├── resume_generation_20250616_233706.log          # Detailed process log
├── resume_generation_results.json                 # Structured analysis results
└── resume.tex                                     # Professional LaTeX output
```

This example demonstrates how Resume AI transforms generic experience descriptions into compelling, job-specific narratives that significantly improve your chances with both ATS systems and human recruiters.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by developers, for developers**

*Star ⭐ this repo if it helped you land your dream job!* 