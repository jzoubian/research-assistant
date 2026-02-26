"""Git-based iteration and change tracking for research workflow."""

import subprocess
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from rich.console import Console

console = Console()


class GitTracker:
    """Track research iterations and changes using Git."""
    
    def __init__(self, project_dir: Path):
        """Initialize Git tracker for a project.
        
        Args:
            project_dir: Project directory path
        """
        self.project_dir = project_dir.resolve()
        self.git_dir = self.project_dir / ".git"
        
    def _run_git(self, args: List[str], check: bool = True, capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a git command in the project directory.
        
        Args:
            args: Git command arguments
            check: Raise exception on non-zero exit code
            capture_output: Capture stdout/stderr
            
        Returns:
            Completed process
            
        Raises:
            RuntimeError: If Git command fails (when check=True)
        """
        cmd = ["git", "-C", str(self.project_dir)] + args
        try:
            return subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=True
            )
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Git command failed: {' '.join(cmd)}[/red]")
            console.print(f"[red]Error: {e.stderr}[/red]")
            if check:
                raise RuntimeError(f"Git command failed: {e.stderr}") from e
            return e
        except FileNotFoundError:
            console.print("[red]Git is not installed or not in PATH[/red]")
            raise RuntimeError("Git is not installed. Please install Git to use version tracking.")
    
    def is_initialized(self) -> bool:
        """Check if Git repository is initialized."""
        return self.git_dir.exists() and self.git_dir.is_dir()
    
    def initialize(self) -> None:
        """Initialize Git repository with appropriate .gitignore."""
        if self.is_initialized():
            console.print("[yellow]Git repository already initialized[/yellow]")
            return
        
        console.print("[cyan]Initializing Git repository...[/cyan]")
        self._run_git(["init"])
        
        # Create comprehensive .gitignore
        gitignore_content = """# Research Assistant - Git Ignore Rules

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Environment managers
.pixi/
.venv/
venv/
env/
.conda/

# Data files (prevent tracking large datasets)
*.csv
*.tsv
*.parquet
*.h5
*.hdf5
*.pkl
*.pickle
*.npy
*.npz
*.mat

# Large binary files
*.pdf
*.zip
*.tar
*.tar.gz
*.tgz
*.rar
*.7z

# Image outputs (optional - remove lines if you want to track plots)
# *.png
# *.jpg
# *.jpeg
# *.gif
# *.svg

# Model checkpoints and weights
*.pt
*.pth
*.ckpt
*.safetensors
*.bin
*.h5
*.pb
*.onnx

# Jupyter notebook checkpoints
.ipynb_checkpoints/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Temporary files
*.log
*.tmp
tmp/
temp/

# Research Assistant - keep these tracked
!.research_state.json
!research_config.toml
"""
        
        gitignore_path = self.project_dir / ".gitignore"
        gitignore_path.write_text(gitignore_content)
        
        # Add .gitignore
        self._run_git(["add", ".gitignore"])
        self._run_git(["commit", "-m", "Initialize research project with Git tracking"])
        
        console.print("[green]✓ Git repository initialized[/green]")
    
    def ensure_initialized(self) -> None:
        """Ensure Git repository is initialized, initialize if not."""
        if not self.is_initialized():
            self.initialize()
    
    def get_status(self) -> str:
        """Get current Git status.
        
        Returns:
            Git status output
        """
        result = self._run_git(["status", "--short"])
        return result.stdout
    
    def has_changes(self) -> bool:
        """Check if there are uncommitted changes.
        
        Returns:
            True if there are changes
        """
        status = self.get_status()
        return bool(status.strip())
    
    def has_staged_changes(self) -> bool:
        """Check if there are staged changes ready to commit.
        
        Returns:
            True if there are staged changes
        """
        result = self._run_git(["diff", "--cached", "--quiet"], check=False)
        return result.returncode != 0
    
    def stage_files(self, patterns: List[str]) -> None:
        """Stage files matching patterns.
        
        Args:
            patterns: File patterns to stage (e.g., ["output/*.md", ".research_state.json"])
        """
        for pattern in patterns:
            # Use git add with --force to override .gitignore if needed for state files
            self._run_git(["add", pattern], check=False)
    
    def stage_all_changes(self) -> None:
        """Stage all tracked and modified files (not untracked files unless explicitly added)."""
        # Use git add -u to stage only modifications to tracked files
        # This avoids accidentally staging unwanted untracked files
        self._run_git(["add", "-u"])
        
        # Also stage specific important files even if untracked
        important_files = [".research_state.json", "research_config.toml", ".gitignore"]
        for file in important_files:
            file_path = self.project_dir / file
            if file_path.exists():
                self._run_git(["add", str(file)], check=False)
    
    def commit(self, message: str, author: Optional[str] = None) -> str:
        """Commit staged changes.
        
        Args:
            message: Commit message
            author: Optional author string (e.g., "Agent Name <agent@research-assistant>")
            
        Returns:
            Commit hash
        """
        if not self.has_changes():
            console.print("[dim]No changes to commit[/dim]")
            return self.get_current_commit()
        
        args = ["commit", "-m", message]
        if author:
            args.extend(["--author", author])
        
        self._run_git(args)
        return self.get_current_commit()
    
    def commit_step(self, module: str, step: str, description: str = "") -> str:
        """Commit changes for a specific module step.
        
        Args:
            module: Module name (e.g., "idea", "analysis")
            step: Step name (e.g., "generation", "execution", "interpretation")
            description: Optional description
            
        Returns:
            Commit hash or None if no changes to commit
        """
        self.stage_all_changes()
        
        # Only commit if there are staged changes
        if not self.has_staged_changes():
            return None
        
        message_parts = [f"[{module}] {step}"]
        if description:
            message_parts.append(f": {description}")
        
        message = "".join(message_parts)
        return self.commit(message)
    
    def commit_iteration(self, module: str, iteration: int, description: str = "") -> str:
        """Commit changes for a module iteration.
        
        Args:
            module: Module name
            iteration: Iteration number
            description: Optional description
            
        Returns:
            Commit hash or None if no changes to commit
        """
        self.stage_all_changes()
        
        # Only commit if there are staged changes
        if not self.has_staged_changes():
            return None
        
        message_parts = [f"[{module}] Iteration {iteration}"]
        if description:
            message_parts.append(f": {description}")
        
        message = "".join(message_parts)
        return self.commit(message)
    
    def commit_debug_attempt(self, module: str, iteration: int, attempt: int, error: str = "") -> str:
        """Commit changes for a debug attempt.
        
        Args:
            module: Module name
            iteration: Iteration number
            attempt: Debug attempt number
            error: Error message summary
            
        Returns:
            Commit hash or None if no changes to commit
        """
        self.stage_all_changes()
        
        # Only commit if there are staged changes
        if not self.has_staged_changes():
            return None
        
        message_parts = [f"[{module}] Iteration {iteration} - Debug attempt {attempt}"]
        if error:
            # Truncate error to first line for commit message
            error_summary = error.split('\n')[0][:60]
            message_parts.append(f": {error_summary}")
        
        message = "".join(message_parts)
        return self.commit(message)
    
    def commit_user_input(self, module: str, action: str, notes: str = "") -> str:
        """Commit user input or decision.
        
        Args:
            module: Module name
            action: User action (e.g., "approved", "edited", "continued")
            notes: Optional user notes
            
        Returns:
            Commit hash or None if no changes to commit
        """
        self.stage_all_changes()
        
        # Only commit if there are staged changes
        if not self.has_staged_changes():
            return None
        
        message_parts = [f"[{module}] User {action}"]
        if notes:
            message_parts.append(f": {notes}")
        
        message = "".join(message_parts)
        return self.commit(message, author="User <user@research-assistant>")
    
    def get_current_commit(self) -> str:
        """Get current commit hash.
        
        Returns:
            Commit hash (short form)
        """
        result = self._run_git(["rev-parse", "--short", "HEAD"])
        return result.stdout.strip()
    
    def get_commit_message(self, commit: str = "HEAD") -> str:
        """Get commit message.
        
        Args:
            commit: Commit reference (default: HEAD)
            
        Returns:
            Commit message
        """
        result = self._run_git(["log", "-1", "--pretty=%B", commit])
        return result.stdout.strip()
    
    def get_log(self, max_count: int = 20, module: Optional[str] = None) -> List[Dict[str, str]]:
        """Get commit log.
        
        Args:
            max_count: Maximum number of commits to retrieve
            module: Filter by module name (e.g., "analysis")
            
        Returns:
            List of commit info dicts with keys: hash, message, author, date
        """
        args = [
            "log",
            f"--max-count={max_count}",
            "--pretty=format:%h|%s|%an|%ai"
        ]
        
        if module:
            args.append(f"--grep=\\[{module}\\]")
        
        result = self._run_git(args)
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 3)
            if len(parts) == 4:
                commits.append({
                    'hash': parts[0],
                    'message': parts[1],
                    'author': parts[2],
                    'date': parts[3]
                })
        
        return commits
    
    def get_diff(self, from_commit: str = "HEAD~1", to_commit: str = "HEAD", 
                 paths: Optional[List[str]] = None) -> str:
        """Get diff between commits.
        
        Args:
            from_commit: Starting commit
            to_commit: Ending commit
            paths: Optional list of paths to limit diff
            
        Returns:
            Diff output
        """
        args = ["diff", from_commit, to_commit]
        if paths:
            args.extend(["--"] + paths)
        
        result = self._run_git(args)
        return result.stdout
    
    def get_iteration_diff(self, module: str, from_iteration: int, to_iteration: int) -> str:
        """Get diff between two iterations of a module.
        
        Args:
            module: Module name
            from_iteration: Starting iteration number
            to_iteration: Ending iteration number
            
        Returns:
            Diff output
        """
        # Find commits for the iterations
        from_commits = self._find_iteration_commits(module, from_iteration)
        to_commits = self._find_iteration_commits(module, to_iteration)
        
        if not from_commits or not to_commits:
            return "Could not find commits for specified iterations"
        
        # Use the last commit of each iteration
        return self.get_diff(from_commits[-1], to_commits[-1])
    
    def _find_iteration_commits(self, module: str, iteration: int) -> List[str]:
        """Find all commits for a specific iteration.
        
        Args:
            module: Module name
            iteration: Iteration number
            
        Returns:
            List of commit hashes
        """
        result = self._run_git([
            "log",
            "--all",
            f"--grep=\\[{module}\\] Iteration {iteration}",
            "--pretty=format:%h"
        ])
        
        commits = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        return commits
    
    def get_file_history(self, filepath: str, max_count: int = 10) -> List[Dict[str, str]]:
        """Get commit history for a specific file.
        
        Args:
            filepath: File path relative to project directory
            max_count: Maximum number of commits to retrieve
            
        Returns:
            List of commit info dicts
        """
        args = [
            "log",
            f"--max-count={max_count}",
            "--pretty=format:%h|%s|%an|%ai",
            "--",
            filepath
        ]
        
        result = self._run_git(args, check=False)
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = line.split('|', 3)
            if len(parts) == 4:
                commits.append({
                    'hash': parts[0],
                    'message': parts[1],
                    'author': parts[2],
                    'date': parts[3]
                })
        
        return commits
    
    def get_module_status(self, module: str) -> Dict[str, any]:
        """Get comprehensive status for a module.
        
        Args:
            module: Module name
            
        Returns:
            Status dict with iteration count, last commit, etc.
        """
        commits = self.get_log(max_count=100, module=module)
        
        # Count iterations
        iterations = set()
        for commit in commits:
            if "Iteration" in commit['message']:
                # Extract iteration number
                import re
                match = re.search(r'Iteration (\d+)', commit['message'])
                if match:
                    iterations.add(int(match.group(1)))
        
        return {
            'module': module,
            'total_commits': len(commits),
            'iteration_count': len(iterations),
            'iterations': sorted(iterations),
            'last_commit': commits[0] if commits else None,
            'all_commits': commits
        }
    
    def print_status(self) -> None:
        """Print formatted Git status."""
        console.print("\n[bold cyan]Git Status[/bold cyan]")
        
        status = self.get_status()
        if status:
            console.print(status)
        else:
            console.print("[green]Working tree clean[/green]")
        
        # Show last few commits
        commits = self.get_log(max_count=5)
        if commits:
            console.print("\n[bold cyan]Recent Commits[/bold cyan]")
            for commit in commits:
                console.print(f"  [yellow]{commit['hash']}[/yellow] {commit['message']} [dim]({commit['date'][:10]})[/dim]")
    
    def print_module_status(self, module: str) -> None:
        """Print formatted status for a specific module.
        
        Args:
            module: Module name
        """
        status = self.get_module_status(module)
        
        console.print(f"\n[bold cyan]Module: {module}[/bold cyan]")
        console.print(f"Total commits: {status['total_commits']}")
        console.print(f"Iterations: {status['iteration_count']}")
        
        if status['iterations']:
            console.print(f"Iteration numbers: {', '.join(map(str, status['iterations']))}")
        
        if status['last_commit']:
            last = status['last_commit']
            console.print(f"\nLast commit:")
            console.print(f"  [yellow]{last['hash']}[/yellow] {last['message']}")
            console.print(f"  [dim]{last['author']} - {last['date'][:19]}[/dim]")
        
        # Show recent commits
        if len(status['all_commits']) > 1:
            console.print(f"\nRecent commits:")
            for commit in status['all_commits'][:5]:
                console.print(f"  [yellow]{commit['hash']}[/yellow] {commit['message']}")
