#!/usr/bin/env python3
"""
Test script for refactored agents to verify they work correctly.
"""

import os
import sys

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all agent classes can be imported correctly."""
    print("Testing imports...")
    
    try:
        from agents import (
            BaseAgent, BaseAgentState, DatabaseAgent, JobAnalysisAgent,
            ResumeAgent, RankingAgent, AgentFactory
        )
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_agent_creation():
    """Test that agents can be created successfully."""
    print("\nTesting agent creation...")
    
    try:
        from agents import ResumeAgent, RankingAgent, AgentFactory
        
        # Test direct instantiation
        resume_agent = ResumeAgent()
        print("✅ ResumeAgent created successfully")
        
        ranking_agent = RankingAgent()
        print("✅ RankingAgent created successfully")
        
        # Test factory creation
        factory_resume = AgentFactory.create_agent("resume")
        print("✅ Factory ResumeAgent created successfully")
        
        factory_ranking = AgentFactory.create_agent("ranking")
        print("✅ Factory RankingAgent created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent creation error: {e}")
        return False

def test_agent_structure():
    """Test that agents have the expected structure."""
    print("\nTesting agent structure...")
    
    try:
        from agents import ResumeAgent, RankingAgent
        
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
        
        # Check that graphs are built
        if resume_agent.graph is None:
            print("❌ ResumeAgent graph not built")
            return False
        print("✅ ResumeAgent graph built successfully")
        
        if ranking_agent.graph is None:
            print("❌ RankingAgent graph not built")
            return False
        print("✅ RankingAgent graph built successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent structure test error: {e}")
        return False

def test_graph_visualization():
    """Test graph visualization functionality."""
    print("\nTesting graph visualization...")
    
    try:
        from agents import ResumeAgent, RankingAgent
        
        resume_agent = ResumeAgent()
        ranking_agent = RankingAgent()
        
        resume_viz = resume_agent.get_graph_visualization()
        ranking_viz = ranking_agent.get_graph_visualization()
        
        print("ResumeAgent Graph Structure:")
        print(resume_viz)
        print("\nRankingAgent Graph Structure:")
        print(ranking_viz)
        
        print("✅ Graph visualization working")
        return True
        
    except Exception as e:
        print(f"❌ Graph visualization error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Refactored Agents\n")
    
    tests = [
        test_imports,
        test_agent_creation,
        test_agent_structure,
        test_graph_visualization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Refactoring successful.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 