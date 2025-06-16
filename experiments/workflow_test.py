from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
import threading

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import AgentFactory

JOB_URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Developer-Technology-Engineer--Public-Sector---New-College-Grad-2025_JR1987718?source=jobboardlinkedin"
USER_ID = 1
NUM_EXPERIENCES = 3
NUM_PROJECTS = 3

def run_resume_agent(experience_id, experience_reason, job_info):
    resume_agent = AgentFactory.create_agent("resume", temperature=1.0)
    result = resume_agent.generate_bullet_points_for_experience(experience_id, ranking_reason=experience_reason, job_info=job_info)
    return result

def run_project_agent(project_id, project_reason, job_info):
    resume_agent = AgentFactory.create_agent("resume", temperature=1.0)
    result = resume_agent.generate_bullet_points_for_project(project_id, ranking_reason=project_reason, job_info=job_info)
    return result

def generate_resume():
    job_analysis_agent = AgentFactory.create_agent("job_analysis", temperature=0.7)
    result = job_analysis_agent.analyze_job(JOB_URL)
    job_info = result.get("job_info", {})
    print(job_info)
    ranking_agent = AgentFactory.create_agent("ranking", temperature=0.4)
    result = ranking_agent.rank_both(job_info, USER_ID)
    
    ranked_experiences = result.get("ranked_experiences", [])
    ranked_projects = result.get("ranked_projects", [])

    for i in range(NUM_EXPERIENCES):
        experience_id = ranked_experiences[i][0]
        experience_reason = ranked_experiences[i][1]
        print(f"Experience {i+1}: {experience_id} - {experience_reason}")
    
    for i in range(NUM_PROJECTS):
        project_id = ranked_projects[i][0]
        project_reason = ranked_projects[i][1]
        print(f"Project {i+1}: {project_id} - {project_reason}")

    resume_agent = AgentFactory.create_agent("resume", temperature=1.0)

    experience_results = []
    for i in range(NUM_EXPERIENCES):
        experience_id = ranked_experiences[i][0]
        experience_reason = ranked_experiences[i][1]
        result = resume_agent.generate_bullet_points_for_experience(experience_id, ranking_reason=experience_reason, job_info=job_info)
        experience_results.append(result)
    
    project_results = []
    for i in range(NUM_PROJECTS):
        project_id = ranked_projects[i][0]
        project_reason = ranked_projects[i][1]
        result = resume_agent.generate_bullet_points_for_project(project_id, ranking_reason=project_reason, job_info=job_info)
        project_results.append(result)
    
    print(experience_results)
    print(project_results)

    # Save results to log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"resume_generation_{timestamp}.log"

    with open(log_filename, "w") as f:
        f.write("Resume Generation Results\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("Experience Results:\n")
        f.write("-" * 30 + "\n")
        for i, result in enumerate(experience_results, 1):
            f.write(f"\nExperience {i}:\n")
            f.write(f"ID: {ranked_experiences[i-1][0]}\n")
            f.write(f"Ranking Reason: {ranked_experiences[i-1][1]}\n")
            if isinstance(result, dict):
                if "bullet_points" in result:
                    f.write("Bullet Points:\n")
                    for bullet in result["bullet_points"]:
                        f.write(f"- {bullet}\n")
                if "error" in result and result["error"]:
                    f.write(f"Error: {result['error']}\n")
            f.write("\n")
            
        f.write("\nProject Results:\n")
        f.write("-" * 30 + "\n")
        for i, result in enumerate(project_results, 1):
            f.write(f"\nProject {i}:\n")
            f.write(f"ID: {ranked_projects[i-1][0]}\n")
            f.write(f"Ranking Reason: {ranked_projects[i-1][1]}\n")
            if isinstance(result, dict):
                if "bullet_points" in result:
                    f.write("Bullet Points:\n")
                    for bullet in result["bullet_points"]:
                        f.write(f"- {bullet}\n")
                if "error" in result and result["error"]:
                    f.write(f"Error: {result['error']}\n")
            f.write("\n")
            
    print(f"\nResults saved to {log_filename}")

if __name__ == "__main__":
    generate_resume()