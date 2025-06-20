# 🎮 Usage Guide

## Starting the CLI
```bash
python main.py
```

## Main Menu Options
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

## Complete Workflow Example

### 1. Add Your Background
```bash
# First time setup
python main.py
# Choose: 1. Add Experience
# Choose: 2. Add Project
```

### 2. Generate Targeted Resume
```bash
# Choose: 11. Generate Resume from Job URL
# Enter job URL: https://company.com/job-posting
# Specify number of experiences: 3
# Specify number of projects: 2
```

### 3. Generate LaTeX Resume
The system will automatically offer to generate a LaTeX file, or you can:
```bash
# Choose: 12. List Generated Results
# Select a previous analysis
# Generate LaTeX resume
```

## Command Line Usage (Advanced)
```bash
# Direct script execution
python experiments/workflow_test.py  # Test the complete workflow
python experiments/resume_write.py   # Generate resume from existing results
```

## Adding Data Examples

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

### Example 2: Adding Project
```
Project Name: AI-Powered Chatbot
Start Date: 2023-01
End Date: 2023-05
Short Description: Conversational AI using transformers
Detailed Description: Built a context-aware chatbot using BERT and GPT-2, deployed on AWS with FastAPI
Technologies/Skills: Python, PyTorch, BERT, GPT-2, FastAPI, AWS, Docker
```

## Output Examples

### Job Analysis Output
```
✓ Job analyzed: Full Stack Developer at TechCorp
✓ Ranked 5 experiences and 3 projects
✓ Generated bullet points for top 3 experiences and 2 projects

Files saved:
- data/resume_generation_20240115_143022.log
- data/resume_generation_results_20240115_143022.json
- data/resume_20240115_143022.tex
```

### Generated Bullet Points Example
```
Experience: Software Engineer Intern at Google
1. Optimized search indexing pipeline by implementing Go microservices with Protocol Buffers, which reduced query latency by 25%
2. Developed distributed caching system using Redis and Kubernetes, which improved system throughput by 40%
3. Built automated testing framework with comprehensive unit tests, which decreased bug reports by 60%
```

## File Management

### Generated Files Location
All generated files are saved in the `data/` directory:
- `resume_generation_*.log` - Detailed generation logs
- `resume_generation_results_*.json` - Reusable analysis results
- `resume_*.tex` - Generated LaTeX resumes

### Data Import/Export
```bash
# Export your data
# Choose: 9. Export Data to JSON
# File saved as: data/resume_data_YYYYMMDD_HHMMSS.json

# Import data (useful for backup/restore)
# Choose: 8. Load Data from JSON
# Enter file path: data/resume_data_20240115_143022.json
```