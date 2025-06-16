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


    experience_results = []
    for i in range(NUM_EXPERIENCES):
        # Create threads for each experience
        experience_threads = []
        for i in range(NUM_EXPERIENCES):
            experience_id = ranked_experiences[i][0]
            experience_reason = ranked_experiences[i][1]
            thread = threading.Thread(
                target=run_resume_agent,
                args=(experience_id, experience_reason, job_info)
            )
            experience_threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in experience_threads:
            result = thread.join()
            experience_results.append(result)
    
    project_results = []
    for i in range(NUM_PROJECTS):
        project_id = ranked_projects[i][0]
        project_reason = ranked_projects[i][1]
        print(f"Project {i+1}: {project_id} - {project_reason}")
        project_threads = []
        for i in range(NUM_PROJECTS):
            project_id = ranked_projects[i][0]
            project_reason = ranked_projects[i][1]
            thread = threading.Thread(
                target=run_project_agent,
                args=(project_id, project_reason, job_info)
            )
            project_threads.append(thread)
            thread.start()
        for thread in project_threads:
            result = thread.join()
            project_results.append(result)

    

if __name__ == "__main__":
    generate_resume()