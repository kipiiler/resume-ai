# 🚀 Installation Guide

## Prerequisites
- Python 3.8 or higher
- Google API key for Gemini
- Git (for cloning the repository)

## Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/resume-ai.git
cd resume-ai
```

## Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 4: Set Up Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

## Step 5: Initialize Database
```bash
python -c "from model.database import init_db; init_db()"
```

## Step 6: Configure Personal Information
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

## Verify Installation
```bash
python main.py
```

You should see the main menu interface if everything is installed correctly. 