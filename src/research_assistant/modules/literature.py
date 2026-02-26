"""Literature review module."""

from pathlib import Path
from rich.console import Console
from research_assistant.orchestrator import AgentOrchestrator
from research_assistant.state import ResearchState
from research_assistant.assistant import prompt_user_review


console = Console()


async def run_literature_review(
    orchestrator: AgentOrchestrator,
    state: ResearchState,
    mode: str,
    project_dir: Path,
) -> None:
    """Run literature review workflow.

    Args:
        orchestrator: Agent orchestrator
        state: Research state
        mode: "interactive" or "automatic"
        project_dir: Project directory path
    """
    output_dir = project_dir / "output"

    # Get context
    context = state.get_context_for_agent("literature_researcher")

    # Step 1: Search for relevant papers
    console.print("[cyan]Step 1/2: Searching for relevant papers...[/cyan]")
    search_prompt = """Based on the research idea, identify relevant academic papers.

**IMPORTANT EFFICIENCY GUIDELINES:**
- For well-known datasets (Iris, MNIST, Wine, Titanic, etc.): Use your knowledge base ONLY, do NOT call search_papers
- For novel research: Call search_papers ONCE with a comprehensive query (max_results=5)
- Limit: Maximum 1-2 search_papers calls total

**For well-known/benchmark datasets:**
Cite foundational papers from your knowledge:
- Original dataset papers
- Classic methodology papers
- Well-known review papers

**For novel/specialized research:**
Use search_papers tool with ONE comprehensive query combining your search terms.

Search for papers that:
1. Address similar research questions
2. Use similar methodologies  
3. Provide relevant background/context
4. Identify gaps in current knowledge
"""

    # Use moderate timeout for literature search
    papers_response = await orchestrator.send_to_agent(
        "literature_researcher", search_prompt, context, timeout=300
    )
    state.add_agent_interaction("literature_researcher", search_prompt, papers_response)

    # Step 2: Synthesize literature review
    console.print("[cyan]Step 2/2: Synthesizing literature review...[/cyan]")
    synthesis_prompt = f"""Based on the papers found, write a comprehensive literature review.

Papers found:
{papers_response}

Your literature review should include:

## Background
- Overview of the research area
- Key concepts and definitions
- Current state of knowledge

## Related Work
- Summary of relevant studies
- Key findings from the literature
- Methodological approaches used

## Research Gap
- What is missing in current research
- Why our proposed idea addresses this gap
- How our approach differs from existing work

## References
- Properly formatted citations for all papers mentioned

Write in academic style suitable for a research paper.
"""

    literature = await orchestrator.send_to_agent(
        "literature_researcher", synthesis_prompt, context
    )
    state.add_agent_interaction("literature_researcher", synthesis_prompt, literature)

    # Step 3: Analyst review
    console.print("[cyan]Analyst reviewing literature synthesis...[/cyan]")
    review_prompt = f"""Review this literature review for completeness and quality:

{literature}

Evaluate:
- Are key papers in the field covered?
- Is the research gap clearly identified?
- Are the connections to our research idea clear?
- Is the writing clear and well-structured?

Provide feedback on what should be improved or added.
"""

    analyst_feedback = await orchestrator.send_to_agent("analyst", review_prompt, context)
    state.add_agent_interaction("analyst", review_prompt, analyst_feedback)

    # Save literature review
    lit_file = output_dir / "literature.md"
    final_literature = f"""{literature}

---

## Analyst Feedback

{analyst_feedback}
"""

    state.save_to_file(lit_file, final_literature)
    state.literature = literature
    
    # Save state before committing
    state.save_state(auto_commit=False)
    # Commit literature generation
    state.commit_step("literature", "generation", "Completed literature search and synthesis with analyst review")

    console.print(f"[green]✓ Literature review saved to {lit_file}[/green]")

    if not prompt_user_review(lit_file, mode):
        return
    
    # Save state before committing
    state.save_state(auto_commit=False)
    # Commit user review
    state.commit_user_input("literature", "reviewed", "User reviewed and approved literature")
