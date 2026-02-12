"""Analysis execution module with nested iteration loops."""

from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm
from research_assistant.orchestrator import AgentOrchestrator
from research_assistant.state import ResearchState
from research_assistant.assistant import prompt_user_review


console = Console()


async def run_analysis_execution(
    orchestrator: AgentOrchestrator,
    state: ResearchState,
    mode: str,
    project_dir: Path,
    require_approval: bool = True,
) -> None:
    """Run analysis execution with nested iteration loops.

    Nested loops:
    - Outer loop: Analyst-driven scientific refinement (max ~5 iterations)
    - Inner loop: Engineer-executor debugging (max ~10 attempts per iteration)

    Args:
        orchestrator: Agent orchestrator
        state: Research state
        mode: "interactive" or "automatic"
        project_dir: Project directory path
        require_approval: Whether to require user approval before code execution
    """
    output_dir = project_dir / "output"
    code_dir = output_dir / "code"
    code_dir.mkdir(parents=True, exist_ok=True)

    # Get context
    context = state.get_context_for_agent("engineer")

    max_analysis_iterations = 5
    max_debug_attempts = 10

    analysis_complete = False
    analysis_iteration = 0

    # Outer loop: Analyst-driven refinement
    while not analysis_complete and analysis_iteration < max_analysis_iterations:
        analysis_iteration += 1
        console.print(f"\n[bold magenta]Analysis Iteration {analysis_iteration}/{max_analysis_iterations}[/bold magenta]")

        # Determine what to analyze
        if analysis_iteration == 1:
            analysis_request = "Implement the complete analysis methodology as specified."
        else:
            # Analyst requests additional analysis
            console.print("[cyan]Analyst determining next steps...[/cyan]")
            analyst_review_prompt = f"""Review the current analysis results:

{state.analysis}

Previous iterations: {analysis_iteration - 1}

Evaluate:
1. Are the results sufficient to answer the research question?
2. Are there missing analyses or additional tests needed?
3. Should we explore alternative approaches?
4. Are there potential confounding factors to check?

If the analysis is complete, state "ANALYSIS COMPLETE".
If more work is needed, specify exactly what additional analysis should be performed.
"""

            analyst_decision = await orchestrator.send_to_agent(
                "analyst", analyst_review_prompt, context
            )

            if "ANALYSIS COMPLETE" in analyst_decision.upper():
                console.print("[green]✓ Analyst confirms analysis is complete[/green]")
                analysis_complete = True
                break
            else:
                analysis_request = f"Additional analysis requested:\n{analyst_decision}"
                console.print(f"[yellow]Additional analysis needed: {analyst_decision[:100]}...[/yellow]")

        # Step 1: Engineer writes code
        console.print(f"[cyan]Engineer writing code (iteration {analysis_iteration})...[/cyan]")
        code_prompt = f"""Write Python code to perform the following analysis:

{analysis_request}

Available context:
- Methodology: {state.methodology[:500]}...
- Data description: {state.data_description[:300]}...

Requirements:
- Use numpy, scipy, pandas, matplotlib as needed
- Include clear comments
- Save all plots to output/plots/ directory
- Print key results and findings
- Handle errors gracefully

Provide complete, executable Python code.
"""

        code_response = await orchestrator.send_to_agent("engineer", code_prompt, context)
        state.add_agent_interaction("engineer", code_prompt, code_response)

        # Extract code (assuming it's in markdown code blocks)
        if "```python" in code_response:
            code = code_response.split("```python")[1].split("```")[0].strip()
        elif "```" in code_response:
            code = code_response.split("```")[1].split("```")[0].strip()
        else:
            code = code_response

        # Save code
        code_file = code_dir / f"analysis_{analysis_iteration:02d}.py"
        state.save_to_file(code_file, code)
        console.print(f"[green]✓ Code saved to {code_file}[/green]")

        # Inner loop: Debugging until successful execution
        debug_attempt = 0
        execution_successful = False

        while not execution_successful and debug_attempt < max_debug_attempts:
            debug_attempt += 1

            if debug_attempt > 1:
                console.print(f"[yellow]Debug attempt {debug_attempt}/{max_debug_attempts}[/yellow]")

            # Step 2: User approval (if required)
            if require_approval and mode == "interactive":
                console.print(f"\n[yellow]Code ready for execution: {code_file}[/yellow]")
                if not Confirm.ask("Execute this code?", default=True):
                    console.print("[red]Execution cancelled by user[/red]")
                    return

            # Step 3: Executor runs code
            console.print("[cyan]Executor running code...[/cyan]")
            exec_prompt = f"""Execute this Python code and report results:

```python
{code}
```

Run the code using the execute_code tool and report:
- Execution output (stdout/stderr)
- Any errors encountered
- Whether execution was successful
"""

            exec_response = await orchestrator.send_to_agent("executor", exec_prompt, context)
            state.add_agent_interaction("executor", exec_prompt, exec_response)

            # Check if execution was successful
            if "Execution successful" in exec_response or "successful" in exec_response.lower():
                execution_successful = True
                console.print("[green]✓ Code executed successfully[/green]")

                # Step 4: Analyst interprets results
                console.print("[cyan]Analyst interpreting results...[/cyan]")
                interpret_prompt = f"""Interpret these analysis results:

Code executed:
```python
{code}
```

Execution output:
{exec_response}

Provide:
1. Summary of key findings
2. Statistical interpretation
3. Visualizations produced
4. How results relate to research question
5. Any limitations or caveats
"""

                analysis_results = await orchestrator.send_to_agent(
                    "analyst", interpret_prompt, context
                )
                state.add_agent_interaction("analyst", interpret_prompt, analysis_results)

                # Save intermediate analysis
                state.analysis = analysis_results
                intermediate_file = output_dir / "intermediate" / f"analysis_{analysis_iteration:02d}.md"
                state.save_to_file(intermediate_file, f"""# Analysis Iteration {analysis_iteration}

## Code
```python
{code}
```

## Execution Results
{exec_response}

## Interpretation
{analysis_results}
""")

                console.print(f"[green]✓ Analysis iteration {analysis_iteration} complete[/green]")

            else:
                # Execution failed - debug
                console.print("[red]Execution failed. Engineer debugging...[/red]")

                debug_prompt = f"""The code execution failed. Debug and fix the code.

Original code:
```python
{code}
```

Execution error:
{exec_response}

Analyze the error and provide corrected code that fixes the issue.
"""

                debug_response = await orchestrator.send_to_agent("engineer", debug_prompt, context)
                state.add_agent_interaction("engineer", debug_prompt, debug_response)

                # Extract corrected code
                if "```python" in debug_response:
                    code = debug_response.split("```python")[1].split("```")[0].strip()
                elif "```" in debug_response:
                    code = debug_response.split("```")[1].split("```")[0].strip()
                else:
                    code = debug_response

                # Save debugged code
                code_file = code_dir / f"analysis_{analysis_iteration:02d}_debug{debug_attempt}.py"
                state.save_to_file(code_file, code)

        if not execution_successful:
            console.print(f"[red]Failed to execute code after {max_debug_attempts} attempts[/red]")
            if mode == "interactive":
                if not Confirm.ask("Continue anyway?", default=False):
                    return

    # Save final analysis
    final_analysis_file = output_dir / "analysis.md"
    state.save_to_file(final_analysis_file, state.analysis)

    console.print(f"\n[green]✓ Final analysis saved to {final_analysis_file}[/green]")
    console.print(f"[green]✓ Code files saved to {code_dir}[/green]")
    console.print(f"[green]✓ Total analysis iterations: {analysis_iteration}[/green]")

    if not prompt_user_review(final_analysis_file, mode):
        return
