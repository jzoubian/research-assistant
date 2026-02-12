"""Tool definitions for research agents."""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable
import aiofiles
from pydantic import BaseModel, Field


# Tool parameter models
class ReadFileParams(BaseModel):
    """Parameters for read_file tool."""

    file_path: str = Field(description="Relative path to file from project directory")


class WriteFileParams(BaseModel):
    """Parameters for write_file tool."""

    file_path: str = Field(description="Relative path to file from project directory")
    content: str = Field(description="Content to write to file")


class ExecuteCodeParams(BaseModel):
    """Parameters for execute_code tool."""

    code: str = Field(description="Python code to execute")
    timeout: int = Field(default=60, description="Execution timeout in seconds")


class CreatePlotParams(BaseModel):
    """Parameters for create_plot tool."""

    code: str = Field(description="Python code to generate plot using matplotlib")
    filename: str = Field(description="Output filename (without path, .png will be added)")


class SearchPapersParams(BaseModel):
    """Parameters for search_papers tool."""

    query: str = Field(description="Search query for academic papers")
    max_results: int = Field(default=10, description="Maximum number of papers to return")


class GetExecutionErrorParams(BaseModel):
    """Parameters for get_execution_error tool."""

    error_id: str = Field(description="Error identifier from failed execution")


class SaveIntermediateAnalysisParams(BaseModel):
    """Parameters for save_intermediate_analysis tool."""

    iteration: int = Field(description="Iteration number")
    content: str = Field(description="Analysis content to save")
    reason: str = Field(description="Reason for this iteration")


def create_tools(project_dir: str, tool_names: list[str]) -> list[Callable]:
    """Create tool functions for an agent.

    Args:
        project_dir: Path to research project directory
        tool_names: List of tool names to create

    Returns:
        List of tool functions
    """
    project_path = Path(project_dir)
    tools = []

    # Tool implementations
    async def read_file(params: ReadFileParams) -> str:
        """Read content from a file in the project directory."""
        file_path = project_path / params.file_path
        if not file_path.exists():
            return f"Error: File '{params.file_path}' not found"

        try:
            async with aiofiles.open(file_path, "r") as f:
                content = await f.read()
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"

    async def write_file(params: WriteFileParams) -> str:
        """Write content to a file in the project directory."""
        file_path = project_path / params.file_path
        file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with aiofiles.open(file_path, "w") as f:
                await f.write(params.content)
            return f"Successfully wrote to {params.file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

    async def execute_code(params: ExecuteCodeParams) -> str:
        """Execute Python code in a sandboxed environment."""
        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(params.code)
                temp_file = f.name

            # Execute code with timeout
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=params.timeout,
                cwd=str(project_path),
            )

            # Cleanup
            os.unlink(temp_file)

            if result.returncode == 0:
                return f"Execution successful:\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            else:
                return f"Execution failed with return code {result.returncode}:\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

        except subprocess.TimeoutExpired:
            return f"Error: Code execution timed out after {params.timeout} seconds"
        except Exception as e:
            return f"Error executing code: {str(e)}"

    async def create_plot(params: CreatePlotParams) -> str:
        """Create a plot using matplotlib and save to plots directory."""
        plot_dir = project_path / "output" / "plots"
        plot_dir.mkdir(parents=True, exist_ok=True)

        # Ensure filename ends with .png
        filename = params.filename
        if not filename.endswith(".png"):
            filename += ".png"

        plot_path = plot_dir / filename

        # Add save command to code
        code_with_save = params.code
        if "plt.savefig" not in code_with_save:
            code_with_save += f"\nimport matplotlib.pyplot as plt\nplt.savefig('{plot_path}')\nplt.close()"

        try:
            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code_with_save)
                temp_file = f.name

            # Execute code
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(project_path),
            )

            # Cleanup
            os.unlink(temp_file)

            if result.returncode == 0 and plot_path.exists():
                return f"Plot saved successfully to {plot_path.relative_to(project_path)}"
            else:
                return f"Error creating plot:\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"

        except Exception as e:
            return f"Error creating plot: {str(e)}"

    async def search_papers(params: SearchPapersParams) -> str:
        """Search for academic papers using arXiv API."""
        try:
            import arxiv

            # Search arXiv
            search = arxiv.Search(
                query=params.query, max_results=params.max_results, sort_by=arxiv.SortCriterion.Relevance
            )

            results = []
            for paper in search.results():
                results.append(
                    {
                        "title": paper.title,
                        "authors": [author.name for author in paper.authors],
                        "summary": paper.summary,
                        "published": paper.published.strftime("%Y-%m-%d"),
                        "pdf_url": paper.pdf_url,
                        "arxiv_id": paper.entry_id.split("/")[-1],
                    }
                )

            if not results:
                return f"No papers found for query: {params.query}"

            # Format results
            formatted = [f"Found {len(results)} papers:\n"]
            for i, paper in enumerate(results, 1):
                formatted.append(f"\n{i}. **{paper['title']}**")
                formatted.append(f"   Authors: {', '.join(paper['authors'][:3])}")
                if len(paper['authors']) > 3:
                    formatted.append(f" et al.")
                formatted.append(f"   Published: {paper['published']}")
                formatted.append(f"   arXiv ID: {paper['arxiv_id']}")
                formatted.append(f"   Summary: {paper['summary'][:200]}...")

            return "\n".join(formatted)

        except Exception as e:
            return f"Error searching papers: {str(e)}"

    async def get_execution_error(params: GetExecutionErrorParams) -> str:
        """Get detailed error information from failed execution."""
        # This is a placeholder - in practice, errors would be stored and retrieved
        return f"Error details for {params.error_id}: See execution output above"

    async def save_intermediate_analysis(params: SaveIntermediateAnalysisParams) -> str:
        """Save intermediate analysis results during iterations."""
        intermediate_dir = project_path / "output" / "intermediate"
        intermediate_dir.mkdir(parents=True, exist_ok=True)

        filename = f"analysis_{params.iteration:02d}.md"
        file_path = intermediate_dir / filename

        content = f"""# Analysis Iteration {params.iteration}

## Reason for Iteration
{params.reason}

## Analysis Results
{params.content}

---
Generated on: {__import__('datetime').datetime.now().isoformat()}
"""

        try:
            async with aiofiles.open(file_path, "w") as f:
                await f.write(content)
            return f"Saved intermediate analysis to {file_path.relative_to(project_path)}"
        except Exception as e:
            return f"Error saving intermediate analysis: {str(e)}"

    # Map tool names to functions
    tool_map = {
        "read_file": read_file,
        "write_file": write_file,
        "execute_code": execute_code,
        "create_plot": create_plot,
        "search_papers": search_papers,
        "get_execution_error": get_execution_error,
        "save_intermediate_analysis": save_intermediate_analysis,
    }

    # Create requested tools
    for tool_name in tool_names:
        if tool_name in tool_map:
            tools.append(tool_map[tool_name])

    return tools
