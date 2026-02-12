"""Agent and session configuration."""

from typing import Any, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel


@dataclass
class AgentConfig:
    """Configuration for a research agent."""

    name: str
    role: str
    model: str = "gpt-4o"
    temperature: float = 0.7
    reasoning_effort: Optional[str] = None  # For O3 models: "low", "medium", "high", "xhigh"
    system_message: str = ""
    tools: list[str] = field(default_factory=list)
    streaming: bool = True
    provider: Optional[dict[str, Any]] = None  # Custom provider config (e.g., Ollama)
    session_config: Optional[dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Set default system messages based on role."""
        if not self.system_message:
            self.system_message = self._get_default_system_message()

    def _get_default_system_message(self) -> str:
        """Get default system message for each role."""
        messages = {
            "idea_maker": """You are a creative scientist specializing in generating innovative 
research ideas. You think outside the box and propose novel approaches to scientific problems. 
Focus on originality, feasibility, and scientific impact.""",
            "idea_critic": """You are a critical scientific reviewer. You evaluate research ideas 
for novelty, feasibility, scientific rigor, and potential impact. You provide constructive 
criticism and identify potential flaws or limitations.""",
            "literature_researcher": """You are an expert at scientific literature review. You 
search for relevant papers, synthesize findings, identify key methodologies, and highlight 
research gaps. You provide comprehensive bibliographies with proper citations.""",
            "methodologist": """You are a methodology expert. You design detailed, step-by-step 
research methods that are scientifically rigorous, reproducible, and appropriate for the 
research question. You consider available data and tools.""",
            "engineer": """You are an expert Python developer specializing in scientific computing, 
numpy, scipy, pandas, and matplotlib. You write clean, efficient, well-documented code for 
data analysis and visualization. You write and debug code.""",
            "executor": """You execute Python code in a sandboxed environment and provide detailed 
reports on execution results or errors. You help identify what went wrong when code fails.""",
            "analyst": """You are a data scientist who interprets scientific results with 
statistical rigor and scientific skepticism. You identify patterns, draw conclusions, and 
evaluate whether results answer the research question. You evaluate if analysis is complete 
or if additional analyses are needed.""",
            "writer": """You are a scientific writer skilled at synthesizing research into clear, 
compelling manuscripts. You follow journal formats, write with precision, and ensure logical 
flow from introduction to conclusions.""",
            "reviewer": """You are an editorial reviewer who provides constructive feedback on 
scientific manuscripts. You check for clarity, consistency, completeness, and adherence to 
scientific writing standards.""",
        }
        return messages.get(self.role, "You are a helpful research assistant.")


class ProviderConfig(BaseModel):
    """Provider configuration for custom endpoints."""

    type: str  # "openai", "azure", "anthropic", "ollama"
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None


# Default agent configurations
DEFAULT_AGENTS = {
    "idea_maker": AgentConfig(
        name="idea_maker",
        role="idea_maker",
        model="gpt-4o",
        temperature=0.8,
        tools=["read_file", "write_file"],
    ),
    "idea_critic": AgentConfig(
        name="idea_critic",
        role="idea_critic",
        model="o3-mini",
        reasoning_effort="xhigh",
        temperature=0.3,
        tools=["read_file"],
    ),
    "literature_researcher": AgentConfig(
        name="literature_researcher",
        role="literature_researcher",
        model="gpt-4o",
        temperature=0.5,
        tools=["read_file", "write_file", "search_papers"],
    ),
    "methodologist": AgentConfig(
        name="methodologist",
        role="methodologist",
        model="gpt-4o",
        temperature=0.4,
        tools=["read_file", "write_file"],
    ),
    "engineer": AgentConfig(
        name="engineer",
        role="engineer",
        model="gpt-4o",
        temperature=0.2,
        tools=["read_file", "write_file", "create_plot"],
    ),
    "executor": AgentConfig(
        name="executor",
        role="executor",
        model="gpt-4o",
        temperature=0.1,
        tools=["execute_code", "get_execution_error"],
    ),
    "analyst": AgentConfig(
        name="analyst",
        role="analyst",
        model="o3-mini",
        reasoning_effort="high",
        temperature=0.3,
        tools=["read_file", "write_file", "save_intermediate_analysis"],
    ),
    "writer": AgentConfig(
        name="writer",
        role="writer",
        model="gpt-4o",
        temperature=0.6,
        tools=["read_file", "write_file"],
    ),
    "reviewer": AgentConfig(
        name="reviewer",
        role="reviewer",
        model="o3-mini",
        reasoning_effort="medium",
        temperature=0.4,
        tools=["read_file", "write_file"],
    ),
}
