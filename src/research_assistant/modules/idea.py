"""Idea generation module."""

from pathlib import Path
from rich.console import Console
from research_assistant.orchestrator import AgentOrchestrator
from research_assistant.state import ResearchState
from research_assistant.assistant import prompt_user_review


console = Console()


async def run_idea_generation(
    orchestrator: AgentOrchestrator,
    state: ResearchState,
    mode: str,
    project_dir: Path,
) -> None:
    """Run idea generation workflow with multi-agent refinement.

    Following Denario methodology:
    1. idea_maker generates 5 initial ideas
    2. idea_critic critiques all ideas
    3. idea_maker refines top 2 ideas
    4. idea_critic evaluates refined ideas
    5. idea_maker selects and finalizes best idea

    Args:
        orchestrator: Agent orchestrator
        state: Research state
        mode: "interactive" or "automatic"
        project_dir: Project directory path
    """
    output_dir = project_dir / "output"

    # Get context
    context = state.get_context_for_agent("idea_maker")

    # Step 1: Generate 5 initial ideas
    console.print("[cyan]Step 1/5: Generating initial ideas...[/cyan]")
    initial_prompt = """Based on the data description, generate 5 innovative research ideas. 
For each idea, provide:
- A clear, concise title
- A 5-sentence description explaining the research question, approach, and potential impact
- Why this idea is novel and feasible

Format each idea as:
## Idea N: [Title]
[5-sentence description]
"""

    initial_ideas = await orchestrator.send_to_agent("idea_maker", initial_prompt, context)
    state.add_agent_interaction("idea_maker", initial_prompt, initial_ideas)

    # Save initial ideas
    ideas_file_1 = output_dir / "01_initial_ideas.md"
    state.save_to_file(ideas_file_1, initial_ideas)

    if not prompt_user_review(ideas_file_1, mode):
        return

    # Reload in case user edited
    initial_ideas = ideas_file_1.read_text()

    # Step 2: Critique all ideas
    console.print("[cyan]Step 2/5: Critiquing ideas...[/cyan]")
    critique_prompt = f"""Review these 5 research ideas critically:

{initial_ideas}

For each idea, evaluate:
- Novelty: Is this truly innovative?
- Feasibility: Can this be done with available data/tools?
- Scientific rigor: Is the approach sound?
- Impact: What is the potential contribution?

Provide constructive criticism and rank the ideas from best to worst.
"""

    critique_1 = await orchestrator.send_to_agent("idea_critic", critique_prompt, context)
    state.add_agent_interaction("idea_critic", critique_prompt, critique_1)

    # Save critique
    critique_file_1 = output_dir / "02_critique.md"
    state.save_to_file(critique_file_1, critique_1)

    if not prompt_user_review(critique_file_1, mode):
        return

    # Reload in case user edited
    critique_1 = critique_file_1.read_text()

    # Step 3: Refine top 2 ideas
    console.print("[cyan]Step 3/5: Refining top ideas...[/cyan]")
    refine_prompt = f"""Based on the critique, take the top 2 ideas and refine them:

Original ideas:
{initial_ideas}

Critique:
{critique_1}

For the top 2 ideas:
1. Address the concerns raised in the critique
2. Strengthen the methodology
3. Clarify the research questions
4. Enhance the novelty and impact

Provide refined versions with improved descriptions.
"""

    refined_ideas = await orchestrator.send_to_agent("idea_maker", refine_prompt, context)
    state.add_agent_interaction("idea_maker", refine_prompt, refined_ideas)

    # Save refined ideas
    ideas_file_2 = output_dir / "03_refined_ideas.md"
    state.save_to_file(ideas_file_2, refined_ideas)

    if not prompt_user_review(ideas_file_2, mode):
        return

    # Reload in case user edited
    refined_ideas = ideas_file_2.read_text()

    # Step 4: Final critique
    console.print("[cyan]Step 4/5: Final evaluation...[/cyan]")
    final_critique_prompt = f"""Evaluate these refined research ideas:

{refined_ideas}

Compare the two ideas and recommend which one should be pursued based on:
- Scientific merit
- Feasibility
- Innovation
- Potential impact

Be specific about strengths and weaknesses of each.
"""

    critique_2 = await orchestrator.send_to_agent("idea_critic", final_critique_prompt, context)
    state.add_agent_interaction("idea_critic", final_critique_prompt, critique_2)

    # Save final critique
    critique_file_2 = output_dir / "04_final_critique.md"
    state.save_to_file(critique_file_2, critique_2)

    if not prompt_user_review(critique_file_2, mode):
        return

    # Reload in case user edited
    critique_2 = critique_file_2.read_text()

    # Step 5: Select final idea
    console.print("[cyan]Step 5/5: Finalizing idea...[/cyan]")
    final_prompt = f"""Based on all the feedback, select the best research idea and present it in final form:

Refined ideas:
{refined_ideas}

Final critique:
{critique_2}

Provide the selected idea with:
1. A clear, compelling title
2. A 5-sentence description that captures:
   - The research question
   - The proposed approach/methodology
   - Why it's novel
   - Expected outcomes
   - Potential impact

Format as a polished research idea ready for development.
"""

    final_idea = await orchestrator.send_to_agent("idea_maker", final_prompt, context)
    state.add_agent_interaction("idea_maker", final_prompt, final_idea)

    # Save final idea
    idea_file = output_dir / "idea.md"
    state.save_to_file(idea_file, final_idea)
    state.idea = final_idea
    
    # Save state before committing (so the commit includes the updated state)
    state.save_state(auto_commit=False)
    
    # Commit idea generation with descriptive message
    state.commit_step("idea", "generation", "Completed 5-step idea generation and refinement")

    console.print(f"[green]✓ Final idea saved to {idea_file}[/green]")

    if not prompt_user_review(idea_file, mode):
        return
    
    # Save state before committing user review
    state.save_state(auto_commit=False)
    
    # Commit user review with descriptive message
    state.commit_user_input("idea", "reviewed", "User reviewed and approved idea")
