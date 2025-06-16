"""
Example usage of the abstracted agents.

This file demonstrates how to use the ResumeAgent and RankingAgent
through the clean abstraction layer.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path to import agents
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agents import AgentFactory
from agents.resume_agent import ResumeAgent
from agents.ranking_agent import RankingAgent

def example_resume_agent():
    """Example of using the ResumeAgent."""
    print("🚀 Resume Agent Example")
    print("=" * 50)
    
    # Method 1: Using the factory
    resume_agent = AgentFactory.create_resume_agent(temperature=1.0)
    
    # Method 2: Direct instantiation
    # resume_agent = ResumeAgent(temperature=1.0)
    
    # Generate bullet points for a specific experience
    experience_id = 5
    result = resume_agent.generate_bullet_points(experience_id)
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return
    
    print(f"Experience ID: {experience_id}")
    print(f"Experience: {result['experience'][:200]}...")
    print(f"\nGenerated Bullet Points:")
    for i, bullet in enumerate(result['bullet_points'], 1):
        print(f"  {i}. {bullet}")
    
    # Generate for multiple experiences
    print(f"\n" + "=" * 50)
    print("Multiple Experiences Example:")
    
    multiple_results = resume_agent.generate_multiple_experiences([1, 2, 3])
    for exp_id, result in multiple_results.items():
        if result.get("error"):
            print(f"Experience {exp_id}: Error - {result['error']}")
        else:
            print(f"Experience {exp_id}: Generated {len(result['bullet_points'])} bullet points")

def example_ranking_agent():
    """Example of using the RankingAgent."""
    print("\n🏆 Ranking Agent Example")
    print("=" * 50)
    
    # Method 1: Using the factory
    ranking_agent = AgentFactory.create_ranking_agent(temperature=0.4)
    
    # Method 2: Direct instantiation
    # ranking_agent = RankingAgent(temperature=0.4)
    
    # Example job posting URL
    job_url = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Software-Research-Intern--AI-Networking-Team---Fall-2025_JR1998253"
    user_id = 1
    
    print(f"Job URL: {job_url}")
    print(f"User ID: {user_id}")
    
    # Rank experiences
    result = ranking_agent.rank_experiences(job_url, user_id)
    
    if result.get("error"):
        print(f"❌ Error: {result['error']}")
        return
    
    # Get summary
    summary = ranking_agent.get_ranking_summary(result)
    
    print(f"\n✅ Job Analysis Complete:")
    print(f"Position: {summary['job_title']} at {summary['company']}")
    print(f"Technical Skills Required: {', '.join(summary['technical_skills_required'][:5])}...")
    print(f"Experiences Analyzed: {summary['experiences_analyzed']}")
    
    if 'skill_matches' in summary:
        print(f"\n🎯 Skill Match Summary:")
        for match in summary['skill_matches']:
            print(f"  {match['company']}: {match['match_percentage']}% match "
                  f"({match['direct_matches']} direct, {match['related_matches']} related)")
    
    print(f"\n🏆 Final Rankings:")
    for i, ranking in enumerate(summary['rankings'], 1):
        print(f"  {i}. {ranking}")

def example_custom_configuration():
    """Example of using agents with custom configurations."""
    print("\n⚙️ Custom Configuration Example")
    print("=" * 50)
    
    # Create agents with custom settings
    creative_resume_agent = ResumeAgent(
        model_name="gemini-2.0-flash-lite",
        temperature=1.2  # More creative
    )
    
    conservative_ranking_agent = RankingAgent(
        model_name="gemini-2.0-flash-lite", 
        temperature=0.1  # More conservative/consistent
    )
    
    print("Created agents with custom configurations:")
    print(f"Resume Agent - Temperature: {creative_resume_agent.temperature}")
    print(f"Ranking Agent - Temperature: {conservative_ranking_agent.temperature}")
    
    # You can use these agents the same way as the default ones
    # result = creative_resume_agent.generate_bullet_points(1)
    # ranking = conservative_ranking_agent.rank_experiences(job_url, 1)

def example_error_handling():
    """Example of proper error handling with agents."""
    print("\n🛡️ Error Handling Example")
    print("=" * 50)
    
    resume_agent = ResumeAgent()
    
    # Try with a non-existent experience ID
    result = resume_agent.generate_bullet_points(999999)
    
    if result.get("error"):
        print(f"✅ Properly handled error: {result['error']}")
    else:
        print("Unexpected success - this should have failed")
    
    # Try ranking with invalid URL
    ranking_agent = RankingAgent()
    result = ranking_agent.rank_experiences("invalid-url", 1)
    
    if result.get("error"):
        print(f"✅ Properly handled error: {result['error']}")
    else:
        print("Unexpected success - this should have failed")

def main():
    """Main function to run all examples."""
    load_dotenv()
    
    print("🎯 Agent Abstraction Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_resume_agent()
        example_ranking_agent()
        example_custom_configuration()
        example_error_handling()
        
        print(f"\n✅ All examples completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure you have:")
        print("1. Set up your GOOGLE_API_KEY in .env file")
        print("2. Have the database and services properly configured")
        print("3. Have valid experience data in your database")

if __name__ == "__main__":
    main() 