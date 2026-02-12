"""Command-line interface for research assistant."""

import asyncio
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console

from research_assistant import ResearchAssistant


app = typer.Typer(help="Personal Research Assistant CLI")
console = Console()


@app.command()
def init(
    project_name: str = typer.Argument(..., help="Name of the research project"),
    path: Optional[str] = typer.Option(None, help="Path where project should be created"),
    env_manager: str = typer.Option("pixi", help="Environment manager (pixi, apptainer, nix, guix)"),
):
    """Initialize a new research project."""
    if path:
        project_dir = Path(path) / project_name
    else:
        project_dir = Path.cwd() / project_name

    project_dir.mkdir(parents=True, exist_ok=True)

    # Create directory structure
    (project_dir / "input").mkdir(exist_ok=True)
    (project_dir / "output").mkdir(exist_ok=True)
    (project_dir / "output" / "plots").mkdir(exist_ok=True)
    (project_dir / "output" / "code").mkdir(exist_ok=True)
    (project_dir / "output" / "intermediate").mkdir(exist_ok=True)

    # Create template data description
    data_desc_template = """# Data Description

## Overview
Describe your available data, tools, and computational resources.

## Data Sources
- Source 1: [Description]
- Source 2: [Description]

## Available Tools
- Tool 1: [Description]
- Tool 2: [Description]

## Research Context
Describe the scientific domain, key questions of interest, and any constraints.
"""

    (project_dir / "input" / "data_description.md").write_text(data_desc_template)
    
    # Create initial state file with env manager preference
    from research_assistant.state import ResearchState
    from research_assistant.config_manager import ConfigManager
    
    state = ResearchState(project_dir=project_dir, env_manager=env_manager)
    
    # Initialize default resources
    if state.resource_manager:
        state.resource_manager.create_default_resources()
        state.resource_manager.save_resources()
    
    # Create default configuration
    config_mgr = ConfigManager(project_dir)
    config_mgr.create_default_config(project_name)
    config_mgr.config.env_manager = env_manager
    config_mgr.save_config()
    
    state.save_state()

    console.print(f"[green]✓ Initialized research project at {project_dir}[/green]")
    console.print(f"[green]✓ Environment manager: {env_manager}[/green]")
    console.print(f"[green]✓ Default resources configured[/green]")
    console.print(f"[green]✓ Configuration file created: research_config.toml[/green]")
    console.print(f"\n[yellow]Next steps:[/yellow]")
    console.print(f"1. Review/edit config: {project_dir}/research_config.toml")
    console.print(f"2. Configure resources: research-assistant resources {project_name} --configure")
    console.print(f"3. Edit {project_dir}/input/data_description.md")
    console.print(f"4. Run: research-assistant run {project_dir}")


@app.command()
def idea(
    project: str = typer.Option(..., help="Path to research project"),
    interactive: bool = typer.Option(True, help="Interactive mode with user reviews"),
):
    """Generate research idea."""
    async def run():
        assistant = ResearchAssistant(project_dir=project)
        await assistant.initialize()
        assistant.load_data_description("input/data_description.md")
        mode = "interactive" if interactive else "automatic"
        await assistant.generate_idea(mode=mode)
        await assistant.cleanup()

    asyncio.run(run())


@app.command()
def literature(
    project: str = typer.Option(..., help="Path to research project"),
    interactive: bool = typer.Option(True, help="Interactive mode with user reviews"),
):
    """Conduct literature review."""
    async def run():
        assistant = ResearchAssistant(project_dir=project)
        await assistant.initialize()
        mode = "interactive" if interactive else "automatic"
        await assistant.review_literature(mode=mode)
        await assistant.cleanup()

    asyncio.run(run())


@app.command()
def methodology(
    project: str = typer.Option(..., help="Path to research project"),
    interactive: bool = typer.Option(True, help="Interactive mode with user reviews"),
):
    """Develop research methodology."""
    async def run():
        assistant = ResearchAssistant(project_dir=project)
        await assistant.initialize()
        mode = "interactive" if interactive else "automatic"
        await assistant.develop_methodology(mode=mode)
        await assistant.cleanup()

    asyncio.run(run())


