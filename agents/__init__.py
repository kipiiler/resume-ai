"""
LangGraph Agent Abstraction Package

This package provides a comprehensive abstraction layer for creating LangGraph agents
with common functionality and patterns.

Base Classes:
- BaseAgent: Abstract base class for all agents
- BaseAgentState: Base state structure
- DatabaseAgent: Base class for database-enabled agents  
- JobAnalysisAgent: Base class for job analysis agents

Concrete Agents:
- ResumeAgent: Generates resume bullet points from experience data
- RankingAgent: Ranks user experiences based on job posting relevance

Factory:
- AgentFactory: Factory class for creating agents
"""

from agents.base_agents import BaseAgent, BaseAgentState, AgentFactory
from agents.database_agent import DatabaseAgent
from agents.job_analysis_agent import JobAnalysisAgent
from agents.resume_agent import ResumeAgent
from agents.ranking_agent import RankingAgent

__all__ = [
    # Base classes
    "BaseAgent",
    "BaseAgentState", 
    "DatabaseAgent",
    "JobAnalysisAgent",
    
    # Concrete agents
    "ResumeAgent",
    "RankingAgent",
    
    # Factory
    "AgentFactory"
]

__version__ = "1.0.0" 