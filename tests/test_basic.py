"""Basic tests for research assistant."""

import pytest
from pathlib import Path
import tempfile
import shutil

from research_assistant.config import AgentConfig, DEFAULT_AGENTS
from research_assistant.state import ResearchState


class TestAgentConfig:
    """Test agent configuration."""

    def test_default_system_message(self):
        """Test that default system messages are set correctly."""
        config = AgentConfig(name="test", role="idea_maker")
        assert "creative" in config.system_message.lower()
        assert len(config.system_message) > 0

    def test_custom_system_message(self):
        """Test custom system message overrides default."""
        custom_msg = "Custom system message"
        config = AgentConfig(name="test", role="idea_maker", system_message=custom_msg)
        assert config.system_message == custom_msg

    def test_all_default_agents_defined(self):
        """Test that all default agents are properly configured."""
        expected_agents = [
            "idea_maker",
            "idea_critic",
            "literature_researcher",
            "methodologist",
            "engineer",
            "executor",
            "analyst",
            "writer",
            "reviewer",
        ]
        for agent_name in expected_agents:
            assert agent_name in DEFAULT_AGENTS
            config = DEFAULT_AGENTS[agent_name]
            assert config.name == agent_name
            assert config.role == agent_name
            assert len(config.system_message) > 0


class TestResearchState:
    """Test research state management."""

    def setup_method(self):
        """Create temporary directory for tests."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test state initialization."""
        state = ResearchState(project_dir=self.temp_dir)
        assert state.project_dir == self.temp_dir
        assert state.data_description == ""
        assert state.idea == ""
        assert len(state.completed_modules) == 0

    def test_mark_module_complete(self):
        """Test marking modules as complete."""
        state = ResearchState(project_dir=self.temp_dir)
        state.mark_module_complete("idea")
        assert state.is_module_complete("idea")
        assert not state.is_module_complete("literature")

    def test_save_to_file(self):
        """Test saving content to file."""
        state = ResearchState(project_dir=self.temp_dir)
        test_file = self.temp_dir / "test.md"
        test_content = "# Test Content\n\nThis is a test."

        state.save_to_file(test_file, test_content)
        assert test_file.exists()
        assert test_file.read_text() == test_content

    def test_load_from_files(self):
        """Test loading state from files."""
        # Create input and output directories
        input_dir = self.temp_dir / "input"
        output_dir = self.temp_dir / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        # Create test files
        (input_dir / "data_description.md").write_text("Test data description")
        (output_dir / "idea.md").write_text("Test idea")

        # Load state
        state = ResearchState(project_dir=self.temp_dir)
        state.load_from_files()

        assert state.data_description == "Test data description"
        assert state.idea == "Test idea"
        assert state.is_module_complete("idea")

    def test_get_context_for_agent(self):
        """Test context generation for different agents."""
        state = ResearchState(project_dir=self.temp_dir)
        state.data_description = "Test data"
        state.idea = "Test idea"
        state.literature = "Test literature"

        # Test idea_maker context
        context = state.get_context_for_agent("idea_maker")
        assert "data_description" in context
        assert "idea" not in context

        # Test methodologist context
        context = state.get_context_for_agent("methodologist")
        assert "data_description" in context
        assert "idea" in context
        assert "literature" in context

    def test_add_agent_interaction(self):
        """Test logging agent interactions."""
        state = ResearchState(project_dir=self.temp_dir)
        state.add_agent_interaction("idea_maker", "test prompt", "test response")

        assert len(state.agent_history) == 1
        interaction = state.agent_history[0]
        assert interaction["agent"] == "idea_maker"
        assert interaction["prompt"] == "test prompt"
        assert interaction["response"] == "test response"


class TestProjectStructure:
    """Test project structure creation."""

    def setup_method(self):
        """Create temporary directory for tests."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_project_structure_creation(self):
        """Test that ResearchAssistant creates proper directory structure."""
        from research_assistant import ResearchAssistant

        assistant = ResearchAssistant(project_dir=str(self.temp_dir))

        # Check directory structure
        assert (self.temp_dir / "input").exists()
        assert (self.temp_dir / "output").exists()
        assert (self.temp_dir / "output" / "plots").exists()
        assert (self.temp_dir / "output" / "code").exists()
        assert (self.temp_dir / "output" / "intermediate").exists()


def test_imports():
    """Test that all main components can be imported."""
    from research_assistant import ResearchAssistant, AgentConfig, ResearchState
    from research_assistant.orchestrator import AgentOrchestrator
    from research_assistant.tools import create_tools

    # Just check they import without errors
    assert ResearchAssistant is not None
    assert AgentConfig is not None
    assert ResearchState is not None
    assert AgentOrchestrator is not None
    assert create_tools is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
