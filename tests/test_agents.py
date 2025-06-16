"""
Simple test script for the abstracted agents.
Run this from the project root directory.
"""

from dotenv import load_dotenv
from agents import ResumeAgent, RankingAgent, AgentFactory

def test_resume_agent():
    """Test the ResumeAgent with a simple example."""
    print("🚀 Testing ResumeAgent")
    print("-" * 40)
    
    try:
        # Create agent using factory
        agent = AgentFactory.create_agent("resume", temperature=1.0)
        
        # Test with experience ID 5 (as used in the original tests)
        result = agent.generate_bullet_points(experience_id=5)
        
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

def test_ranking_agent():
    """Test the RankingAgent with a simple example."""
    print("\n🏆 Testing RankingAgent")
    print("-" * 40)
    
    try:
        # Create agent using direct instantiation
        agent = RankingAgent(temperature=0.4)
        
        # Test with a sample job URL
        job_url = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Software-Research-Intern--AI-Networking-Team---Fall-2025_JR1998253"
        
        result = agent.rank_experiences(job_url, user_id=1)
        
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
            return False
        
        summary = agent.get_ranking_summary(result)
        print(f"✅ Successfully analyzed {summary['experiences_analyzed']} experiences")
        print(f"Job: {summary['job_title']} at {summary['company']}")
        print(f"Generated {len(summary['rankings'])} rankings")
        
        # Show first ranking as example
        if summary['rankings']:
            print("Sample ranking:")
            print(f"  • {summary['rankings'][0][:100]}...")
        
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
        
        print(f"✅ Created ResumeAgent with temperature: {resume_agent.temperature}")
        print(f"✅ Created RankingAgent with temperature: {ranking_agent.temperature}")
        
        # Test custom parameters
        custom_resume = AgentFactory.create_agent("resume", temperature=1.5)
        custom_ranking = AgentFactory.create_agent("ranking", temperature=0.2)
        
        print(f"✅ Created custom ResumeAgent with temperature: {custom_resume.temperature}")
        print(f"✅ Created custom RankingAgent with temperature: {custom_ranking.temperature}")
        
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
        
        return True
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    """Run all tests."""
    load_dotenv()
    
    print("🧪 Agent Abstraction Tests")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Factory", test_factory()))
    results.append(("Agent Structure", test_agent_structure()))
    results.append(("ResumeAgent", test_resume_agent()))
    results.append(("RankingAgent", test_ranking_agent()))
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:15} {status}")
        if success:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("🎉 All tests passed! The refactored agent abstraction is working correctly.")
    else:
        print("⚠️  Some tests failed. Check your configuration:")
        print("1. Ensure GOOGLE_API_KEY is set in .env")
        print("2. Verify database is accessible")
        print("3. Check that experience data exists")
        print("4. Ensure all service imports are correct")

if __name__ == "__main__":
    main() 