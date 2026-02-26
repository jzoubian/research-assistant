"""Agent orchestration using Copilot SDK."""

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any, Optional
from copilot import CopilotClient, CopilotSession
from copilot.types import SessionConfig
from research_assistant.config import AgentConfig
from research_assistant.tools import create_tools


class AgentOrchestrator:
    """Manages multiple Copilot SDK sessions for multi-agent workflows."""

    def __init__(self, project_dir: str):
        """Initialize orchestrator.

        Args:
            project_dir: Path to research project directory
        """
        self.project_dir = project_dir
        self.client: Optional[CopilotClient] = None
        self.agents: dict[str, dict[str, Any]] = {}  # agent_name -> {config, session, tools}

    def _find_copilot_cli(self) -> Optional[str]:
        """Find the Copilot CLI executable.
        
        Returns:
            Path to copilot CLI or None if not found
        """
        # Check environment variable first
        cli_path = os.environ.get("COPILOT_CLI_PATH")
        if cli_path and os.path.isfile(cli_path):
            return cli_path
        
        # Check if 'copilot' is in PATH
        cli_path = shutil.which("copilot")
        if cli_path:
            return cli_path
        
        # Check common VS Code installation paths
        vscode_paths = [
            Path.home() / ".config" / "Code" / "User" / "globalStorage" / "github.copilot-chat" / "copilotCli" / "copilot",
            Path.home() / ".vscode" / "extensions" / "github.copilot-chat" / "copilotCli" / "copilot",
            Path.home() / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "github.copilot-chat" / "copilotCli" / "copilot",  # macOS
        ]
        
        for path in vscode_paths:
            if path.exists():
                return str(path)
        
        return None

    async def initialize(self) -> None:
        """Initialize Copilot SDK client."""
        cli_path = self._find_copilot_cli()
        
        if not cli_path:
            raise RuntimeError(
                "Copilot CLI not found. Please ensure GitHub Copilot is installed via VS Code "
                "or set the COPILOT_CLI_PATH environment variable to the copilot executable path."
            )
        
        # Create client with options dictionary
        self.client = CopilotClient({"cli_path": cli_path})
        await self.client.start()

    async def create_agent(self, config: AgentConfig) -> None:
        """Create a new agent with its own session.

        Args:
            config: Agent configuration
        """
        if not self.client:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")

        # Create tools for this agent
        tools = create_tools(self.project_dir, config.tools)

        # Create session config
        session_config: dict[str, Any] = {
            "model": config.model,
        }

        # Add optional parameters if provided
        if config.system_message:
            session_config["system_message"] = config.system_message
        if config.temperature is not None:
            session_config["temperature"] = config.temperature
        
        # Only add reasoning_effort for models that support it (o1 series)
        # o3-mini and other models don't support this parameter
        if config.reasoning_effort and config.model.startswith("o1"):
            session_config["reasoning_effort"] = config.reasoning_effort

        # Create session
        session = await self.client.create_session(session_config)

        # Register tools with session if the API supports it
        # Note: Tool registration may need to be updated based on actual SDK API
        if hasattr(session, 'register_tool'):
            for tool in tools:
                await session.register_tool(tool)

        self.agents[config.name] = {
            "config": config,
            "session": session,
            "tools": tools,
        }

    async def _ensure_session_valid(self, agent_name: str) -> None:
        """Ensure agent session is valid, recreate if necessary.
        
        Args:
            agent_name: Name of the agent to check
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        agent = self.agents[agent_name]
        config = agent["config"]
        
        # Try to check session health - if session is invalid, recreate it
        try:
            # Test if session is still alive by checking its session_id attribute
            _ = agent["session"].session_id
        except (AttributeError, RuntimeError, Exception):
            # Session is dead, recreate it
            from rich.console import Console
            console = Console()
            console.print(f"[yellow]⚠ Session for {agent_name} is invalid, recreating...[/yellow]")
            
            # Create new session with same config
            session_config: dict[str, Any] = {"model": config.model}
            if config.system_message:
                session_config["system_message"] = config.system_message
            if config.temperature is not None:
                session_config["temperature"] = config.temperature
            if config.reasoning_effort and config.model.startswith("o1"):
                session_config["reasoning_effort"] = config.reasoning_effort
            
            new_session = await self.client.create_session(session_config)
            
            # Register tools if needed
            if hasattr(new_session, 'register_tool'):
                for tool in agent["tools"]:
                    await new_session.register_tool(tool)
            
            # Update agent with new session
            self.agents[agent_name]["session"] = new_session
            console.print(f"[green]✓ Session recreated for {agent_name}[/green]")

    async def send_to_agent(
        self, agent_name: str, prompt: str, context: Optional[dict[str, str]] = None, timeout: int = 300
    ) -> str:
        """Send a message to a specific agent.

        Args:
            agent_name: Name of the agent
            prompt: Message to send
            context: Additional context to include
            timeout: Timeout in seconds (default: 300s / 5 minutes)

        Returns:
            Agent's response
        """
        import asyncio
        from rich.console import Console
        from rich.prompt import Confirm
        
        console = Console()
        
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")
        
        # Ensure session is valid before sending
        await self._ensure_session_valid(agent_name)

        agent = self.agents[agent_name]
        session = agent["session"]

        # Build full prompt with context
        full_prompt = prompt
        if context:
            context_str = "\n\n".join([f"## {k}\n{v}" for k, v in context.items() if v])
            full_prompt = f"{context_str}\n\n## Task\n{prompt}"

        # Send message and get response with timeout handling
        while True:
            try:
                response = await session.send_and_wait({"prompt": full_prompt}, timeout=timeout)
                break  # Success, exit loop
            except asyncio.TimeoutError:
                console.print(f"[yellow]⚠ Timeout after {timeout}s waiting for {agent_name}[/yellow]")
                console.print(f"[yellow]The agent may still be processing (code execution, reasoning, etc.)[/yellow]")
                
                # Prompt user with 30-second timeout on the prompt itself
                try:
                    should_stop = await asyncio.wait_for(
                        asyncio.to_thread(
                            Confirm.ask,
                            "Stop waiting and abort?",
                            default=False
                        ),
                        timeout=30.0
                    )
                except asyncio.TimeoutError:
                    # No response in 30s, continue waiting
                    should_stop = False
                    console.print("[cyan]No response - continuing to wait...[/cyan]")
                
                if should_stop:
                    console.print("[red]Aborted by user[/red]")
                    raise asyncio.TimeoutError(f"User aborted after {timeout}s timeout")
                else:
                    console.print(f"[cyan]Continuing to wait for {agent_name} (timeout extended by {timeout}s)...[/cyan]")
                    # Ensure session is still valid before retrying
                    await self._ensure_session_valid(agent_name)
                    session = self.agents[agent_name]["session"]
                    # Continue loop with same timeout increment
            except Exception as e:
                # Check for quota/session errors
                error_str = str(e).lower()
                if "402" in error_str or "no quota" in error_str:
                    console.print(f"[red]Session error: 402 You have no quota. Stopping execution.[/red]")
                    raise RuntimeError("Session error: 402 You have no quota. Stopping execution.")
                elif "session not found" in error_str or "session" in error_str:
                    console.print(f"[yellow]⚠ Session error: {e}[/yellow]")
                    console.print("[yellow]Attempting to recover session...[/yellow]")
                    await self._ensure_session_valid(agent_name)
                    session = self.agents[agent_name]["session"]
                    console.print("[cyan]Retrying with new session...[/cyan]")
                    # Continue loop to retry
                else:
                    # Unknown error, re-raise
                    raise

        # Extract text from response
        if response and hasattr(response, 'data') and hasattr(response.data, 'content'):
            return response.data.content
        else:
            return str(response)

    async def multi_agent_conversation(
        self,
        agents: list[str],
        initial_prompt: str,
        rounds: int = 3,
        context: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """Orchestrate a multi-agent conversation.

        Args:
            agents: List of agent names to participate
            initial_prompt: Starting prompt for the conversation
            rounds: Number of conversation rounds
            context: Shared context for all agents

        Returns:
            Dictionary with conversation history and final responses
        """
        history = []
        current_prompt = initial_prompt

        for round_num in range(rounds):
            round_responses = {}

            for agent_name in agents:
                # Add previous responses to context
                round_context = context.copy() if context else {}
                if history:
                    round_context["previous_responses"] = "\n\n".join(
                        [f"**{h['agent']}**: {h['response']}" for h in history[-len(agents) :]]
                    )

                # Get agent response
                response = await self.send_to_agent(agent_name, current_prompt, round_context)

                # Record interaction
                history.append(
                    {
                        "round": round_num + 1,
                        "agent": agent_name,
                        "prompt": current_prompt,
                        "response": response,
                    }
                )

                round_responses[agent_name] = response

                # Update prompt for next agent based on previous response
                if len(agents) > 1:
                    current_prompt = f"Based on the previous response from {agent_name}, provide your perspective:\n\n{response}"

            # Reset prompt for next round
            current_prompt = initial_prompt

        return {"history": history, "final_responses": round_responses}

    async def get_agent_config(self, agent_name: str) -> AgentConfig:
        """Get configuration for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Agent configuration
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")
        return self.agents[agent_name]["config"]

    async def cleanup(self) -> None:
        """Close all sessions and cleanup resources."""
        for agent in self.agents.values():
            session = agent["session"]
            await session.destroy()

        if self.client:
            await self.client.stop()

        self.agents.clear()
