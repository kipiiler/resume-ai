import os
import json
import re
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, List, TypedDict, Annotated, Sequence
import operator
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()

class BaseAgentState(TypedDict):
    """Base state structure for all agents."""
    messages: Annotated[Sequence[HumanMessage | AIMessage], operator.add]
    error: str

class BaseAgent(ABC):
    """Abstract base class for all LangGraph agents."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash-lite", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = self._create_llm()
        self.graph = None
        self._build_graph()
    
    def _create_llm(self) -> ChatGoogleGenerativeAI:
        """Create and configure the LLM."""
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=api_key
        )
    
    def _create_prompt_template(self, system_message: str, human_message: str) -> ChatPromptTemplate:
        """Create a chat prompt template."""
        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", human_message)
        ])
    
    def _safe_llm_invoke(self, prompt: str, fallback_response: str = "") -> str:
        """Safely invoke LLM with error handling."""
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            print(f"LLM invocation error: {e}")
            return fallback_response
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean and extract JSON from LLM response."""
        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        
        # Find JSON content between braces or brackets
        json_match = re.search(r'[\[\{].*[\]\}]', response_text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return response_text.strip()
    
    @abstractmethod
    def get_state_class(self) -> type:
        """Return the state class for this agent."""
        pass
    
    @abstractmethod
    def create_nodes(self) -> Dict[str, Callable]:
        """Create all nodes for the agent graph."""
        pass
    
    @abstractmethod
    def define_edges(self) -> List[tuple]:
        """Define the edges between nodes."""
        pass
    
    @abstractmethod
    def get_entry_point(self) -> str:
        """Return the entry point node name."""
        pass
    
    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Create the graph with the appropriate state class
        state_class = self.get_state_class()
        workflow = StateGraph(state_class)
        
        # Add nodes
        nodes = self.create_nodes()
        for node_name, node_func in nodes.items():
            workflow.add_node(node_name, node_func)
        
        # Add edges
        edges = self.define_edges()
        for edge in edges:
            if len(edge) == 2:
                # Simple edge: from_node -> to_node
                workflow.add_edge(edge[0], edge[1])
            elif len(edge) == 3:
                # Conditional edge: from_node -> condition_func -> {condition: to_node}
                workflow.add_conditional_edges(edge[0], edge[1], edge[2])
        
        # Set entry point and end
        workflow.set_entry_point(self.get_entry_point())
        
        # Add END edges for terminal nodes
        terminal_nodes = self._get_terminal_nodes(edges)
        for node in terminal_nodes:
            workflow.add_edge(node, END)
        
        # Compile the graph
        self.graph = workflow.compile()
    
    def _get_terminal_nodes(self, edges: List[tuple]) -> List[str]:
        """Identify terminal nodes that should connect to END."""
        all_nodes = set(self.create_nodes().keys())
        nodes_with_outgoing = set()
        
        for edge in edges:
            if len(edge) >= 2:
                nodes_with_outgoing.add(edge[0])
        
        # Terminal nodes are those without outgoing edges
        terminal_nodes = all_nodes - nodes_with_outgoing
        return list(terminal_nodes)
    
    def run(self, initial_state: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent with the given initial state."""
        try:
            if not self.graph:
                raise ValueError("Graph not built. Call _build_graph() first.")
            
            result = self.graph.invoke(initial_state)
            return result
        except Exception as e:
            error_msg = f"Agent execution error: {str(e)}"
            print(error_msg)
            return {**initial_state, "error": error_msg}
    
    def get_graph_visualization(self) -> str:
        """Get a text representation of the graph structure."""
        if not self.graph:
            return "Graph not built"
        
        nodes = list(self.create_nodes().keys())
        edges = self.define_edges()
        
        viz = f"Agent: {self.__class__.__name__}\n"
        viz += f"Nodes: {', '.join(nodes)}\n"
        viz += "Edges:\n"
        for edge in edges:
            if len(edge) == 2:
                viz += f"  {edge[0]} -> {edge[1]}\n"
            elif len(edge) == 3:
                viz += f"  {edge[0]} -> [conditional] -> {edge[2]}\n"
        
        return viz

class AgentFactory:
    """Factory class for creating different types of agents."""
    
    @staticmethod
    def create_agent(agent_type: str, **kwargs) -> BaseAgent:
        """Create an agent of the specified type."""
        # Import here to avoid circular imports
        from agents.resume_agent import ResumeAgent
        from agents.ranking_agent import RankingAgent
        
        agent_classes = {
            "resume": ResumeAgent,
            "ranking": RankingAgent,
        }
        
        if agent_type not in agent_classes:
            available_types = ", ".join(agent_classes.keys())
            raise ValueError(f"Unknown agent type: {agent_type}. Available types: {available_types}")
        
        agent_class = agent_classes[agent_type]
        return agent_class(**kwargs)
    
    @staticmethod
    def list_available_agents() -> List[str]:
        """List all available agent types."""
        return ["resume", "ranking"]
