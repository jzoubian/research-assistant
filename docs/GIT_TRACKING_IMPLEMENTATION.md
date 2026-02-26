# Git-Based Iteration Tracking - Implementation Summary

## Overview

Replaced the file duplication-based iteration tracking system (`.iterations/` directory) with a comprehensive Git-based version control system. This provides better tracking, collaboration capabilities, and eliminates redundant file storage.

## Key Changes

### 1. New GitTracker Class (`src/research_assistant/git_tracker.py`)

Created a comprehensive Git wrapper class that handles all version control operations:

**Core Features:**
- **Initialization**: Automatically initializes Git repository with comprehensive `.gitignore`
- **Commit Operations**:
  - `commit_step()`: Commit module steps (e.g., generation, execution)
  - `commit_iteration()`: Commit iteration completions
  - `commit_debug_attempt()`: Track debugging attempts with error messages
  - `commit_user_input()`: Record user actions and decisions
- **Query Operations**:
  - `get_status()`: Current working tree status
  - `get_log()`: Commit history with module filtering
  - `get_diff()`: Diffs between commits or iterations
  - `get_module_status()`: Comprehensive module statistics
  - `get_file_history()`: History for specific files
- **Smart .gitignore**: Prevents tracking of:
  - Data files (CSV, HDF5, Parquet, etc.)
  - Large binary files (models, checkpoints)
  - Environment directories (.pixi, venv, conda)
  - Optional: plot images (can be enabled)

### 2. ResearchState Integration (`src/research_assistant/state.py`)

**Removed:**
- `ModuleIteration` class (replaced by Git commits)
- `module_iterations` dict (replaced by Git log)
- `add_module_iteration()` method (replaced by commit methods)
- `get_module_iteration_count()` method
- `get_latest_iteration()` method

**Added:**
- `git_enabled` field (default: True)
- `git_tracker` field (GitTracker instance, not serialized)
- `commit_step()`: Commit module steps
- `commit_iteration()`: Commit iterations
- `commit_debug_attempt()`: Commit debug attempts
- `commit_user_input()`: Commit user actions
- `get_module_status()`: Get module status from Git
- `get_iteration_diff()`: Get diff between iterations
- `print_git_status()`: Display Git status
- `print_module_git_status()`: Display module-specific status

**Modified:**
- `save_state()`: Now commits state file to Git automatically
- `load_state()`: Reinitializes Git tracker on load
- `mark_module_complete()`: Commits completion to Git

### 3. Analysis Module Updates (`src/research_assistant/modules/analysis.py`)

Added Git commits at key points:
- **Code Generation**: After engineer writes code
- **Execution Success**: After successful code execution
- **Iteration Completion**: After analyst interprets results
- **Debug Attempts**: After each debugging attempt with error summary
- **Finalization**: After all iterations complete
- **User Decisions**: When user continues or completes analysis

### 4. Other Module Updates

**Idea Module** (`src/research_assistant/modules/idea.py`):
- Commit after idea generation
- Commit after user review

**Literature Module** (`src/research_assistant/modules/literature.py`):
- Commit after literature synthesis
- Commit after user review

**Methodology Module** (`src/research_assistant/modules/methodology.py`):
- Commit after methodology development
- Commit after user review

### 5. CLI Updates (`src/research_assistant/cli.py`)

**Removed:**
- `preserve_iteration_files()` function
- All file copying logic from module commands
- `.iterations/` directory creation

**Simplified:**
- All module commands now use simple Git commits instead of file preservation
- `--iterate` flag now just commits user intent

**Added New Commands:**
- `status [--module MODULE]`: Show Git status and commit history
  ```bash
  research-assistant status iris_classification
  research-assistant status iris_classification --module analysis
  ```

- `log [--module MODULE] [--count N]`: Show commit log
  ```bash
  research-assistant log iris_classification
  research-assistant log iris_classification --module analysis --count 50
  ```

- `diff --module MODULE --from N --to M`: Show diff between iterations
  ```bash
  research-assistant diff iris_classification --module analysis --from 1 --to 2
  ```

### 6. Testing (`tests/test_git_tracking.py`)

Comprehensive test suite covering:
- Git initialization
- Commit operations (steps, iterations, debug attempts)
- Query operations (status, log, diff)
- ResearchState integration
- Git disabled mode

