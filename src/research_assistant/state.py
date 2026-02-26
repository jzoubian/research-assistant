"""Research state management."""

from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field

try:
    from research_assistant.resources import ResourceManager
except ImportError:
    ResourceManager = None

try:
    from research_assistant.git_tracker import GitTracker
except ImportError:
    GitTracker = None


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
    
    # Git-based iteration tracking
    git_enabled: bool = True
    
    # Resource manager (not serialized)
    resource_manager: Optional[object] = Field(default=None, exclude=True)
    
    # Git tracker (not serialized)
    git_tracker: Optional[object] = Field(default=None, exclude=True)
    
    def __init__(self, **data):
        """Initialize state and set up resource manager and Git tracking."""
        super().__init__(**data)
        # Ensure project directory exists
        self.project_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize resource manager if available
        if ResourceManager:
            self.resource_manager = ResourceManager(self.project_dir)
            self.resource_manager.load_resources()
        else:
            self.resource_manager = None
        
        # Initialize Git tracker if enabled
        if self.git_enabled and GitTracker:
            self.git_tracker = GitTracker(self.project_dir)
            self.git_tracker.ensure_initialized()
        else:
            self.git_tracker = None

    class Config:
        arbitrary_types_allowed = True

    def mark_module_complete(self, module: str) -> None:
        """Mark a module as completed and commit to Git."""
        self.completed_modules.add(module)
        if self.git_tracker:
            self.git_tracker.commit_step(module, "completed", "Module marked as complete")
        self.save_state()

    def is_module_complete(self, module: str) -> bool:
        """Check if a module is completed."""
        return module in self.completed_modules
    
    def commit_step(self, module: str, step: str, description: str = "") -> Optional[str]:
        """Commit a step to Git.
        
        Args:
            module: Module name
            step: Step name
            description: Optional description
            
        Returns:
            Commit hash or None if Git not enabled
        """
        if self.git_tracker:
            return self.git_tracker.commit_step(module, step, description)
        return None
    
    def commit_iteration(self, module: str, iteration: int, description: str = "") -> Optional[str]:
        """Commit an iteration to Git.
        
        Args:
            module: Module name
            iteration: Iteration number
            description: Optional description
            
        Returns:
            Commit hash or None if Git not enabled
        """
        if self.git_tracker:
            return self.git_tracker.commit_iteration(module, iteration, description)
        return None
    
    def commit_debug_attempt(self, module: str, iteration: int, attempt: int, error: str = "") -> Optional[str]:
        """Commit a debug attempt to Git.
        
        Args:
            module: Module name
            iteration: Iteration number
            attempt: Debug attempt number
            error: Error message
            
        Returns:
            Commit hash or None if Git not enabled
        """
        if self.git_tracker:
            return self.git_tracker.commit_debug_attempt(module, iteration, attempt, error)
        return None
    
    def commit_user_input(self, module: str, action: str, notes: str = "") -> Optional[str]:
        """Commit user input to Git.
        
        Args:
            module: Module name
            action: User action
            notes: Optional notes
            
        Returns:
            Commit hash or None if Git not enabled
        """
        if self.git_tracker:
            return self.git_tracker.commit_user_input(module, action, notes)
        return None
    
    def get_module_status(self, module: str) -> Optional[dict]:
        """Get module status from Git.
        
        Args:
            module: Module name
            
        Returns:
            Status dict or None if Git not enabled
        """
        if self.git_tracker:
            return self.git_tracker.get_module_status(module)
        return None
    
    def get_iteration_diff(self, module: str, from_iteration: int, to_iteration: int) -> Optional[str]:
        """Get diff between iterations.
        
        Args:
            module: Module name
            from_iteration: Starting iteration
            to_iteration: Ending iteration
            
        Returns:
            Diff string or None if Git not enabled
        """
        if self.git_tracker:
            return self.git_tracker.get_iteration_diff(module, from_iteration, to_iteration)
        return None
    
    def print_git_status(self) -> None:
        """Print Git status."""
        if self.git_tracker:
            self.git_tracker.print_status()
    
    def print_module_git_status(self, module: str) -> None:
        """Print Git status for a module."""
        if self.git_tracker:
            self.git_tracker.print_module_status(module)
    
    def save_state(self) -> None:
        """Save state to JSON file and commit to Git."""
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
        
        # Commit state to Git
        if self.git_tracker:
            self.git_tracker.stage_files([".research_state.json"])
            if self.git_tracker.has_changes():
                self.git_tracker.commit("Update research state")
    
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
        
        # Create state instance (this will reinitialize Git tracker)
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
