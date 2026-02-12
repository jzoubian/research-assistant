"""Main ResearchAssistant class."""

from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Confirm

from research_assistant.config import AgentConfig, DEFAULT_AGENTS
from research_assistant.state import ResearchState
from research_assistant.orchestrator import AgentOrchestrator


console = Console()


class ResearchAssistant:
    """Main research assistant orchestrator."""

    def __init__(
        self,
        project_dir: str,
        agent_configs: Optional[dict[str, AgentConfig]] = None,
    ):
        """Initialize research assistant.

        Args:
            project_dir: Path to research project directory
            agent_configs: Custom agent configurations (defaults to DEFAULT_AGENTS)
        """
        self.project_dir = Path(project_dir)
        self.agent_configs = agent_configs or DEFAULT_AGENTS
        self.orchestrator = AgentOrchestrator(str(self.project_dir))
        self.state = ResearchState(project_dir=self.project_dir)

        # Ensure project structure exists
        self._setup_project_structure()

    def _setup_project_structure(self) -> None:
        """Create project directory structure."""
        (self.project_dir / "input").mkdir(parents=True, exist_ok=True)
        (self.project_dir / "output").mkdir(parents=True, exist_ok=True)
        (self.project_dir / "output" / "plots").mkdir(parents=True, exist_ok=True)
        (self.project_dir / "output" / "code").mkdir(parents=True, exist_ok=True)
        (self.project_dir / "output" / "intermediate").mkdir(parents=True, exist_ok=True)

    async def initialize(self) -> None:
        """Initialize Copilot SDK and create all agents."""
        console.print("[bold blue]Initializing Research Assistant...[/bold blue]")

        # Initialize orchestrator
        await self.orchestrator.initialize()

        # Create all configured agents
        for agent_name, config in self.agent_configs.items():
            console.print(f"Creating agent: {agent_name} ({config.model})")
            await self.orchestrator.create_agent(config)

        # Load existing state from files
        self.state.load_from_files()

        console.print("[bold green]✓ Research Assistant initialized[/bold green]\n")

    def load_data_description(self, file_path: str) -> None:
        """Load data description from file.

        Args:
            file_path: Path to data description markdown file
        """
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_dir / path

        if path.exists():
            self.state.data_description = path.read_text()
            console.print(f"[green]✓ Loaded data description from {path}[/green]")
        else:
            console.print(f"[red]✗ Data description file not found: {path}[/red]")

    async def generate_idea(self, mode: str = "interactive") -> None:
        """Generate research idea using multi-agent workflow.

        Args:
            mode: "interactive" for human-in-the-loop, "automatic" for full automation
        """
        console.print("\n[bold]Module 1: Idea Generation[/bold]\n")

        if not self.state.data_description:
            console.print("[red]Error: No data description loaded. Call load_data_description() first.[/red]")
            return

        # Import and run idea generation module
        from research_assistant.modules.idea import run_idea_generation

        await run_idea_generation(self.orchestrator, self.state, mode, self.project_dir)

        self.state.mark_module_complete("idea")
        console.print("[bold green]✓ Idea Generation complete[/bold green]\n")

    async def review_literature(self, mode: str = "interactive") -> None:
        """Conduct literature review.

        Args:
            mode: "interactive" for human-in-the-loop, "automatic" for full automation
        """
        console.print("\n[bold]Module 2: Literature Review[/bold]\n")

        if not self.state.idea:
            console.print("[yellow]Warning: No idea found. Loading from file...[/yellow]")
            self.state.load_from_files()

        # Import and run literature review module
        from research_assistant.modules.literature import run_literature_review

        await run_literature_review(self.orchestrator, self.state, mode, self.project_dir)

        self.state.mark_module_complete("literature")
        console.print("[bold green]✓ Literature Review complete[/bold green]\n")

    async def develop_methodology(self, mode: str = "interactive") -> None:
        """Develop research methodology.

        Args:
            mode: "interactive" for human-in-the-loop, "automatic" for full automation
        """
        console.print("\n[bold]Module 3: Methodology Development[/bold]\n")

        # Import and run methodology module
        from research_assistant.modules.methodology import run_methodology_development

        await run_methodology_development(self.orchestrator, self.state, mode, self.project_dir)

        self.state.mark_module_complete("methodology")
        console.print("[bold green]✓ Methodology Development complete[/bold green]\n")

    async def execute_analysis(
        self, mode: str = "interactive", require_approval: bool = True
    ) -> None:
        """Execute analysis with nested iteration loops.

        Args:
            mode: "interactive" for human-in-the-loop, "automatic" for full automation
            require_approval: Whether to require user approval before code execution
        """
        console.print("\n[bold]Module 4: Analysis Execution[/bold]\n")

        # Import and run analysis module
        from research_assistant.modules.analysis import run_analysis_execution

        await run_analysis_execution(
            self.orchestrator, self.state, mode, self.project_dir, require_approval
        )

        self.state.mark_module_complete("analysis")
        console.print("[bold green]✓ Analysis Execution complete[/bold green]\n")

    async def write_paper(
        self, mode: str = "interactive", journal_format: str = "nature"
    ) -> None:
        """Write research paper.

        Args:
            mode: "interactive" for human-in-the-loop, "automatic" for full automation
            journal_format: Target journal format (e.g., "nature", "science", "prl")
        """
        console.print("\n[bold]Module 5: Paper Writing[/bold]\n")

        # Import and run paper writing module
        from research_assistant.modules.paper import run_paper_writing

        await run_paper_writing(
            self.orchestrator, self.state, mode, self.project_dir, journal_format
        )

        self.state.mark_module_complete("paper")
        console.print("[bold green]✓ Paper Writing complete[/bold green]\n")

    async def review_paper(self, mode: str = "interactive") -> None:
        """Review and refine paper.

        Args:
            mode: "interactive" for human-in-the-loop, "automatic" for full automation
        """
        console.print("\n[bold]Module 6: Review & Refinement[/bold]\n")

        # Import and run review module
        from research_assistant.modules.review import run_paper_review

        await run_paper_review(self.orchestrator, self.state, mode, self.project_dir)

        self.state.mark_module_complete("review")
        console.print("[bold green]✓ Review & Refinement complete[/bold green]\n")

    async def cleanup(self) -> None:
        """Cleanup resources and close all sessions."""
        console.print("\n[bold]Cleaning up...[/bold]")
        await self.orchestrator.cleanup()
        console.print("[bold green]✓ Cleanup complete[/bold green]")


def prompt_user_review(file_path: Path, mode: str = "interactive") -> bool:
    """Prompt user to review and edit a file.

    Args:
        file_path: Path to file for review
        mode: "interactive" or "automatic"

    Returns:
        True if user wants to continue, False otherwise
    """
    if mode != "interactive":
        return True

    console.print(f"\n[yellow]📄 Output saved to: {file_path}[/yellow]")
    console.print("[yellow]Please review and edit the file if needed.[/yellow]\n")

    return Confirm.ask("Continue to next step?", default=True)
