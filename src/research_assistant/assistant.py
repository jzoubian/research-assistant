"""Main ResearchAssistant class."""

from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.prompt import Confirm

from research_assistant.config import AgentConfig, DEFAULT_AGENTS
from research_assistant.state import ResearchState
from research_assistant.orchestrator import AgentOrchestrator
from research_assistant.environment import EnvironmentManager


console = Console()


class ResearchAssistant:
    """Main research assistant orchestrator."""

    def __init__(
        self,
        project_dir: str,
        agent_configs: Optional[dict[str, AgentConfig]] = None,
        env_manager: str = "pixi",
    ):
        """Initialize research assistant.

        Args:
            project_dir: Path to research project directory
            agent_configs: Custom agent configurations (defaults to DEFAULT_AGENTS)
            env_manager: Environment manager type (pixi, conda, venv, docker)
        """
        self.project_dir = Path(project_dir)
        self.agent_configs = agent_configs or DEFAULT_AGENTS
        self.orchestrator = AgentOrchestrator(str(self.project_dir))
        
        # Try to load existing state, otherwise create new
        loaded_state = ResearchState.load_state(self.project_dir)
        if loaded_state:
            self.state = loaded_state
            console.print("[yellow]Loaded existing research state[/yellow]")
        else:
            self.state = ResearchState(project_dir=self.project_dir, env_manager=env_manager)
        
        # Initialize environment manager
        self.env_manager = EnvironmentManager(self.project_dir, env_manager)

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
        
        # Initialize environment for code execution
        console.print(f"[cyan]Initializing {self.state.env_manager} environment...[/cyan]")
        env_success = self.env_manager.initialize_environment()
        if env_success:
            console.print(f"[green]✓ {self.state.env_manager} environment ready[/green]")
        else:
            console.print(f"[yellow]⚠ {self.state.env_manager} initialization failed, code execution may not work[/yellow]")

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
            self.orchestrator, self.state, mode, self.project_dir, require_approval, self.env_manager
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
        
        # Save state before cleanup
        self.state.save_state()
        console.print("[green]✓ State saved[/green]")
        
        await self.orchestrator.cleanup()
        console.print("[bold green]✓ Cleanup complete[/bold green]")
    
    async def run_from_module(self, start_module: str, mode: str = "interactive", **kwargs) -> None:
        """Run all modules starting from a specific module.
        
        Args:
            start_module: Module to start from (idea, literature, methodology, analysis, paper, review)
            mode: "interactive" or "automatic"
            **kwargs: Additional arguments for specific modules
        """
        modules = ["idea", "literature", "methodology", "analysis", "paper", "review"]
        
        if start_module not in modules:
            console.print(f"[red]Error: Unknown module '{start_module}'[/red]")
            return
        
        start_index = modules.index(start_module)
        
        console.print(f"\n[bold cyan]Running modules from '{start_module}' onwards...[/bold cyan]\n")
        
        for i in range(start_index, len(modules)):
            module = modules[i]
            
            if module == "idea":
                await self.generate_idea(mode=mode)
            elif module == "literature":
                await self.review_literature(mode=mode)
            elif module == "methodology":
                await self.develop_methodology(mode=mode)
            elif module == "analysis":
                require_approval = kwargs.get("require_approval", True)
                await self.execute_analysis(mode=mode, require_approval=require_approval)
            elif module == "paper":
                journal_format = kwargs.get("journal_format", "nature")
                await self.write_paper(mode=mode, journal_format=journal_format)
            elif module == "review":
                await self.review_paper(mode=mode)
        
        console.print("\n[bold green]✓ All modules from '{start_module}' completed![/bold green]")


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