## Usage Examples

### View Project Status
```bash
# Overall project status
research-assistant status iris_classification

# Module-specific status
research-assistant status iris_classification --module analysis
```

### View Commit History
```bash
# All commits
research-assistant log iris_classification

# Analysis module only
research-assistant log iris_classification --module analysis

# Last 50 commits
research-assistant log iris_classification --count 50
```

### Compare Iterations
```bash
# See what changed between iteration 1 and 2
research-assistant diff iris_classification --module analysis --from 1 --to 2
```

### Standard Git Commands
Since everything is in Git, you can also use standard Git commands:

```bash
cd iris_classification

# View status
git status

# View log
git log --oneline

# View specific module
git log --grep="\[analysis\]"

# View diff
git diff HEAD~1

# View file history
git log --follow output/code/analysis_01.py

# Checkout previous state
git checkout <commit-hash>

# Create branches for experiments
git checkout -b experiment-1
```

## Commit Message Format

All commits follow a consistent format:

- **Steps**: `[module] step: description`
  - Example: `[analysis] code_generation: Generated code for iteration 1`

- **Iterations**: `[module] Iteration N: description`
  - Example: `[analysis] Iteration 1: Completed analysis iteration`

- **Debug Attempts**: `[module] Iteration N - Debug attempt M: error`
  - Example: `[analysis] Iteration 1 - Debug attempt 1: NameError: name 'pd' is not defined`

- **User Input**: `[module] User action: notes`
  - Example: `[analysis] User continued: User requested more iterations`

- **State Updates**: `Update research state`

## Benefits

### 1. No File Duplication
- Eliminates redundant `.iterations/` directory
- Git efficiently stores only changes (diffs)
- Saves disk space

### 2. Complete Audit Trail
- Every change is tracked with timestamp and author
- Can see exactly what changed between any two points
- Can revert to any previous state

### 3. Better Collaboration
- Multiple users can work on same project
- Standard Git workflows (branches, merges, pull requests)
- Easy to share and reproduce

### 4. Powerful Querying
- Find all commits for a specific module
- Compare any two iterations
- Track debugging history
- View file evolution

### 5. Standard Tools
- Use any Git client (command line, VS Code, GitHub Desktop)
- Integrates with GitHub, GitLab, Bitbucket
- Can use git hooks for automation

### 6. Reproducibility
- Complete history of research process
- Can reproduce any intermediate state
- Clear documentation of decision points

## Migration Notes

### For Existing Projects

Existing projects with `.iterations/` directories will:
1. Automatically initialize Git on first run
2. Old iterations remain in `.iterations/` (can be safely deleted)
3. Future iterations will use Git only

To manually migrate:
```bash
cd your_project
research-assistant status your_project  # This initializes Git
rm -rf .iterations  # Optional: remove old iterations
```

### Git Configuration

Ensure Git is installed:
```bash
git --version
```

Configure Git if not already done:
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

### Disabling Git

If needed, Git can be disabled by setting `git_enabled=False` in the research_config.toml:
```toml
[execution]
git_enabled = false
```

## Implementation Checklist

- [x] Created GitTracker class with all core functionality
- [x] Integrated GitTracker into ResearchState
- [x] Updated analysis module with Git commits
- [x] Updated idea module with Git commits
- [x] Updated literature module with Git commits  
- [x] Updated methodology module with Git commits
- [x] Removed old iteration preservation code from CLI
- [x] Added new Git status commands to CLI
- [x] Created comprehensive test suite
- [x] Updated documentation

## Future Enhancements

Potential future improvements:
1. **Git Branches**: Automatically create branches for experimental iterations
2. **Git Tags**: Tag significant milestones (e.g., paper submission versions)
3. **Remote Push**: Optionally push to GitHub/GitLab automatically
4. **Git Hooks**: Custom hooks for validation or notifications
5. **Interactive Rebase**: Clean up commit history before sharing
6. **Blame Integration**: Show which agent/user made which changes
7. **Bisect**: Find when bugs were introduced using git bisect

## Notes

- Large data files are gitignored by default (prevents repository bloat)
- Plot images are tracked by default (remove comment in .gitignore to exclude)
- State file (.research_state.json) is always tracked (contains project metadata)
- Git operations are atomic and fast (typically <100ms per commit)