@app.command()
def analysis(
    project: str = typer.Option(..., help="Path to research project"),
    interactive: bool = typer.Option(True, help="Interactive mode with user reviews"),
    approve_code: bool = typer.Option(True, help="Require approval before code execution"),
):
    """Execute analysis with nested iteration loops."""
    async def run():
        assistant = ResearchAssistant(project_dir=project)
        await assistant.initialize()
        mode = "interactive" if interactive else "automatic"
        await assistant.execute_analysis(mode=mode, require_approval=approve_code)
        await assistant.cleanup()

    asyncio.run(run())


@app.command()
def paper(
    project: str = typer.Option(..., help="Path to research project"),
    interactive: bool = typer.Option(True, help="Interactive mode with user reviews"),
    format: str = typer.Option("nature", help="Journal format (nature, science, prl, etc.)"),
):
    """Write research paper."""
    async def run():
        assistant = ResearchAssistant(project_dir=project)
        await assistant.initialize()
        mode = "interactive" if interactive else "automatic"
        await assistant.write_paper(mode=mode, journal_format=format)
        await assistant.cleanup()

    asyncio.run(run())


@app.command()
def review(
    project: str = typer.Option(..., help="Path to research project"),
    interactive: bool = typer.Option(True, help="Interactive mode with user reviews"),
):
    """Review and refine paper."""
    async def run():
        assistant = ResearchAssistant(project_dir=project)
        await assistant.initialize()
        mode = "interactive" if interactive else "automatic"
        await assistant.review_paper(mode=mode)
        await assistant.cleanup()

    asyncio.run(run())


@app.command()
def run(
    project: str = typer.Option(..., help="Path to research project"),
    interactive: bool = typer.Option(True, help="Interactive mode with user reviews"),
    start_from: Optional[str] = typer.Option(None, help="Start from specific module (idea, literature, methodology, analysis, paper, review)"),
    approve_code: bool = typer.Option(True, help="Require approval before code execution"),
    journal_format: str = typer.Option("nature", help="Journal format for paper"),
    env_manager: Optional[str] = typer.Option(None, help="Environment manager override (pixi, apptainer, nix, guix)"),
):
    """Run complete research workflow."""
    from research_assistant.state import ResearchState
    from research_assistant.config_manager import ConfigManager
    
    project_dir = Path(project).resolve()
    
    # Load configuration
    config_mgr = ConfigManager(project_dir)
    if config_mgr.load_config():
        console.print(f"[green]Loaded configuration from research_config.toml[/green]")
        console.print(config_mgr.get_summary())
        
        # Override with CLI args if provided
        config_mgr.update_from_cli_args(
            mode="interactive" if interactive else "autonomous",
            require_code_approval=approve_code,
            env_manager=env_manager,
        )
    else:
        console.print(f"[yellow]No config file found, using defaults[/yellow]")
    
    # Load existing state or create new one
    try:
        state = ResearchState.load_state(project_dir)
        if env_manager:
            state.env_manager = env_manager  # Override if specified
        elif config_mgr.config:
            state.env_manager = config_mgr.config.env_manager
        console.print(f"[green]Loaded existing project state[/green]")
    except FileNotFoundError:
        state = ResearchState(project_dir=project_dir, env_manager=env_manager or "pixi")
        console.print(f"[yellow]No existing state found, creating new project[/yellow]")
    
    assistant = ResearchAssistant(state, env_manager=state.env_manager)

    try:
        assistant.initialize()

        mode = "interactive" if interactive else "autonomous"
        
        # Use run_from_module if start_from is specified
        if start_from:
            console.print(f"\n[bold]Starting workflow from module: {start_from}[/bold]\n")
            assistant.run_from_module(start_from, mode, require_approval=approve_code, journal_format=journal_format)
        else:
            console.print(f"\n[bold]Starting complete research workflow in {mode} mode[/bold]\n")
            assistant.run_idea_generation(mode)
            assistant.run_literature_review(mode)
            assistant.run_methodology_design(mode)
            assistant.run_analysis_execution(mode, require_approval=approve_code)
            assistant.run_paper_writing(mode, journal_format=journal_format)
            assistant.run_review_synthesis(mode)

        console.print("\n[bold green]✓ Complete research workflow finished![/bold green]")

    finally:
        assistant.cleanup()


@app.command()
def resume(
    project: str = typer.Argument(..., help="Path to research project"),
    from_module: str = typer.Option(..., "--from", help="Module to resume from"),
    interactive: bool = typer.Option(True, help="Interactive mode with user reviews"),
    env_manager: Optional[str] = typer.Option(None, help="Environment manager override"),
):
    """Resume research workflow from a specific module."""
    run(project=project, interactive=interactive, start_from=from_module, env_manager=env_manager)


