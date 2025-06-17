# 🤝 Contributing Guide

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- Google API key for Gemini

### Installation for Development
```bash
# Clone the repository
git clone https://github.com/yourusername/resume-ai.git
cd resume-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from model.database import init_db; init_db()"
```

### Running Tests
```bash
# Run specific test file
python tests/test_agents.py
```

### Pull Request Process

#### 1. Before Starting
- Check existing issues and PRs to avoid duplication

#### 2. Development Process
```bash
# Create feature branch
git checkout -b feature/amazing-feature

# Make changes with clear, atomic commits
git add .
git commit -m "Add amazing feature

- Implemented core functionality
- Added comprehensive tests
- Updated documentation"

# Push to your fork
git push origin feature/amazing-feature
```

#### 3. Pull Request Requirements
- **Clear Title**: Descriptive title summarizing the change
- **Description**: Explain what, why, and how
- **Tests**: Include tests for new functionality
- **Documentation**: Update relevant documentation