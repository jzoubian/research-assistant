"""Research state management."""

from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field


class ResearchState(BaseModel):
    """State management for research workflow."""

    # Project metadata
    project_dir: Path
    data_description: str = ""

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

    class Config:
        arbitrary_types_allowed = True

    def mark_module_complete(self, module: str) -> None:
        """Mark a module as completed."""
        self.completed_modules.add(module)

    def is_module_complete(self, module: str) -> bool:
        """Check if a module is completed."""
        return module in self.completed_modules

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