@app.command()
def iterations(
    project: str = typer.Argument(..., help="Path to research project"),
    module: Optional[str] = typer.Option(None, help="Show iterations for specific module"),
):
    """Display iteration history for the project."""
    from research_assistant.state import ResearchState
    from rich.table import Table
    
    project_dir = Path(project).resolve()
    
    try:
        state = ResearchState.load_state(project_dir)
    except FileNotFoundError:
        console.print(f"[red]No project state found at {project_dir}[/red]")
        raise typer.Exit(1)
    
    if module:
        # Show iterations for specific module
        iterations = state.module_iterations.get(module, [])
        if not iterations:
            console.print(f"[yellow]No iterations found for module: {module}[/yellow]")
            return
        
        console.print(f"\n[bold cyan]Iteration History for {module.upper()}[/bold cyan]\n")
        
        for iter_data in iterations:
            table = Table(title=f"Iteration {iter_data.iteration}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Timestamp", str(iter_data.timestamp))
            table.add_row("Status", iter_data.status)
            table.add_row("Input Files", ", ".join(str(f) for f in iter_data.input_files))
            table.add_row("Output Files", ", ".join(str(f) for f in iter_data.output_files))
            table.add_row("Notes", iter_data.notes)
            
            console.print(table)
            console.print()
    else:
        # Show summary for all modules
        console.print("\n[bold cyan]Iteration Summary for All Modules[/bold cyan]\n")
        
        table = Table()
        table.add_column("Module", style="cyan")
        table.add_column("Iterations", justify="right", style="green")
        table.add_column("Last Run", style="yellow")
        table.add_column("Status", style="white")
        
        for module_name in ["idea", "literature", "methodology", "analysis", "paper", "review"]:
            count = state.get_module_iteration_count(module_name)
            if count > 0:
                latest = state.get_latest_iteration(module_name)
                table.add_row(
                    module_name.upper(),
                    str(count),
                    str(latest.timestamp) if latest else "-",
                    latest.status if latest else "-"
                )
            else:
                table.add_row(module_name.upper(), "0", "-", "-")
        
        console.print(table)
        console.print(f"\n[dim]Use --module to see detailed iteration history for a specific module[/dim]")


@app.command()
def config(
    project: str = typer.Argument(..., help="Path to research project"),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    edit: bool = typer.Option(False, "--edit", help="Open config file in editor"),
    validate: bool = typer.Option(False, "--validate", help="Validate configuration"),
    export_template: bool = typer.Option(False, "--export-template", help="Export configuration template"),
    output: Optional[str] = typer.Option(None, "--output", help="Output path for template export"),
):
    """Manage project configuration."""
    from research_assistant.config_manager import ConfigManager
    import subprocess
    import os
    
    project_dir = Path(project).resolve()
    config_mgr = ConfigManager(project_dir)
    
    if export_template:
        output_path = Path(output) if output else Path("research_config_template.toml")
        if config_mgr.export_template(output_path):
            console.print(f"[green]✓ Template exported to {output_path}[/green]")
        else:
            console.print(f"[red]Failed to export template[/red]")
        return
    
    if not config_mgr.load_config():
        console.print(f"[red]No configuration file found at {config_mgr.config_file}[/red]")
        console.print(f"[yellow]Run 'research-assistant init' to create a project[/yellow]")
        raise typer.Exit(1)
    
    if validate:
        is_valid, errors = config_mgr.validate_config()
        if is_valid:
            console.print("[green]✓ Configuration is valid[/green]")
        else:
            console.print("[red]✗ Configuration has errors:[/red]")
            for error in errors:
                console.print(f"  - {error}")
        return
    
    if edit:
        editor = os.environ.get('EDITOR', 'nano')
        try:
            subprocess.run([editor, str(config_mgr.config_file)])
            console.print("[green]✓ Configuration file closed[/green]")
            
            # Validate after editing
            if config_mgr.load_config():
                is_valid, errors = config_mgr.validate_config()
                if is_valid:
                    console.print("[green]✓ Configuration is valid[/green]")
                else:
                    console.print("[yellow]⚠ Configuration has warnings:[/yellow]")
                    for error in errors:
                        console.print(f"  - {error}")
        except Exception as e:
            console.print(f"[red]Failed to open editor: {e}[/red]")
        return
    
    if show or True:  # Default action
        console.print("\n[bold cyan]Project Configuration[/bold cyan]\n")
        console.print(config_mgr.get_summary())
        console.print(f"\n[dim]Config file: {config_mgr.config_file}[/dim]")
        console.print(f"[dim]Use --edit to modify configuration[/dim]")


