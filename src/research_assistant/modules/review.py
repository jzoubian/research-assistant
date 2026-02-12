"""Review and refinement module."""

from pathlib import Path
from rich.console import Console
from research_assistant.orchestrator import AgentOrchestrator
from research_assistant.state import ResearchState
from research_assistant.assistant import prompt_user_review


console = Console()


async def run_paper_review(
    orchestrator: AgentOrchestrator,
    state: ResearchState,
    mode: str,
    project_dir: Path,
) -> None:
    """Run final paper review and refinement.

    Args:
        orchestrator: Agent orchestrator
        state: Research state
        mode: "interactive" or "automatic"
        project_dir: Project directory path
    """
    output_dir = project_dir / "output"

    # Get context
    context = state.get_context_for_agent("reviewer")

    # Step 1: Comprehensive review
    console.print("[cyan]Step 1/2: Conducting final review...[/cyan]")
    review_prompt = """Conduct a comprehensive editorial review of the paper.

Check for:
- Scientific accuracy and rigor
- Logical consistency across sections
- Clarity and readability
- Proper citations
- Figure references
- Grammar and style
- Adherence to academic standards

Provide:
1. Overall assessment
2. Major issues (if any)
3. Minor suggestions
4. Final recommendation
"""

    final_review = await orchestrator.send_to_agent("reviewer", review_prompt, context)
    state.add_agent_interaction("reviewer", review_prompt, final_review)

    # Step 2: Final improvements
    console.print("[cyan]Step 2/2: Implementing final improvements...[/cyan]")
    improve_prompt = f"""Make final improvements to the paper based on this review:

{final_review}

Provide the final, polished version of the manuscript ready for submission.
"""

    final_paper = await orchestrator.send_to_agent("writer", improve_prompt, context)
    state.add_agent_interaction("writer", improve_prompt, final_paper)

    # Save final paper
    final_file = output_dir / "paper_final.md"
    review_file = output_dir / "review_notes.md"

    state.save_to_file(final_file, final_paper)
    state.save_to_file(review_file, final_review)

    console.print(f"[green]✓ Final paper saved to {final_file}[/green]")
    console.print(f"[green]✓ Review notes saved to {review_file}[/green]")

    if not prompt_user_review(final_file, mode):
        return
