"""Paper writing module."""

from pathlib import Path
from rich.console import Console
from research_assistant.orchestrator import AgentOrchestrator
from research_assistant.state import ResearchState
from research_assistant.assistant import prompt_user_review


console = Console()


async def run_paper_writing(
    orchestrator: AgentOrchestrator,
    state: ResearchState,
    mode: str,
    project_dir: Path,
    journal_format: str = "nature",
) -> None:
    """Run paper writing workflow.

    Multi-agent pattern: writer ↔ reviewer

    Args:
        orchestrator: Agent orchestrator
        state: Research state
        mode: "interactive" or "automatic"
        project_dir: Project directory path
        journal_format: Target journal format
    """
    output_dir = project_dir / "output"

    # Get context
    context = state.get_context_for_agent("writer")
    context["journal_format"] = journal_format

    # Step 1: Writer creates initial manuscript
    console.print("[cyan]Step 1/3: Writing manuscript...[/cyan]")
    write_prompt = f"""Write a complete research paper manuscript in markdown format.

Target journal: {journal_format}

Use all available research materials:
- Idea: {state.idea[:200]}...
- Literature review: Available in context
- Methodology: Available in context
- Analysis results: {state.analysis[:300]}...

Structure the paper with:

# Title
[Compelling title based on the research idea]

## Abstract
[150-250 words summarizing the research]

## Introduction
- Background and motivation
- Research question
- Significance and novelty

## Literature Review / Related Work
[Based on the literature review]

## Methodology
[Based on the methodology section]

## Results
[Based on the analysis results]
- Include references to figures/plots
- Present key findings clearly

## Discussion
- Interpretation of results
- Implications
- Limitations
- Future work

## Conclusions
[Summary of contributions and findings]

## References
[All citations]

Write in professional academic style appropriate for {journal_format}.
"""

    manuscript = await orchestrator.send_to_agent("writer", write_prompt, context)
    state.add_agent_interaction("writer", write_prompt, manuscript)

    # Step 2: Reviewer provides feedback
    console.print("[cyan]Step 2/3: Reviewer providing feedback...[/cyan]")
    review_prompt = f"""Review this manuscript and provide detailed editorial feedback:

{manuscript}

Evaluate:
- Clarity and organization
- Scientific rigor
- Logical flow
- Writing quality
- Completeness
- Citations and references
- Figures and tables

Provide specific suggestions for improvement.
"""

    reviewer_feedback = await orchestrator.send_to_agent("reviewer", review_prompt, context)
    state.add_agent_interaction("reviewer", review_prompt, reviewer_feedback)

    # Step 3: Writer implements feedback
    console.print("[cyan]Step 3/3: Incorporating feedback...[/cyan]")
    revise_prompt = f"""Revise the manuscript based on reviewer feedback:

Original manuscript:
{manuscript}

Reviewer feedback:
{reviewer_feedback}

Provide the revised manuscript incorporating all suggestions.
"""

    revised_manuscript = await orchestrator.send_to_agent("writer", revise_prompt, context)
    state.add_agent_interaction("writer", revise_prompt, revised_manuscript)

    # Save paper
    paper_file = output_dir / "paper.md"
    final_paper = f"""{revised_manuscript}

---

## Reviewer Feedback

{reviewer_feedback}
"""

    state.save_to_file(paper_file, final_paper)
    state.paper = revised_manuscript

    console.print(f"[green]✓ Paper saved to {paper_file}[/green]")

    if not prompt_user_review(paper_file, mode):
        return
