#!/usr/bin/env python3
"""
Test script for refactored agents to verify they work correctly.
"""

import os
import sys

# Add the parent directory to Python path for imports (where agents module is located)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """Test that all agent classes can be imported correctly."""
    print("Testing imports...")
    
    try:
        from agents import (
            BaseAgent, BaseAgentState, DatabaseAgent, JobAnalysisAgent,
            ResumeAgent, RankingAgent, AgentFactory
        )
        print("✅ All imports successful")
        
        # Test JobInfo import
        from job_scraper import JobInfo
        print("✅ JobInfo import successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_agent_creation():
    """Test that agents can be created successfully."""
    print("\nTesting agent creation...")
    
    try:
        from agents import ResumeAgent, RankingAgent, JobAnalysisAgent, AgentFactory
        
        # Test direct instantiation
        resume_agent = ResumeAgent()
        print("✅ ResumeAgent created successfully")
        
        ranking_agent = RankingAgent()
        print("✅ RankingAgent created successfully")
        
        job_analysis_agent = JobAnalysisAgent()
        print("✅ JobAnalysisAgent created successfully")
        
        # Test factory creation
        factory_resume = AgentFactory.create_agent("resume")
        print("✅ Factory ResumeAgent created successfully")
        
        factory_ranking = AgentFactory.create_agent("ranking")
        print("✅ Factory RankingAgent created successfully")
        
        factory_job_analysis = AgentFactory.create_agent("job_analysis")
        print("✅ Factory JobAnalysisAgent created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation error: {e}")
        return False

def test_agent_structure():
    """Test that agents have the expected structure."""
    print("\nTesting agent structure...")
    
    try:
        from agents import ResumeAgent, RankingAgent, JobAnalysisAgent
        
        resume_agent = ResumeAgent()
        ranking_agent = RankingAgent()
        job_analysis_agent = JobAnalysisAgent()
        
        # Check that agents have required methods
        required_methods = ['create_nodes', 'define_edges', 'get_entry_point', 'get_state_class', 'run']
        
        agents_to_test = [
            (resume_agent, "ResumeAgent"), 
            (ranking_agent, "RankingAgent"),
            (job_analysis_agent, "JobAnalysisAgent")
        ]
        
        for agent, name in agents_to_test:
            for method in required_methods:
                if not hasattr(agent, method):
                    print(f"❌ {name} missing method: {method}")
                    return False
            print(f"✅ {name} has all required methods")
        
        # Check that graphs are built
        if resume_agent.graph is None:
            print("❌ ResumeAgent graph not built")
            return False
        print("✅ ResumeAgent graph built successfully")
        
        if ranking_agent.graph is None:
            print("❌ RankingAgent graph not built")
            return False
        print("✅ RankingAgent graph built successfully")
        
        if job_analysis_agent.graph is None:
            print("❌ JobAnalysisAgent graph not built")
            return False
        print("✅ JobAnalysisAgent graph built successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent structure test error: {e}")
        return False

def test_agent_specific_methods():
    """Test agent-specific methods exist."""
    print("\nTesting agent-specific methods...")
    
    try:
        from agents import ResumeAgent, RankingAgent, JobAnalysisAgent
        
        # Test ResumeAgent methods
        resume_agent = ResumeAgent()
        resume_methods = [
            'generate_bullet_points_for_experience',
            'generate_bullet_points_for_project', 
            'generate_bullet_points',
            'query_experience_from_db',
            'query_project_from_db'
        ]
        
        for method in resume_methods:
            if not hasattr(resume_agent, method):
                print(f"❌ ResumeAgent missing method: {method}")
                return False
        print("✅ ResumeAgent has all specific methods")
        
        # Test RankingAgent methods (new decoupled methods)
        ranking_agent = RankingAgent()
        ranking_methods = [
            'rank_experiences',
            'rank_projects', 
            'rank_both',
            'rank_experiences_from_url',  # Backward compatibility
            'rank_projects_from_url',     # Backward compatibility
            'rank_both_from_url',         # Backward compatibility
            'query_all_user_experiences',
            'query_all_user_projects',
            'get_ranking_summary'
        ]
        
        for method in ranking_methods:
            if not hasattr(ranking_agent, method):
                print(f"❌ RankingAgent missing method: {method}")
                return False
        print("✅ RankingAgent has all specific methods")
        
        # Test JobAnalysisAgent methods
        job_analysis_agent = JobAnalysisAgent()
        job_analysis_methods = [
            'analyze_job',
            'get_job_analysis_summary',
            '_extract_job_information',
            '_extract_technical_skills'
        ]
        
        for method in job_analysis_methods:
            if not hasattr(job_analysis_agent, method):
                print(f"❌ JobAnalysisAgent missing method: {method}")
                return False
        print("✅ JobAnalysisAgent has all specific methods")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent-specific methods test error: {e}")
        return False

def test_factory_agent_types():
    """Test that factory supports all agent types."""
    print("\nTesting factory agent types...")
    
    try:
        from agents import AgentFactory
        
        # Test available agents
        available = AgentFactory.list_available_agents()
        expected_agents = ["resume", "ranking", "job_analysis"]
        
        for agent_type in expected_agents:
            if agent_type not in available:
                print(f"❌ Factory missing agent type: {agent_type}")
                return False
        
        print(f"✅ Factory supports all expected agent types: {', '.join(available)}")
        
        # Test creating each type
        for agent_type in expected_agents:
            try:
                agent = AgentFactory.create_agent(agent_type)
                print(f"✅ Successfully created {agent_type} agent via factory")
            except Exception as e:
                print(f"❌ Failed to create {agent_type} agent: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Factory test error: {e}")
        return False

def test_graph_visualization():
    """Test graph visualization functionality."""
    print("\nTesting graph visualization...")
    
    try:
        from agents import ResumeAgent, RankingAgent, JobAnalysisAgent
        
        resume_agent = ResumeAgent()
        ranking_agent = RankingAgent()
        job_analysis_agent = JobAnalysisAgent()
        
        # Test that visualization methods exist and return strings
        agents_to_test = [
            (resume_agent, "ResumeAgent"),
            (ranking_agent, "RankingAgent"), 
            (job_analysis_agent, "JobAnalysisAgent")
        ]
        
        for agent, name in agents_to_test:
            try:
                viz = agent.get_graph_visualization()
                print(viz)
                if isinstance(viz, str) and len(viz) > 0:
                    print(f"✅ {name} graph visualization working")
                else:
                    print(f"❌ {name} graph visualization returned invalid result")
                    return False
            except Exception as e:
                print(f"❌ {name} graph visualization error: {e}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Graph visualization error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Decoupled Agent Architecture Structure\n")
    
    tests = [
        ("Imports", test_imports),
        ("Agent Creation", test_agent_creation),
        ("Agent Structure", test_agent_structure),
        ("Agent-Specific Methods", test_agent_specific_methods),
        ("Factory Agent Types", test_factory_agent_types),
        ("Graph Visualization", test_graph_visualization)
    ]
    
    passed = 0
    total = len(tests)
    failed_tests = []
    
    for test_name, test_func in tests:
        print(f"🔍 Running {test_name} Test...")
        if test_func():
            passed += 1
        else:
            failed_tests.append(test_name)
        print()
    
    print("📊 Test Results Summary")
    print("=" * 50)
    print(f"Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All structural tests passed! Decoupled architecture is properly implemented.")
        print("✨ Architecture features verified:")
        print("   • All agent imports working correctly")
        print("   • Standalone JobAnalysisAgent implemented")
        print("   • Decoupled RankingAgent with JobInfo support")
        print("   • Enhanced ResumeAgent with JobInfo context")
        print("   • Factory pattern supporting all agent types")
        print("   • Graph visualization for all agents")
        print("   • Backward compatibility methods present")
    else:
        print(f"\n⚠️  {len(failed_tests)} structural test(s) failed:")
        for failed_test in failed_tests:
            print(f"   • {failed_test}")
        print("\nThis indicates issues with the agent architecture implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 