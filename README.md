> 👍 **Note**  
> This system is experimental. Use responsibly and always review generated content.

# 🚀 Resume tailoring AI

A automatic resume customized system that analyzes job postings, ranks your experiences and projects, and generates tailored bullet points using LLMs.

## ✨ What Resume AI Does

1. **📊 Analyzes Job Postings** - Extracts requirements and technical skills from URLs
2. **🎯 Ranks Your Background** -  Ranks experiences/projects by relevance  
3. **📝 Generates Bullet Points** - Creates impactful content using Google's XYZ format
4. **📄 Creates LaTeX Resumes** - Outputs professional, ATS-friendly PDFs (Jake Resume)

## Example Showcase

See directory `/sample_generated`. Two difference version of resume tailored for NVIDIA and Splunk from the same content `sample_resume_data.json`

## 🚀 Quick Start

```bash
# 1. Install
git clone https://github.com/yourusername/resume-ai.git
cd resume-ai
pip install -r requirements.txt

# 2. Configure
echo "GOOGLE_API_KEY=your_key_here" > .env
python -c "from model.database import init_db; init_db()"

# 3. Run
python main.py
```

## 📋 Workflow

1. **Add your background** (experiences, projects, skills)
2. **Paste a job URL** from any major job site
3. **AI analyzes and ranks** your most relevant content  
4. **Generate LaTeX resume** tailored to that specific job
5. **Compile to PDF** and apply with confidence

## 📚 Documentation

- **[🚀 Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[⚙️ Configuration](docs/configuration.md)** - Customization options  
- **[🎮 Usage Guide](docs/usage.md)** - Complete workflow examples
- **[🏗️ Architecture](docs/architecture.md)** - Technical deep dive
- **[🔧 API Reference](docs/api-reference.md)** - Developer documentation
- **[🤝 Contributing](docs/contributing.md)** - Development guidelines

## 🔧 Requirements

- Python 3.8+
- Google Gemini API key  
- LaTeX (for PDF generation)

## 🤝 Contributing

We welcome contributions! Check out our [Contributing Guide](docs/contributing.md) for development setup, coding standards, and pull request guidelines.

---

⭐ **Star this repo** if this project helped you land interviews!  
