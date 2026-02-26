"""Methodology development module."""

from pathlib import Path
from rich.console import Console
from research_assistant.orchestrator import AgentOrchestrator
from research_assistant.state import ResearchState
from research_assistant.assistant import prompt_user_review


console = Console()


async def run_methodology_development(
    orchestrator: AgentOrchestrator,
    state: ResearchState,
    mode: str,
    project_dir: Path,
) -> None:
    """Run methodology development workflow.

    Multi-agent pattern: methodologist + engineer + analyst

    Args:
        orchestrator: Agent orchestrator
        state: Research state
        mode: "interactive" or "automatic"
        project_dir: Project directory path
    """
    output_dir = project_dir / "output"

    # Get context
    context = state.get_context_for_agent("methodologist")

    # Step 1: Methodologist proposes methodology
    console.print("[cyan]Step 1/3: Developing methodology...[/cyan]")
    method_prompt = """Based on the research idea, literature review, and available data, develop a detailed methodology.

Your methodology should include:

## Overview
- Brief summary of the approach

## Data
- What data will be used
- How data will be processed/prepared
- Any data quality considerations

## Analysis Steps
- Detailed step-by-step analysis plan
- Statistical methods to be used
- Any modeling approaches

## Validation
- How results will be validated
- Quality checks and controls
- Potential limitations

## Expected Outputs
- What results/figures are expected
- How results will answer research question

Be specific and detailed enough that someone could implement this methodology.
"""

    methodology = await orchestrator.send_to_agent("methodologist", method_prompt, context)
    state.add_agent_interaction("methodologist", method_prompt, methodology)

    # Step 2: Engineer reviews technical feasibility
    console.print("[cyan]Step 2/3: Engineer reviewing feasibility...[/cyan]")
    engineer_prompt = f"""Review this methodology from a technical implementation perspective:

{methodology}

Evaluate:
- Can this be implemented with available tools (Python, numpy, scipy, matplotlib, etc.)?
- Are there any technical challenges or missing details?
- Are the proposed statistical methods appropriate?
- Can you foresee any implementation issues?

Provide specific feedback on:
- Technical feasibility
- Implementation suggestions
- Potential improvements
"""

    engineer_feedback = await orchestrator.send_to_agent("engineer", engineer_prompt, context)
    state.add_agent_interaction("engineer", engineer_prompt, engineer_feedback)

    # Step 3: Analyst reviews scientific validity
    console.print("[cyan]Step 3/3: Analyst reviewing scientific validity...[/cyan]")
    analyst_prompt = f"""Review this methodology from a scientific validity perspective:

{methodology}

Engineer feedback:
{engineer_feedback}

Evaluate:
- Is the approach scientifically sound?
- Will this methodology answer the research question?
- Are the statistical methods appropriate?
- Are there potential confounding factors?
- Are the validation steps sufficient?

Provide specific feedback on scientific rigor and validity.
"""

    analyst_feedback = await orchestrator.send_to_agent("analyst", analyst_prompt, context)
    state.add_agent_interaction("analyst", analyst_prompt, analyst_feedback)

    # Combine into final methodology document
    final_methodology = f"""{methodology}

---

## Technical Feasibility Review (Engineer)

{engineer_feedback}

---

## Scientific Validity Review (Analyst)

{analyst_feedback}
"""

    # Save methodology
    method_file = output_dir / "methodology.md"
    state.save_to_file(method_file, final_methodology)
    state.methodology = methodology
    
    # Save state before committing
    state.save_state(auto_commit=False)
    # Commit methodology generation
    state.commit_step("methodology", "generation", "Completed methodology development with engineer and analyst review")

    console.print(f"[green]✓ Methodology saved to {method_file}[/green]")

    if not prompt_user_review(method_file, mode):
        return
    
    # Save state before committing
    state.save_state(auto_commit=False)
    # Commit user review
    state.commit_user_input("methodology", "reviewed", "User reviewed and approved methodology")
