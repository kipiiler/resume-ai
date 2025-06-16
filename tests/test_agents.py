"""
Simple test script for the abstracted agents.
Run this from the project root directory.
"""

import os
import sys

# Add the parent directory to the path to import services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from agents import ResumeAgent, RankingAgent, AgentFactory, JobAnalysisAgent
from job_scraper import JobInfo

TESTING_JOB_URL = "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Developer-Technology-Engineer--Public-Sector---New-College-Grad-2025_JR1987718?source=jobboardlinkedin"

def test_resume_agent():
    """Test the ResumeAgent with a simple example."""
    print("🚀 Testing ResumeAgent - Experience")
    print("-" * 40)
    
    try:
        # Create agent using factory
        agent = AgentFactory.create_agent("resume", temperature=1.0)
        
        # Test with experience ID 5 (as used in the original tests)
        result = agent.generate_bullet_points_for_experience(experience_id=5)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Successfully generated {len(result['bullet_points'])} bullet points")
        print("Generated bullet points:")
        for i, bullet in enumerate(result['bullet_points'], 1):
            print(f"  {i}. {bullet}")
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_resume_agent_project():
    """Test the ResumeAgent with project bullet point generation."""
    print("\n🎯 Testing ResumeAgent - Project")
    print("-" * 40)
    
    try:
        # Create agent using factory
        agent = AgentFactory.create_agent("resume", temperature=1.0)
        
        # Test with project ID 1
        result = agent.generate_bullet_points_for_project(project_id=1)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Successfully generated {len(result['bullet_points'])} project bullet points")
        print("Generated project bullet points:")
        for i, bullet in enumerate(result['bullet_points'], 1):
            print(f"  {i}. {bullet}")
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_resume_agent_with_ranking():
    """Test the ResumeAgent with ranking reason context."""
    print("\n🎯🏆 Testing ResumeAgent - With Ranking Context")
    print("-" * 50)
    
    try:
        # Create agent using factory
        agent = AgentFactory.create_agent("resume", temperature=1.0)
        
        # Test with ranking reason
        ranking_reason = "Good fit because the experience demonstrates strong C++ skills, which is a core requirement. The use of CMake aligns with the job description. While not directly related to networking, the project's focus on modular design, performance tuning, and problem-solving in a complex software environment indicates a solid technical foundation and the ability to learn and adapt to the networking-specific challenges of the role."
        
        # Test experience with ranking context
        result = agent.generate_bullet_points_for_experience(
            experience_id=2, 
            ranking_reason=ranking_reason
        )
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Successfully generated {len(result['bullet_points'])} contextual bullet points")
        print("Generated bullet points with ranking context:")
        for i, bullet in enumerate(result['bullet_points'], 1):
            print(f"  {i}. {bullet}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_resume_agent_generic():
    """Test the generic generate_bullet_points method."""
    print("\n🔧 Testing ResumeAgent - Generic Method")
    print("-" * 45)
    
    try:
        agent = AgentFactory.create_agent("resume", temperature=1.0)
        
        # Test generic method with experience
        exp_result = agent.generate_bullet_points(item_id=5, item_type="experience")
        
        if exp_result.get("error"):
            print(f"❌ Experience Error: {exp_result['error']}")
            return False
        
        print(f"✅ Generic method - Experience: {len(exp_result['bullet_points'])} bullet points")
        
        # Test generic method with project
        proj_result = agent.generate_bullet_points(item_id=1, item_type="project")
        
        if proj_result.get("error"):
            print(f"❌ Project Error: {proj_result['error']}")
            return False
        
        print(f"✅ Generic method - Project: {len(proj_result['bullet_points'])} bullet points")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_ranking_agent_experiences():
    """Test the RankingAgent experience ranking functionality."""
    print("\n🏆 Testing RankingAgent - Experience Ranking")
    print("-" * 50)
    
    try:
        # Create agent using direct instantiation
        agent = RankingAgent(temperature=0.4)
        
        # Test with a sample job URL
        job_url = TESTING_JOB_URL
        
        result = agent.rank_experiences_from_url(job_url, user_id=1)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        summary = agent.get_ranking_summary(result)
        print(f"✅ Successfully analyzed {summary['experiences_analyzed']} experiences")
        print(f"Job: {summary['job_title']} at {summary['company']}")
        print(f"Generated {len(summary.get('experience_rankings', []))} experience rankings")
        
        # Show first ranking as example
        if summary.get('experience_rankings'):
            print("Sample experience ranking:")
            first_ranking = summary['experience_rankings'][0]
            if isinstance(first_ranking, tuple) and len(first_ranking) >= 2:
                exp_id, reason = first_ranking
                print(f"  • Experience {exp_id}: {reason[:100]}...")
            else:
                print(f"  • {str(first_ranking)[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_ranking_agent_projects():
    """Test the RankingAgent project ranking functionality."""
    print("\n🎯 Testing RankingAgent - Project Ranking")
    print("-" * 50)
    
    try:
        # Create agent using direct instantiation
        agent = RankingAgent(temperature=0.4)
        
        # Test with a sample job URL
        job_url = TESTING_JOB_URL
        
        result = agent.rank_projects_from_url(job_url, user_id=1)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        summary = agent.get_ranking_summary(result)
        print(f"✅ Successfully analyzed {summary['projects_analyzed']} projects")
        print(f"Job: {summary['job_title']} at {summary['company']}")
        print(f"Generated {len(summary.get('project_rankings', []))} project rankings")
        
        # Show first ranking as example
        if summary.get('project_rankings'):
            print("Sample project ranking:")
            first_ranking = summary['project_rankings'][0]
            if isinstance(first_ranking, tuple) and len(first_ranking) >= 2:
                proj_id, reason = first_ranking
                print(f"  • Project {proj_id}: {reason[:100]}...")
            else:
                print(f"  • {str(first_ranking)[:100]}...")
        
        # Show skill match info if available
        if summary.get('project_skill_matches'):
            print("Project skill matches:")
            for match in summary['project_skill_matches'][:2]:  # Show first 2
                print(f"  • {match['project_name']}: {match['match_percentage']:.1f}% match")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_ranking_agent_both():
    """Test the RankingAgent ranking both experiences and projects."""
    print("\n🎯🏆 Testing RankingAgent - Both Experiences & Projects")
    print("-" * 60)
    
    try:
        # Create agent using direct instantiation
        agent = RankingAgent(temperature=0.4)
        
        # Test with a sample job URL
        job_url = TESTING_JOB_URL
        
        result = agent.rank_both_from_url(job_url, user_id=1)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        summary = agent.get_ranking_summary(result)
        print(f"✅ Successfully analyzed {summary['experiences_analyzed']} experiences and {summary['projects_analyzed']} projects")
        print(f"Job: {summary['job_title']} at {summary['company']}")
        
        # Show experience rankings
        exp_rankings = summary.get('experience_rankings', [])
        proj_rankings = summary.get('project_rankings', [])
        
        print(f"Generated {len(exp_rankings)} experience rankings and {len(proj_rankings)} project rankings")
        
        if exp_rankings:
            print("Top experience ranking:")
            first_exp = exp_rankings[0]
            if isinstance(first_exp, tuple) and len(first_exp) >= 2:
                exp_id, reason = first_exp
                print(f"  • Experience {exp_id}: {reason}...")
            else:
                print(f"  • {str(first_exp)}...")
        
        if proj_rankings:
            print("Top project ranking:")
            first_proj = proj_rankings[0]
            if isinstance(first_proj, tuple) and len(first_proj) >= 2:
                proj_id, reason = first_proj
                print(f"  • Project {proj_id}: {reason}...")
            else:
                print(f"  • {str(first_proj)}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_job_analysis_agent():
    """Test the JobAnalysisAgent standalone functionality."""
    print("\n🔍 Testing JobAnalysisAgent - Standalone Job Analysis")
    print("-" * 55)
    
    try:
        # Create agent using factory
        agent = AgentFactory.create_agent("job_analysis", temperature=0.7)
        
        # Test with a sample job URL
        job_url = TESTING_JOB_URL
        
        result = agent.analyze_job(job_url)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        summary = agent.get_job_analysis_summary(result)
        
        if summary.get("error"):
            print(f"❌ Summary Error: {summary['error']}")
            return False
        
        print(f"✅ Successfully analyzed job posting!")
        print(f"   Company: {summary['company_name']}")
        print(f"   Position: {summary['job_title']}")
        print(f"   Location: {summary['location']}")
        print(f"   Job Type: {summary['job_type']}")
        print(f"   Technical Skills Found: {len(summary['technical_skills_extracted'])}")
        print(f"   Total Qualifications: {summary['total_qualifications']}")
        
        # Verify JobInfo object is returned
        job_info = summary['job_info_object']
        if job_info and hasattr(job_info, 'company_name'):
            print(f"✅ JobInfo object properly created and accessible")
        else:
            print(f"❌ JobInfo object creation failed")
            return False
        
        # Show some technical skills
        if summary['technical_skills_extracted']:
            print(f"   Sample skills: {', '.join(summary['technical_skills_extracted'][:5])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_factory():
    """Test the AgentFactory."""
    print("\n🏭 Testing AgentFactory")
    print("-" * 40)
    
    try:
        # Test available agents
        available = AgentFactory.list_available_agents()
        print(f"✅ Available agents: {', '.join(available)}")
        
        # Test creating agents using new factory method
        resume_agent = AgentFactory.create_agent("resume")
        ranking_agent = AgentFactory.create_agent("ranking")
        job_analysis_agent = AgentFactory.create_agent("job_analysis")
        
        print(f"✅ Created ResumeAgent with temperature: {resume_agent.temperature}")
        print(f"✅ Created RankingAgent with temperature: {ranking_agent.temperature}")
        print(f"✅ Created JobAnalysisAgent with temperature: {job_analysis_agent.temperature}")
        
        # Test custom parameters
        custom_resume = AgentFactory.create_agent("resume", temperature=1.5)
        custom_ranking = AgentFactory.create_agent("ranking", temperature=0.2)
        custom_job_analysis = AgentFactory.create_agent("job_analysis", temperature=0.5)
        
        print(f"✅ Created custom ResumeAgent with temperature: {custom_resume.temperature}")
        print(f"✅ Created custom RankingAgent with temperature: {custom_ranking.temperature}")
        print(f"✅ Created custom JobAnalysisAgent with temperature: {custom_job_analysis.temperature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_agent_structure():
    """Test that agents have the expected structure after refactoring."""
    print("\n🔧 Testing Agent Structure")
    print("-" * 40)
    
    try:
        # Test direct instantiation
        resume_agent = ResumeAgent()
        ranking_agent = RankingAgent()
        
        # Check that agents have required methods
        required_methods = ['create_nodes', 'define_edges', 'get_entry_point', 'get_state_class', 'run']
        
        for agent, name in [(resume_agent, "ResumeAgent"), (ranking_agent, "RankingAgent")]:
            for method in required_methods:
                if not hasattr(agent, method):
                    print(f"❌ {name} missing method: {method}")
                    return False
            print(f"✅ {name} has all required methods")
        
        # Check that graphs are built automatically
        if resume_agent.graph is None:
            print("❌ ResumeAgent graph not built")
            return False
        print("✅ ResumeAgent graph built successfully")
        
        if ranking_agent.graph is None:
            print("❌ RankingAgent graph not built")
            return False
        print("✅ RankingAgent graph built successfully")
        
        # Test graph visualization
        resume_viz = resume_agent.get_graph_visualization()
        ranking_viz = ranking_agent.get_graph_visualization()
        
        print("✅ Graph visualization working")
        print(f"ResumeAgent nodes: {len(resume_agent.create_nodes())}")
        print(f"RankingAgent nodes: {len(ranking_agent.create_nodes())}")
        
        # Test new ranking agent methods
        ranking_methods = ['rank_experiences', 'rank_projects', 'rank_both', 'query_all_user_projects']
        for method in ranking_methods:
            if not hasattr(ranking_agent, method):
                print(f"❌ RankingAgent missing new method: {method}")
                return False
        print("✅ RankingAgent has all new project ranking methods")
        
        # Test new resume agent methods
        resume_methods = ['generate_bullet_points_for_experience', 'generate_bullet_points_for_project', 'query_project_from_db']
        for method in resume_methods:
            if not hasattr(resume_agent, method):
                print(f"❌ ResumeAgent missing new method: {method}")
                return False
        print("✅ ResumeAgent has all new project methods")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_ranking_agent_methods():
    """Test that RankingAgent has all the expected ranking methods."""
    print("\n🧪 Testing RankingAgent Methods")
    print("-" * 40)
    
    try:
        agent = RankingAgent()
        
        # Test that all ranking methods exist
        methods_to_test = [
            ('rank_experiences', 'Rank experiences only'),
            ('rank_projects', 'Rank projects only'),
            ('rank_both', 'Rank both experiences and projects'),
            ('query_all_user_experiences', 'Query user experiences'),
            ('query_all_user_projects', 'Query user projects'),
            ('get_ranking_summary', 'Get ranking summary')
        ]
        
        for method_name, description in methods_to_test:
            if hasattr(agent, method_name):
                print(f"✅ {method_name}: {description}")
            else:
                print(f"❌ Missing method: {method_name}")
                return False
        
        # Test that the state class includes project fields
        state_class = agent.get_state_class()
        state_annotations = getattr(state_class, '__annotations__', {})
        
        required_fields = ['project_list', 'project_skills_analysis', 'ranked_projects', 'ranking_type']
        for field in required_fields:
            if field in state_annotations:
                print(f"✅ State has field: {field}")
            else:
                print(f"❌ Missing state field: {field}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_resume_agent_with_job_info():
    """Test the ResumeAgent with JobInfo context."""
    print("\n🎯 Testing ResumeAgent - With JobInfo Context")
    print("-" * 50)
    
    try:
        # Create agent using factory
        agent = AgentFactory.create_agent("resume", temperature=1.0)
        
        # Create a sample JobInfo object
        job_info = JobInfo(
            company_name="NVIDIA",
            job_title="Software Research Intern - AI Networking Team",
            location="Santa Clara, CA",
            job_type="Internship", 
            description="We are looking for a passionate and talented Software Research Intern to join our AI Networking team. You will work on cutting-edge networking technologies, develop high-performance software solutions, and contribute to research in AI-accelerated networking systems. The role involves working with C++, Python, CUDA, and various networking protocols.",
            qualifications=[
                "Strong programming skills in C++ and Python",
                "Experience with networking protocols and systems", 
                "Knowledge of CUDA programming and GPU computing",
                "Understanding of machine learning and AI concepts",
                "Experience with distributed systems and high-performance computing"
            ]
        )
        
        # Test experience with job context
        result = agent.generate_bullet_points_for_experience(
            experience_id=5,
            job_info=job_info
        )
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Successfully generated {len(result['bullet_points'])} bullet points with job context")
        print("Generated bullet points with JobInfo:")
        for i, bullet in enumerate(result['bullet_points'], 1):
            print(f"  {i}. {bullet}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_decoupled_job_analysis_and_ranking():
    """Test the decoupled workflow: JobAnalysisAgent → RankingAgent."""
    print("\n🔗 Testing Decoupled Job Analysis + Ranking Workflow")
    print("-" * 60)
    
    try:
        # Step 1: Use JobAnalysisAgent to parse job URL into JobInfo
        print("Step 1: Analyzing job posting...")
        job_analysis_agent = AgentFactory.create_agent("job_analysis", temperature=0.7)
        
        job_url = TESTING_JOB_URL
        
        job_analysis_result = job_analysis_agent.analyze_job(job_url)
        
        if job_analysis_result.get("error"):
            print(f"❌ Job analysis error: {job_analysis_result['error']}")
            return False
        
        job_analysis_summary = job_analysis_agent.get_job_analysis_summary(job_analysis_result)
        job_info = job_analysis_summary["job_info_object"]
        
        print(f"✅ Job analysis complete!")
        print(f"   Company: {job_analysis_summary['company_name']}")
        print(f"   Position: {job_analysis_summary['job_title']}")
        print(f"   Technical skills found: {len(job_analysis_summary['technical_skills_extracted'])}")
        
        # Step 2: Use RankingAgent with the JobInfo object
        print("\nStep 2: Ranking experiences with job context...")
        ranking_agent = AgentFactory.create_agent("ranking", temperature=0.4)
        
        ranking_result = ranking_agent.rank_experiences(job_info, user_id=1)
        
        if ranking_result.get("error"):
            print(f"❌ Ranking error: {ranking_result['error']}")
            return False
        
        ranking_summary = ranking_agent.get_ranking_summary(ranking_result)
        
        print(f"✅ Experience ranking complete!")
        print(f"   Experiences analyzed: {ranking_summary['experiences_analyzed']}")
        print(f"   Rankings generated: {len(ranking_summary['experience_rankings'])}")
        
        # Show sample ranking
        if ranking_summary['experience_rankings']:
            first_ranking = ranking_summary['experience_rankings'][0]
            if isinstance(first_ranking, tuple) and len(first_ranking) >= 2:
                exp_id, reason = first_ranking
                print(f"   Top match: Experience {exp_id}")
                print(f"   Reason: {reason[:100]}...")
        
        # Step 3: Demonstrate the decoupling benefit - reuse JobInfo
        print("\nStep 3: Reusing JobInfo for project ranking...")
        project_ranking_result = ranking_agent.rank_projects(job_info, user_id=1)
        
        if project_ranking_result.get("error"):
            print(f"❌ Project ranking error: {project_ranking_result['error']}")
            return False
        
        project_summary = ranking_agent.get_ranking_summary(project_ranking_result)
        print(f"✅ Project ranking complete using same JobInfo!")
        print(f"   Projects analyzed: {project_summary['projects_analyzed']}")
        print(f"   Rankings generated: {len(project_summary['project_rankings'])}")
        
        print("\n🎉 Decoupled workflow successful! JobAnalysisAgent → RankingAgent")
        print("   Benefits: Job analysis can be cached and reused across multiple ranking operations")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run all tests."""
    load_dotenv()
    
    print("🧪 Agent Abstraction Tests - Decoupled Architecture with Project Support")
    print("=" * 75)
    
    results = []
    
    # Core Infrastructure Tests
    print("\n📋 Core Infrastructure Tests")
    print("-" * 40)
    results.append(("Factory", test_factory()))
    results.append(("Agent Structure", test_agent_structure()))
    results.append(("RankingAgent Methods", test_ranking_agent_methods()))
    
    # Individual Agent Tests
    print("\n🤖 Individual Agent Tests")
    print("-" * 40)
    results.append(("JobAnalysisAgent", test_job_analysis_agent()))
    results.append(("ResumeAgent - Basic", test_resume_agent()))
    results.append(("ResumeAgent - Project", test_resume_agent_project()))
    results.append(("ResumeAgent - With Ranking", test_resume_agent_with_ranking()))
    results.append(("ResumeAgent - Generic Method", test_resume_agent_generic()))
    results.append(("ResumeAgent - With JobInfo", test_resume_agent_with_job_info()))
    
    # Ranking Agent Tests (Backward Compatibility)
    print("\n🏆 Ranking Agent Tests (Backward Compatibility)")
    print("-" * 55)
    results.append(("RankingAgent - Experiences", test_ranking_agent_experiences()))
    results.append(("RankingAgent - Projects", test_ranking_agent_projects()))
    results.append(("RankingAgent - Both", test_ranking_agent_both()))
    
    # Integration & Workflow Tests
    print("\n🔗 Integration & Workflow Tests")
    print("-" * 40)
    results.append(("Decoupled Job Analysis → Ranking", test_decoupled_job_analysis_and_ranking()))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 75)
    
    passed = 0
    failed_tests = []
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:35} {status}")
        if success:
            passed += 1
        else:
            failed_tests.append(test_name)
    
    print(f"\nOverall Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The decoupled agent architecture is working correctly.")
        print("✨ Key features verified:")
        print("   • Standalone JobAnalysisAgent for parsing job URLs → JobInfo")
        print("   • Decoupled RankingAgent accepting JobInfo objects")
        print("   • Enhanced ResumeAgent with JobInfo context")
        print("   • Backward compatibility for URL-based ranking methods")
        print("   • Full project support across all agents")
    else:
        print(f"\n⚠️  {len(failed_tests)} test(s) failed. Check your configuration:")
        print("   Failed tests:", ", ".join(failed_tests))
        print("\nTroubleshooting checklist:")
        print("1. Ensure GOOGLE_API_KEY is set in .env")
        print("2. Verify database is accessible")
        print("3. Check that experience and project data exists")
        print("4. Ensure all service imports are correct")
        print("5. Verify web scraping functionality works")
        print("6. Check JobInfo object creation and serialization")

if __name__ == "__main__":
    main() 