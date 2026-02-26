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
    env_manager = None,
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
        env_manager: Environment manager for isolated code execution
    """
    # Ensure project_dir is absolute for relative_to() operations
    project_dir = project_dir.resolve()
    
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

            # Analyst uses reasoning model (o3-mini), needs 20-minute timeout
            analyst_decision = await orchestrator.send_to_agent(
                "analyst", analyst_review_prompt, context, timeout=1200
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
        code_prompt = f"""Write Python code for: {analysis_request}

Context:
- Data: {state.data_description[:200]}...
- Method: {state.methodology[:300]}...

Requirements: Use pandas/numpy/matplotlib, save plots to output/plots/, print results.

Provide complete Python code only.
"""

        # Use 20-minute timeout for code generation (o3-mini reasoning takes ~15min)
        code_response = await orchestrator.send_to_agent("engineer", code_prompt, context, timeout=1200)
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
        
        # Commit code generation
        state.commit_step("analysis", "code_generation", f"Generated code for iteration {analysis_iteration}")
        state.save_state()

        # Step 2: Execute code (no approval required - automatic execution)
        # Inner loop: Debugging until successful execution
        debug_attempt = 0
        execution_successful = False

        while not execution_successful and debug_attempt < max_debug_attempts:
            debug_attempt += 1

            if debug_attempt > 1:
                console.print(f"[yellow]Debug attempt {debug_attempt}/{max_debug_attempts}[/yellow]")

            # Step 3: Executor runs code
            console.print("[cyan]Executor running code...[/cyan]")
            console.print("[dim]This may take several minutes for complex analysis...[/dim]")
            
            # Use environment manager if available
            # Increase timeout to 30 minutes for data analysis tasks (model training, CV, etc.)
            if env_manager:
                # Run synchronous execute_code in thread pool to avoid blocking event loop
                import asyncio
                success, stdout, stderr = await asyncio.to_thread(
                    env_manager.execute_code, code, 1800
                )
                if success:
                    exec_response = f"Execution successful:\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
                else:
                    exec_response = f"Execution failed:\n\nSTDOUT:\n{stdout}\n\nSTDERR:\n{stderr}"
            else:
                # Fallback to direct execution via agent (needs long timeout for code execution)
                exec_prompt = f"""Execute this Python code and report results:

```python
{code}
```

Run the code using the execute_code tool and report:
- Execution output (stdout/stderr)
- Any errors encountered
- Whether execution was successful
"""

                # Executor needs 30-minute timeout to wait for code execution
                exec_response = await orchestrator.send_to_agent("executor", exec_prompt, context, timeout=1800)
            
            state.add_agent_interaction("executor", "Code execution", exec_response)

            # Check if execution was successful
            if "Execution successful" in exec_response or "successful" in exec_response.lower():
                execution_successful = True
                console.print("[green]✓ Code executed successfully[/green]")
                
                # Commit successful execution
                state.commit_step("analysis", "execution_success", f"Iteration {analysis_iteration}, attempt {debug_attempt}")
                state.save_state()

                # Step 4: Analyst interprets results
                console.print("[cyan]Analyst interpreting results...[/cyan]")
                console.print("[dim]This may take 10-20 minutes (o3-mini reasoning model)...[/dim]")
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

                # Analyst interpretation needs 20-minute timeout (o3-mini reasoning)
                analysis_results = await orchestrator.send_to_agent(
                    "analyst", interpret_prompt, context, timeout=1200
                )
                state.add_agent_interaction("analyst", interpret_prompt, analysis_results)
                console.print("[green]✓ Analyst interpretation complete[/green]")

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
                
                # Commit iteration completion
                state.commit_iteration("analysis", analysis_iteration, "Completed analysis iteration")
                state.save_state()

                console.print(f"[green]✓ Analysis iteration {analysis_iteration} complete[/green]")

            else:
                # Execution failed - debug
                console.print("[red]Execution failed. Engineer debugging...[/red]")
                
                # Extract error message for commit
                error_summary = exec_response.split('\n')[0][:100] if exec_response else "Unknown error"

                debug_prompt = f"""The code execution failed. Debug and fix the code.

Original code:
```python
{code}
```

Execution error:
{exec_response}

Analyze the error and provide corrected code that fixes the issue.
"""

                # Engineer debugging needs 20-minute timeout (o3-mini code generation)
                debug_response = await orchestrator.send_to_agent("engineer", debug_prompt, context, timeout=1200)
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
                
                # Commit debug attempt
                state.commit_debug_attempt("analysis", analysis_iteration, debug_attempt, error_summary)
                state.save_state()

        if not execution_successful:
            console.print(f"[red]Failed to execute code after {max_debug_attempts} attempts[/red]")
            if mode == "interactive":
                if not Confirm.ask("Continue anyway?", default=False):
                    return

    # Save final analysis
    final_analysis_file = output_dir / "analysis.md"
    state.save_to_file(final_analysis_file, state.analysis)
    
    # Commit final analysis
    state.commit_step("analysis", "finalized", f"Completed {analysis_iteration} iterations")
    state.save_state()

    console.print(f"\n[green]✓ Final analysis saved to {final_analysis_file}[/green]")
    console.print(f"[green]✓ Code files saved to {code_dir}[/green]")
    console.print(f"[green]✓ Total analysis iterations: {analysis_iteration}[/green]")

    # Review results and ask if user wants more iterations
    if mode == "interactive":
        console.print("\n[bold cyan]Analysis Complete - Review Results[/bold cyan]")
        console.print(f"Review output files:")
        console.print(f"  - Analysis: {final_analysis_file}")
        console.print(f"  - Code: {code_dir}")
        console.print(f"  - Plots: {output_dir / 'plots'}")
        console.print(f"  - Intermediate: {output_dir / 'intermediate'}")
        
        import asyncio
        # Ask if user wants additional iterations
        more_iterations = await asyncio.to_thread(
            Confirm.ask, 
            "\nDo you want to run additional analysis iterations?", 
            default=False
        )
        
        if more_iterations:
            console.print("\n[cyan]Starting additional analysis iterations...[/cyan]")
            # Commit user decision
            state.commit_user_input("analysis", "continued", "User requested more iterations")
            state.save_state()
            
            # Recursively call this function to continue analysis
            await run_analysis_execution(
                orchestrator, state, mode, project_dir, require_approval, env_manager
            )
        else:
            console.print("[green]✓ Analysis workflow complete[/green]")
            # Commit user decision
            state.commit_user_input("analysis", "completed", "User confirmed completion")
            state.save_state()
    else:
        # In automatic mode, just finish
        console.print("[green]✓ Analysis workflow complete[/green]")
