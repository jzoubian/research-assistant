"""Example usage of research assistant."""

import asyncio
from research_assistant import ResearchAssistant, AgentConfig


async def example_basic():
    """Basic usage example with default agents."""
    print("=" * 80)
    print("EXAMPLE 1: Basic Usage with Default Agents")
    print("=" * 80)

    # Initialize assistant with default configuration
    assistant = ResearchAssistant(project_dir="./my_research")
    await assistant.initialize()

    # Load data description
    assistant.load_data_description("input/data_description.md")

    # Run workflow step by step
    await assistant.generate_idea(mode="interactive")
    await assistant.review_literature()
    await assistant.develop_methodology()
    await assistant.execute_analysis(require_approval=True)
    await assistant.write_paper(journal_format="nature")
    await assistant.review_paper()

    await assistant.cleanup()


async def example_custom_agents():
    """Example with custom agent configurations."""
    print("=" * 80)
    print("EXAMPLE 2: Custom Agent Configurations")
    print("=" * 80)

    # Customize specific agents
    custom_agents = {
        "idea_maker": AgentConfig(
            name="idea_maker",
            role="idea_maker",
            model="claude-sonnet-4.5",
            temperature=0.9,
            system_message="""You are a creative physicist specializing in cosmology. 
            Generate innovative research ideas that push boundaries.""",
        ),
        "idea_critic": AgentConfig(
            name="idea_critic",
            role="idea_critic",
            model="o3-mini",
            reasoning_effort="xhigh",
        ),
        "engineer": AgentConfig(
            name="engineer",
            role="engineer",
            model="deepseek-coder-v2:16b",
            provider={
                "type": "openai",
                "base_url": "http://localhost:11434/v1",
            },
            temperature=0.2,
        ),
        "analyst": AgentConfig(
            name="analyst",
            role="analyst",
            model="o3-mini",
            reasoning_effort="high",
            temperature=0.3,
        ),
    }

    assistant = ResearchAssistant(
        project_dir="./custom_research",
        agent_configs=custom_agents,
    )

    await assistant.initialize()
    assistant.load_data_description("input/data_description.md")

    # Run specific modules
    await assistant.generate_idea(mode="interactive")
    await assistant.execute_analysis(require_approval=True)

    await assistant.cleanup()


async def example_multi_agent_conversation():
    """Example of direct multi-agent orchestration."""
    print("=" * 80)
    print("EXAMPLE 3: Direct Multi-Agent Orchestration")
    print("=" * 80)

    assistant = ResearchAssistant(project_dir="./orchestration_example")
    await assistant.initialize()

    # Load context
    assistant.load_data_description("input/data_description.md")

    # Direct access to orchestrator for custom workflows
    orchestrator = assistant.orchestrator

    # Multi-round conversation between idea_maker and idea_critic
    context = {"data_description": assistant.state.data_description}

    result = await orchestrator.multi_agent_conversation(
        agents=["idea_maker", "idea_critic", "idea_maker"],
        initial_prompt="Generate 5 innovative research ideas based on the data.",
        rounds=3,
        context=context,
    )

    # Print conversation history
    print("\nConversation History:")
    for msg in result["history"]:
        print(f"\n--- Round {msg['round']} - {msg['agent']} ---")
        print(msg["response"][:200] + "...")

    await assistant.cleanup()


async def example_automatic_mode():
    """Example of fully automatic mode without user intervention."""
    print("=" * 80)
    print("EXAMPLE 4: Automatic Mode (No User Intervention)")
    print("=" * 80)

    assistant = ResearchAssistant(project_dir="./auto_research")
    await assistant.initialize()

    assistant.load_data_description("input/data_description.md")

    # Run all modules in automatic mode
    await assistant.generate_idea(mode="automatic")
    await assistant.review_literature(mode="automatic")
    await assistant.develop_methodology(mode="automatic")
    await assistant.execute_analysis(mode="automatic", require_approval=False)
    await assistant.write_paper(mode="automatic", journal_format="prl")
    await assistant.review_paper(mode="automatic")

    await assistant.cleanup()

    print("\n[Complete research workflow executed automatically]")


async def example_specialized_models():
    """Example using different models for different tasks."""
    print("=" * 80)
    print("EXAMPLE 5: Specialized Models per Task")
    print("=" * 80)

    specialized_agents = {
        # Fast, creative model for brainstorming
        "idea_maker": AgentConfig(
            name="idea_maker",
            model="gpt-4o",
            temperature=0.8,
        ),
        # Reasoning model for critique
        "idea_critic": AgentConfig(
            name="idea_critic",
            model="o3-mini",
            reasoning_effort="xhigh",
        ),
        # Claude for literature synthesis
        "literature_researcher": AgentConfig(
            name="literature_researcher",
            model="claude-sonnet-4.5",
            temperature=0.5,
        ),
        # GPT-4.1 for complex methodology
        "methodologist": AgentConfig(
            name="methodologist",
            model="gpt-4o",
            temperature=0.4,
        ),
        # Local coding model
        "engineer": AgentConfig(
            name="engineer",
            model="deepseek-coder-v2:16b",
            provider={"type": "openai", "base_url": "http://localhost:11434/v1"},
        ),
        # O3 for rigorous analysis
        "analyst": AgentConfig(
            name="analyst",
            model="o3-mini",
            reasoning_effort="high",
            temperature=0.2,
        ),
        # Fast model for writing
        "writer": AgentConfig(
            name="writer",
            model="gemini-2.5-flash",
            temperature=0.6,
        ),
        # Reasoning model for review
        "reviewer": AgentConfig(
            name="reviewer",
            model="o3-mini",
            reasoning_effort="medium",
        ),
    }

    assistant = ResearchAssistant(
        project_dir="./specialized_research",
        agent_configs=specialized_agents,
    )

    await assistant.initialize()
    # ... continue with workflow ...
    await assistant.cleanup()


def main():
    """Run examples."""
    print("\nResearch Assistant Examples")
    print("=" * 80)
    print("\nAvailable examples:")
    print("1. Basic usage with default agents")
    print("2. Custom agent configurations")
    print("3. Direct multi-agent orchestration")
    print("4. Automatic mode (no user intervention)")
    print("5. Specialized models per task")
    print("\nNote: These examples are for demonstration. Uncomment to run.")

    # Uncomment to run specific example:
    # asyncio.run(example_basic())
    # asyncio.run(example_custom_agents())
    # asyncio.run(example_multi_agent_conversation())
    # asyncio.run(example_automatic_mode())
    # asyncio.run(example_specialized_models())


if __name__ == "__main__":
    main()
