"""Test Git-based iteration tracking."""

import pytest
import tempfile
import shutil
from pathlib import Path

from research_assistant.state import ResearchState
from research_assistant.git_tracker import GitTracker


def test_git_tracker_initialization():
    """Test Git tracker initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        
        tracker = GitTracker(project_dir)
        assert not tracker.is_initialized()
        
        tracker.initialize()
        assert tracker.is_initialized()
        
        # Check .gitignore was created
        gitignore = project_dir / ".gitignore"
        assert gitignore.exists()
        
        # Check initial commit was made
        commits = tracker.get_log(max_count=1)
        assert len(commits) == 1
        assert "Initialize research project" in commits[0]['message']


def test_git_commit_step():
    """Test committing a step."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        
        tracker = GitTracker(project_dir)
        tracker.initialize()
        
        # Create a test file
        test_file = project_dir / "test.txt"
        test_file.write_text("test content")
        
        # Commit it
        commit_hash = tracker.commit_step("test_module", "test_step", "Test description")
        assert commit_hash is not None
        
        # Check commit message
        message = tracker.get_commit_message()
        assert "[test_module] test_step: Test description" in message


def test_git_commit_iteration():
    """Test committing an iteration."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        
        tracker = GitTracker(project_dir)
        tracker.initialize()
        
        # Commit iterations
        for i in range(1, 4):
            test_file = project_dir / f"iteration_{i}.txt"
            test_file.write_text(f"iteration {i}")
            tracker.commit_iteration("analysis", i, f"Completed iteration {i}")
        
        # Check commits
        commits = tracker.get_log(max_count=10, module="analysis")
        assert len(commits) >= 3
        
        # Check status
        status = tracker.get_module_status("analysis")
        assert status['iteration_count'] == 3
        assert status['iterations'] == [1, 2, 3]


def test_git_commit_debug_attempt():
    """Test committing debug attempts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        
        tracker = GitTracker(project_dir)
        tracker.initialize()
        
        # Commit debug attempts
        test_file = project_dir / "debug.py"
        test_file.write_text("# debug attempt 1")
        tracker.commit_debug_attempt("analysis", 1, 1, "NameError: undefined variable")
        
        test_file.write_text("# debug attempt 2")
        tracker.commit_debug_attempt("analysis", 1, 2, "Fixed undefined variable")
        
        # Check commits
        commits = tracker.get_log(max_count=10, module="analysis")
        assert any("Debug attempt 1" in c['message'] for c in commits)
        assert any("Debug attempt 2" in c['message'] for c in commits)


def test_git_diff():
    """Test getting diffs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        
        tracker = GitTracker(project_dir)
        tracker.initialize()
        
        # Create initial file
        test_file = project_dir / "test.txt"
        test_file.write_text("version 1")
        tracker.commit_step("test", "step1", "Initial")
        commit1 = tracker.get_current_commit()
        
        # Modify file
        test_file.write_text("version 2")
        tracker.commit_step("test", "step2", "Updated")
        commit2 = tracker.get_current_commit()
        
        # Get diff
        diff = tracker.get_diff(commit1, commit2)
        assert "version 1" in diff
        assert "version 2" in diff


def test_research_state_git_integration():
    """Test ResearchState with Git tracking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        
        # Create state with Git enabled
        state = ResearchState(project_dir=project_dir, git_enabled=True)
        assert state.git_tracker is not None
        assert state.git_tracker.is_initialized()
        
        # Test commit methods
        (project_dir / "test.md").write_text("test")
        state.commit_step("test", "generation", "Test generation")
        
        # Check commit was made
        commits = state.git_tracker.get_log(max_count=5)
        assert any("generation" in c['message'] for c in commits)
        
        # Test save state with Git commit
        state.idea = "Test idea"
        state.save_state()
        
        commits = state.git_tracker.get_log(max_count=5)
        assert any("Update research state" in c['message'] for c in commits)


def test_git_disabled():
    """Test behavior when Git is disabled."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir) / "test_project"
        project_dir.mkdir()
        
        # Create state with Git disabled
        state = ResearchState(project_dir=project_dir, git_enabled=False)
        assert state.git_tracker is None
        
        # Commit methods should return None gracefully
        result = state.commit_step("test", "step", "description")
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
