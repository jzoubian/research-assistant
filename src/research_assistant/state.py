"""Research state management."""

from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field

try:
    from research_assistant.resources import ResourceManager
except ImportError:
    ResourceManager = None


class ModuleIteration(BaseModel):
    """Track a single iteration of a module."""
    iteration: int
    timestamp: str
    input_files: list[str] = Field(default_factory=list)
    output_files: list[str] = Field(default_factory=list)
    notes: str = ""
    status: str = "completed"  # completed, failed, in_progress


class ResearchState(BaseModel):
    """State management for research workflow."""

    # Project metadata
    project_dir: Path
    data_description: str = ""
    env_manager: str = "pixi"  # pixi, apptainer, nix, guix

    # Research artifacts
    idea: str = ""
    literature: str = ""
    methodology: str = ""
    analysis: str = ""
    paper: str = ""

    # File paths
    plot_paths: list[Path] = Field(default_factory=list)
    code_files: list[Path] = Field(default_factory=list)
    intermediate_analyses: list[Path] = Field(default_factory=list)

    # Agent interaction history
    agent_history: list[dict] = Field(default_factory=list)

    # Module completion tracking
    completed_modules: set[str] = Field(default_factory=set)
    
    # Iteration tracking per module
    module_iterations: dict[str, list[ModuleIteration]] = Field(default_factory=dict)
    
    def __init__(self, **data):
        """Initialize state and set up resource manager."""
        super().__init__(**data)
        # Ensure project directory exists
        self.project_dir.mkdir(parents=True, exist_ok=True)
        # Initialize resource manager if available
        if ResourceManager:
            self.resource_manager = ResourceManager(self.project_dir)
            self.resource_manager.load_resources()
        else:
            self.resource_manager = None

    class Config:
        arbitrary_types_allowed = True

    def mark_module_complete(self, module: str) -> None:
        """Mark a module as completed."""
        self.completed_modules.add(module)

    def is_module_complete(self, module: str) -> bool:
        """Check if a module is completed."""
        return module in self.completed_modules
    
    def add_module_iteration(
        self, module: str, input_files: list[str], output_files: list[str], notes: str = ""
    ) -> int:
        """Add a new iteration for a module.
        
        Returns:
            Iteration number
        """
        from datetime import datetime
        
        if module not in self.module_iterations:
            self.module_iterations[module] = []
        
        iteration_num = len(self.module_iterations[module]) + 1
        
        iteration = ModuleIteration(
            iteration=iteration_num,
            timestamp=datetime.now().isoformat(),
            input_files=input_files,
            output_files=output_files,
            notes=notes,
            status="completed"
        )
        
        self.module_iterations[module].append(iteration)
        return iteration_num
    
    def get_module_iteration_count(self, module: str) -> int:
        """Get the number of iterations for a module."""
        return len(self.module_iterations.get(module, []))
    
    def get_latest_iteration(self, module: str) -> Optional[ModuleIteration]:
        """Get the latest iteration for a module."""
        iterations = self.module_iterations.get(module, [])
        return iterations[-1] if iterations else None
    
    def save_state(self) -> None:
        """Save state to JSON file."""
        state_file = self.project_dir / ".research_state.json"
        state_data = self.model_dump(mode="json")
        # Convert Path objects to strings for JSON serialization
        state_data["project_dir"] = str(state_data["project_dir"])
        state_data["plot_paths"] = [str(p) for p in state_data["plot_paths"]]
        state_data["code_files"] = [str(p) for p in state_data["code_files"]]
        state_data["intermediate_analyses"] = [str(p) for p in state_data["intermediate_analyses"]]
        
        import json
        with open(state_file, "w") as f:
            json.dump(state_data, f, indent=2)
    
    @classmethod
    def load_state(cls, project_dir: Path) -> Optional["ResearchState"]:
        """Load state from JSON file."""
        state_file = project_dir / ".research_state.json"
        if not state_file.exists():
            return None
        
        import json
        with open(state_file, "r") as f:
            state_data = json.load(f)
        
        # Convert string paths back to Path objects
        state_data["project_dir"] = Path(state_data["project_dir"])
        state_data["plot_paths"] = [Path(p) for p in state_data["plot_paths"]]
        state_data["code_files"] = [Path(p) for p in state_data["code_files"]]
        state_data["intermediate_analyses"] = [Path(p) for p in state_data["intermediate_analyses"]]
        
        return cls(**state_data)

    def add_agent_interaction(self, agent: str, prompt: str, response: str) -> None:
        """Log an agent interaction."""
        self.agent_history.append(
            {"agent": agent, "prompt": prompt, "response": response}
        )

    def load_from_files(self) -> None:
        """Load state from markdown files in project directory."""
        input_dir = self.project_dir / "input"
        output_dir = self.project_dir / "output"

        # Load data description
        data_desc_file = input_dir / "data_description.md"
        if data_desc_file.exists():
            self.data_description = data_desc_file.read_text()

        # Load research artifacts
        if (output_dir / "idea.md").exists():
            self.idea = (output_dir / "idea.md").read_text()
            self.mark_module_complete("idea")

        if (output_dir / "literature.md").exists():
            self.literature = (output_dir / "literature.md").read_text()
            self.mark_module_complete("literature")

        if (output_dir / "methodology.md").exists():
            self.methodology = (output_dir / "methodology.md").read_text()
            self.mark_module_complete("methodology")

        if (output_dir / "analysis.md").exists():
            self.analysis = (output_dir / "analysis.md").read_text()
            self.mark_module_complete("analysis")

        if (output_dir / "paper.md").exists():
            self.paper = (output_dir / "paper.md").read_text()
            self.mark_module_complete("paper")

        # Load file paths
        plot_dir = output_dir / "plots"
        if plot_dir.exists():
            self.plot_paths = list(plot_dir.glob("*.png")) + list(plot_dir.glob("*.pdf"))

        code_dir = output_dir / "code"
        if code_dir.exists():
            self.code_files = list(code_dir.glob("*.py"))

        intermediate_dir = output_dir / "intermediate"
        if intermediate_dir.exists():
            self.intermediate_analyses = sorted(intermediate_dir.glob("analysis_*.md"))

    def save_to_file(self, output_path: Path, content: str) -> None:
        """Save content to a file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)

    def get_context_for_agent(self, agent_role: str) -> dict[str, str]:
        """Get relevant context for a specific agent."""
        context = {"data_description": self.data_description}

        # Add relevant context based on agent role and completed modules
        if agent_role in ["idea_critic", "literature_researcher", "methodologist"]:
            if self.idea:
                context["idea"] = self.idea

        if agent_role in ["methodologist", "engineer", "analyst"]:
            if self.literature:
                context["literature"] = self.literature

        if agent_role in ["engineer", "executor", "analyst"]:
            if self.methodology:
                context["methodology"] = self.methodology

        if agent_role in ["writer", "reviewer"]:
            context.update(
                {
                    "idea": self.idea,
                    "literature": self.literature,
                    "methodology": self.methodology,
                    "analysis": self.analysis,
                }
            )

        return context