@app.command()
def resources(
    project: str = typer.Argument(..., help="Path to research project"),
    configure: bool = typer.Option(False, "--configure", help="Interactively configure resources"),
    show: bool = typer.Option(False, "--show", help="Show current resource configuration"),
):
    """Manage computational resources and constraints."""
    from research_assistant.state import ResearchState
    from research_assistant.resources import ComputeResource, ResourceConstraints
    from rich.prompt import Prompt, Confirm
    
    project_dir = Path(project).resolve()
    
    try:
        state = ResearchState.load_state(project_dir)
    except FileNotFoundError:
        console.print(f"[red]No project state found at {project_dir}[/red]")
        raise typer.Exit(1)
    
    if not state.resource_manager:
        console.print(f"[red]Resource manager not available[/red]")
        raise typer.Exit(1)
    
    if show or (not configure):
        # Show current resources
        console.print(state.resource_manager.get_resource_summary())
        return
    
    if configure:
        console.print("[bold cyan]Configure Computational Resources[/bold cyan]\n")
        
        # CPU configuration
        cpu_cores = Prompt.ask("CPU cores available", default=str(state.resource_manager.resources.cpu_cores or "4"))
        cpu_memory = Prompt.ask("RAM available (GB)", default=str(state.resource_manager.resources.cpu_memory_gb or "8"))
        
        # GPU configuration
        gpu_available = Confirm.ask("GPU available?", default=state.resource_manager.resources.gpu_available)
        gpu_count = None
        gpu_type = None
        gpu_memory = None
        if gpu_available:
            gpu_count = Prompt.ask("Number of GPUs", default="1")
            gpu_type = Prompt.ask("GPU type (e.g., A100, V100, RTX4090)", default="")
            gpu_memory = Prompt.ask("GPU memory per device (GB)", default="")
        
        # Cluster configuration
        cluster_available = Confirm.ask("Cluster/HPC access available?", default=state.resource_manager.resources.cluster_available)
        cluster_type = None
        cluster_partition = None
        if cluster_available:
            cluster_type = Prompt.ask("Cluster type", choices=["SLURM", "PBS", "SGE"], default="SLURM")
            cluster_partition = Prompt.ask("Default partition/queue", default="")
        
        # MPI/OpenMP
        mpi_available = Confirm.ask("MPI available?", default=state.resource_manager.resources.mpi_available)
        
        # Update resources
        state.resource_manager.resources = ComputeResource(
            cpu_cores=int(cpu_cores),
            cpu_memory_gb=float(cpu_memory),
            gpu_available=gpu_available,
            gpu_count=int(gpu_count) if gpu_count and gpu_available else None,
            gpu_type=gpu_type if gpu_type and gpu_available else None,
            gpu_memory_gb=float(gpu_memory) if gpu_memory and gpu_available else None,
            cluster_available=cluster_available,
            cluster_type=cluster_type if cluster_available else None,
            cluster_partition=cluster_partition if cluster_partition and cluster_available else None,
            mpi_available=mpi_available,
            openmp_available=True,
            internet_access=True,
        )
        
        # Constraints
        console.print("\n[bold cyan]Configure Resource Constraints[/bold cyan]\n")
        
        max_memory = Prompt.ask("Max memory per job (GB)", default=str(float(cpu_memory) * 0.8))
        max_cpu = Prompt.ask("Max CPUs per job", default=cpu_cores)
        max_runtime = Prompt.ask("Max runtime per job (hours)", default="")
        
        has_quota = Confirm.ask("Resource quota exists?", default=False)
        quota_details = None
        if has_quota:
            quota_details = Prompt.ask("Quota details")
        
        state.resource_manager.constraints = ResourceConstraints(
            max_memory_per_job_gb=float(max_memory),
            max_cpu_per_job=int(max_cpu),
            max_runtime_hours=float(max_runtime) if max_runtime else None,
            has_quota=has_quota,
            quota_details=quota_details if has_quota else None,
            prefer_parallel=True,
        )
        
        # Save
        state.resource_manager.save_resources()
        console.print("\n[green]✓ Resources configured and saved[/green]\n")
        console.print(state.resource_manager.get_resource_summary())


if __name__ == "__main__":
    app()
