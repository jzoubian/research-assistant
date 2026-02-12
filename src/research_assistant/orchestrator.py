"""Agent orchestration using Copilot SDK."""

import asyncio
from typing import Any, Optional
from copilot_sdk_agent import CopilotSDK, SessionOptions
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
        self.client: Optional[CopilotSDK] = None
        self.agents: dict[str, dict[str, Any]] = {}  # agent_name -> {config, session, tools}

    async def initialize(self) -> None:
        """Initialize Copilot SDK client."""
        self.client = CopilotSDK()
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

        # Create session options
        session_options = SessionOptions(
            agent_name=config.name,
            model=config.model,
            system_message=config.system_message,
            temperature=config.temperature,
        )

        # Add reasoning_effort for O3 models
        if config.reasoning_effort:
            session_options.reasoning_effort = config.reasoning_effort

        # Create session
        session = await self.client.create_session(session_options)

        # Register tools with session
        for tool in tools:
            await session.register_tool(tool)

        self.agents[config.name] = {
            "config": config,
            "session": session,
            "tools": tools,
        }

    async def send_to_agent(
        self, agent_name: str, prompt: str, context: Optional[dict[str, str]] = None
    ) -> str:
        """Send a message to a specific agent.

        Args:
            agent_name: Name of the agent
            prompt: Message to send
            context: Additional context to include

        Returns:
            Agent's response
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not found")

        agent = self.agents[agent_name]
        session = agent["session"]

        # Build full prompt with context
        full_prompt = prompt
        if context:
            context_str = "\n\n".join([f"## {k}\n{v}" for k, v in context.items() if v])
            full_prompt = f"{context_str}\n\n## Task\n{prompt}"

        # Send message and get response
        response = await session.send_message(full_prompt)

        # Handle streaming
        if agent["config"].streaming:
            full_response = ""
            async for chunk in response:
                full_response += chunk.text
            return full_response
        else:
            return response.text

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
            await session.close()

        if self.client:
            await self.client.stop()

        self.agents.clear()
