"""Configuration management for research projects."""

from pathlib import Path
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import tomli
import tomli_w


class AgentConfiguration(BaseModel):
    """Configuration for a single agent."""
    name: str
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    reasoning_effort: Optional[str] = None  # For o3-mini: low, medium, high


class ExecutionConfig(BaseModel):
    """Execution configuration."""
    mode: str = Field("interactive", description="interactive or autonomous")
    require_code_approval: bool = Field(True, description="Require approval before executing code")
    max_iterations: int = Field(3, description="Maximum iterations per module")
    timeout_seconds: int = Field(300, description="Timeout for code execution")


class ProjectConfig(BaseModel):
    """Complete project configuration."""
    
    # Project metadata
    project_name: str
    description: str = ""
    version: str = "1.0.0"
    
    # Environment
    env_manager: str = Field("pixi", description="Environment manager: pixi, apptainer, nix, guix")
    python_version: str = "3.10"
    
    # Execution settings
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    
    # Agent configurations
    agents: Dict[str, AgentConfiguration] = Field(default_factory=dict)
    
    # Module settings
    modules: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "idea": {"enabled": True, "max_iterations": 3},
            "literature": {"enabled": True, "max_papers": 20},
            "methodology": {"enabled": True},
            "analysis": {"enabled": True, "max_retries": 3},
            "paper": {"enabled": True, "journal_format": "nature"},
            "review": {"enabled": True},
        }
    )
    
    # Paths
    paths: Dict[str, str] = Field(
        default_factory=lambda: {
            "input_dir": "input",
            "output_dir": "output",
            "data_description": "input/data_description.md",
            "state_file": ".research_state.json",
            "resources_file": "resources.json",
        }
    )
    
    # Custom parameters
    custom: Dict[str, Any] = Field(default_factory=dict)


