from agents.resume_agent import ResumeAgent
from agents.ranking_agent import RankingAgent
from agents.job_analysis_agent import JobAnalysisAgent
from agents import AgentFactory

JOB_URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Developer-Technology-Engineer--Public-Sector---New-College-Grad-2025_JR1987718?source=jobboardlinkedin"
USER_ID = 1

def generate_resume():
    job_analysis_agent = AgentFactory.create_agent("job_analysis")
    job_info = job_analysis_agent.analyze_job(JOB_URL)
    ranking_agent = AgentFactory.create_agent("ranking")

if __name__ == "__main__":
    generate_resume()