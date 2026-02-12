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

    console.print(f"[green]✓ Initialized research project at {project_dir}[/green]")
    console.print(f"\n[yellow]Next steps:[/yellow]")
    console.print(f"1. Edit {project_dir}/input/data_description.md")
    console.print(f"2. Run: research-assistant idea --project {project_dir}")


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
):
    """Run complete research workflow."""
    async def run_workflow():
        assistant = ResearchAssistant(project_dir=project)
        await assistant.initialize()

        mode = "interactive" if interactive else "automatic"
        modules = ["idea", "literature", "methodology", "analysis", "paper", "review"]

        # Determine starting point
        start_index = 0
        if start_from:
            if start_from in modules:
                start_index = modules.index(start_from)
            else:
                console.print(f"[red]Invalid module: {start_from}[/red]")
                return

        # Load data description if starting from beginning
        if start_index == 0:
            assistant.load_data_description("input/data_description.md")

        # Execute modules
        if start_index <= 0:
            console.print("\n[bold cyan]Starting Module 1: Idea Generation[/bold cyan]")
            await assistant.generate_idea(mode=mode)

        if start_index <= 1:
            console.print("\n[bold cyan]Starting Module 2: Literature Review[/bold cyan]")
            await assistant.review_literature(mode=mode)

        if start_index <= 2:
            console.print("\n[bold cyan]Starting Module 3: Methodology Development[/bold cyan]")
            await assistant.develop_methodology(mode=mode)

        if start_index <= 3:
            console.print("\n[bold cyan]Starting Module 4: Analysis Execution[/bold cyan]")
            await assistant.execute_analysis(mode=mode, require_approval=approve_code)

        if start_index <= 4:
            console.print("\n[bold cyan]Starting Module 5: Paper Writing[/bold cyan]")
            await assistant.write_paper(mode=mode, journal_format=journal_format)

        if start_index <= 5:
            console.print("\n[bold cyan]Starting Module 6: Review & Refinement[/bold cyan]")
            await assistant.review_paper(mode=mode)

        await assistant.cleanup()

        console.print("\n[bold green]✓ Complete research workflow finished![/bold green]")

    asyncio.run(run_workflow())


@app.command()
def resume(
    project: str = typer.Argument(..., help="Path to research project"),
    from_module: str = typer.Option(..., "--from", help="Module to resume from"),
    interactive: bool = typer.Option(True, help="Interactive mode with user reviews"),
):
    """Resume research workflow from a specific module."""
    run(project=project, interactive=interactive, start_from=from_module)


if __name__ == "__main__":
    app()