class ConfigManager:
    """Manage project configuration."""
    
    def __init__(self, project_dir: Path):
        """Initialize configuration manager.
        
        Args:
            project_dir: Path to project directory
        """
        self.project_dir = project_dir
        self.config_file = project_dir / "research_config.toml"
        self.config: Optional[ProjectConfig] = None
    
    def load_config(self) -> bool:
        """Load configuration from TOML file.
        
        Returns:
            True if loaded successfully
        """
        if not self.config_file.exists():
            return False
        
        try:
            with open(self.config_file, 'rb') as f:
                data = tomli.load(f)
            
            self.config = ProjectConfig(**data)
            return True
        except Exception as e:
            print(f"Failed to load config: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to TOML file.
        
        Returns:
            True if saved successfully
        """
        if not self.config:
            return False
        
        try:
            data = self.config.model_dump(exclude_none=True)
            
            with open(self.config_file, 'wb') as f:
                tomli_w.dump(data, f)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def create_default_config(self, project_name: str) -> None:
        """Create default configuration.
        
        Args:
            project_name: Name of the project
        """
        self.config = ProjectConfig(
            project_name=project_name,
            description="Research project configuration",
            env_manager="pixi",
            python_version="3.10",
            execution=ExecutionConfig(
                mode="interactive",
                require_code_approval=True,
                max_iterations=3,
                timeout_seconds=300,
            ),
            agents={
                "idea_maker": AgentConfiguration(
                    name="idea_maker",
                    model="gpt-4",
                    temperature=0.9,
                ),
                "idea_critic": AgentConfiguration(
                    name="idea_critic",
                    model="o3-mini",
                    temperature=0.3,
                    reasoning_effort="high",
                ),
                "literature_researcher": AgentConfiguration(
                    name="literature_researcher",
                    model="gpt-4",
                    temperature=0.5,
                ),
                "methodologist": AgentConfiguration(
                    name="methodologist",
                    model="gpt-4",
                    temperature=0.7,
                ),
                "engineer": AgentConfiguration(
                    name="engineer",
                    model="gpt-4.1",
                    temperature=0.3,
                ),
                "executor": AgentConfiguration(
                    name="executor",
                    model="gpt-4.1",
                    temperature=0.2,
                ),
                "analyst": AgentConfiguration(
                    name="analyst",
                    model="o3-mini",
                    temperature=0.5,
                    reasoning_effort="medium",
                ),
                "writer": AgentConfiguration(
                    name="writer",
                    model="gpt-4",
                    temperature=0.7,
                ),
                "reviewer": AgentConfiguration(
                    name="reviewer",
                    model="o3-mini",
                    temperature=0.5,
                    reasoning_effort="high",
                ),
            },
        )
    
    def get_agent_config(self, agent_name: str) -> Optional[AgentConfiguration]:
        """Get configuration for a specific agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent configuration or None
        """
        if not self.config:
            return None
        return self.config.agents.get(agent_name)
    
    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """Get configuration for a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Module configuration dictionary
        """
        if not self.config:
            return {}
        return self.config.modules.get(module_name, {})
    
    def is_module_enabled(self, module_name: str) -> bool:
        """Check if a module is enabled.
        
        Args:
            module_name: Name of the module
            
        Returns:
            True if enabled
        """
        module_config = self.get_module_config(module_name)
        return module_config.get("enabled", True)
    
    def get_execution_params(self) -> Dict[str, Any]:
        """Get execution parameters.
        
        Returns:
            Dictionary of execution parameters
        """
        if not self.config:
            return {}
        
        return {
            "mode": self.config.execution.mode,
            "require_code_approval": self.config.execution.require_code_approval,
            "max_iterations": self.config.execution.max_iterations,
            "timeout_seconds": self.config.execution.timeout_seconds,
        }
    
    def update_from_cli_args(self, **kwargs) -> None:
        """Update configuration from CLI arguments.
        
        Args:
            **kwargs: CLI arguments to update
        """
        if not self.config:
            return
        
        # Update execution settings
        if "mode" in kwargs and kwargs["mode"]:
            self.config.execution.mode = kwargs["mode"]
        if "require_code_approval" in kwargs and kwargs["require_code_approval"] is not None:
            self.config.execution.require_code_approval = kwargs["require_code_approval"]
        if "env_manager" in kwargs and kwargs["env_manager"]:
            self.config.env_manager = kwargs["env_manager"]
    
    def export_template(self, output_path: Path) -> bool:
        """Export configuration template with comments.
        
        Args:
            output_path: Path to save template
            
        Returns:
            True if successful
        """
        template = '''# Research Assistant Configuration
# This file configures all aspects of your research project

# Project metadata
project_name = "my_research"
description = "Description of your research project"
version = "1.0.0"

# Environment configuration
env_manager = "pixi"  # Options: pixi, apptainer, nix, guix
python_version = "3.10"

# Execution settings
[execution]
mode = "interactive"  # Options: interactive, autonomous
require_code_approval = true  # Require approval before executing code
max_iterations = 3  # Maximum iterations per module
timeout_seconds = 300  # Timeout for code execution

# Agent configurations
[agents.idea_maker]
name = "idea_maker"
model = "gpt-4"
temperature = 0.9

[agents.idea_critic]
name = "idea_critic"
model = "o3-mini"
temperature = 0.3
reasoning_effort = "high"  # Options: low, medium, high

[agents.literature_researcher]
name = "literature_researcher"
model = "gpt-4"
temperature = 0.5

[agents.methodologist]
name = "methodologist"
model = "gpt-4"
temperature = 0.7

[agents.engineer]
name = "engineer"
model = "gpt-4.1"
temperature = 0.3

[agents.executor]
name = "executor"
model = "gpt-4.1"
temperature = 0.2

[agents.analyst]
name = "analyst"
model = "o3-mini"
temperature = 0.5
reasoning_effort = "medium"

[agents.writer]
name = "writer"
model = "gpt-4"
temperature = 0.7

[agents.reviewer]
name = "reviewer"
model = "o3-mini"
temperature = 0.5
reasoning_effort = "high"

# Module settings
[modules.idea]
enabled = true
max_iterations = 3

[modules.literature]
enabled = true
max_papers = 20

[modules.methodology]
enabled = true

[modules.analysis]
enabled = true
max_retries = 3

[modules.paper]
enabled = true
journal_format = "nature"  # Options: nature, science, pnas, arxiv

[modules.review]
enabled = true

# File paths (relative to project directory)
[paths]
input_dir = "input"
output_dir = "output"
data_description = "input/data_description.md"
state_file = ".research_state.json"
resources_file = "resources.json"

# Custom parameters (add your own here)
[custom]
# Example custom parameters:
# domain = "cosmology"
# experiment_type = "simulation"
'''
        try:
            with open(output_path, 'w') as f:
                f.write(template)
            return True
        except Exception as e:
            print(f"Failed to export template: {e}")
            return False
    
    def validate_config(self) -> tuple[bool, List[str]]:
        """Validate configuration.
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not self.config:
            return False, ["No configuration loaded"]
        
        errors = []
        
        # Validate env_manager
        valid_env_managers = ["pixi", "apptainer", "nix", "guix"]
        if self.config.env_manager not in valid_env_managers:
            errors.append(f"Invalid env_manager: {self.config.env_manager}. Must be one of {valid_env_managers}")
        
        # Validate execution mode
        valid_modes = ["interactive", "autonomous"]
        if self.config.execution.mode not in valid_modes:
            errors.append(f"Invalid execution mode: {self.config.execution.mode}. Must be one of {valid_modes}")
        
        # Validate agents
        required_agents = ["idea_maker", "idea_critic", "literature_researcher", 
                          "methodologist", "engineer", "executor", "analyst", "writer", "reviewer"]
        for agent_name in required_agents:
            if agent_name not in self.config.agents:
                errors.append(f"Missing required agent: {agent_name}")
        
        # Validate paths exist
        for path_name, path_value in self.config.paths.items():
            if not path_name.endswith("_file"):  # Don't check files, only dirs
                full_path = self.project_dir / path_value
                if not full_path.exists() and path_name.endswith("_dir"):
                    errors.append(f"Path does not exist: {path_value}")
        
        return len(errors) == 0, errors
    
    def get_summary(self) -> str:
        """Get human-readable configuration summary.
        
        Returns:
            Formatted string with configuration summary
        """
        if not self.config:
            return "No configuration loaded"
        
        lines = [
            f"Project: {self.config.project_name}",
            f"Version: {self.config.version}",
            f"Environment: {self.config.env_manager} (Python {self.config.python_version})",
            f"Mode: {self.config.execution.mode}",
            "",
            "Enabled Modules:",
        ]
        
        for module_name, module_config in self.config.modules.items():
            if module_config.get("enabled", True):
                lines.append(f"  ✓ {module_name}")
            else:
                lines.append(f"  ✗ {module_name} (disabled)")
        
        lines.extend([
            "",
            f"Agents: {len(self.config.agents)} configured",
        ])
        
        return "\n".join(lines)
