# Human-in-the-Loop Improvements

This document describes the enhanced human-in-the-loop capabilities added to the research assistant.

## Overview

The research assistant now includes comprehensive iteration tracking, reproducible execution environments, and flexible workflow resumption capabilities. These improvements enable researchers to:

1. Track all iterations of each research module
2. Execute code in isolated, reproducible environments
3. Resume workflows from any point
4. Review complete iteration history

## Features

### 1. Iteration Tracking

Every module execution is tracked as a numbered iteration with comprehensive metadata.

**What's Tracked:**
- Iteration number (sequential for each module)
- Timestamp of execution
- Input files used
- Output files generated
- Descriptive notes about the iteration
- Status (success, failed, in-progress)

**Usage:**
```python
from research_assistant.state import ResearchState

# Load project state
state = ResearchState.load_state("./my_research")

# Get iteration count for a module
count = state.get_module_iteration_count("analysis")
print(f"Analysis has been run {count} times")

# Get latest iteration
latest = state.get_latest_iteration("analysis")
if latest:
    print(f"Last run: {latest.timestamp}")
    print(f"Status: {latest.status}")
    print(f"Output files: {latest.output_files}")
```

### 2. Environment Management

Execute code in isolated, reproducible environments with automatic dependency management.

**Supported Environment Managers:**

#### pixi (Default)
Modern conda alternative with fast dependency resolution, ideal for scientific Python workflows.
```bash
research-assistant init my_research --env-manager pixi
```

Generates: `pixi.toml`
```toml
[project]
name = "my_research"
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "osx-arm64", "win-64"]

[dependencies]
python = ">=3.10"
numpy = "*"
pandas = "*"
matplotlib = "*"
scipy = "*"
```

#### apptainer (formerly Singularity)
HPC-focused containers for reproducibility on shared computing clusters.
```bash
research-assistant init my_research --env-manager apptainer
```

Generates: `apptainer.def`
- Compatible with Singularity environments
- No root privileges required for execution
- Native MPI support for HPC applications
- Ideal for reproducibility on supercomputers

#### nix
Declarative reproducible builds with precise package versioning.
```bash
research-assistant init my_research --env-manager nix
```

Generates: `default.nix`
- Fully reproducible builds
- Declarative dependency specification
- Multiple Python versions side-by-side
- Source-based package management

#### guix
Functional package manager with transactional upgrades and rollbacks.
```bash
research-assistant init my_research --env-manager guix
```

Generates: `guix.scm`
- Scheme-based configuration
- Transactional package operations
- Bit-for-bit reproducibility
- Freedom-respecting software focus

**How It Works:**

1. **Initialization**: Environment is set up when the assistant initializes
   ```python
   assistant = ResearchAssistant(state, env_manager="pixi")
   assistant.initialize()  # Sets up environment
   ```

2. **Code Execution**: All analysis code runs in the isolated environment
   ```python
   success, stdout, stderr = env_manager.execute_code(
       code="import numpy as np; print(np.__version__)",
       timeout=300
   )
   ```

3. **Package Installation**: Dependencies added automatically or on-demand
   ```python
   env_manager.install_package("scikit-learn")
   ```

### 3. Workflow Resumption

Resume research from any module, running all subsequent modules automatically.

**CLI Usage:**
```bash
# Resume from specific module (runs that module only)
research-assistant resume my_research --from methodology

# Run from specific module onwards (runs all remaining modules)
research-assistant run --project my_research --start-from analysis
```

**Programmatic Usage:**
```python
assistant = ResearchAssistant(state, env_manager="pixi")
assistant.initialize()

# Run all modules from methodology onwards
assistant.run_from_module(
    start_module="methodology",
    mode="interactive",
    require_approval=True,
    journal_format="nature"
)

assistant.cleanup()
```

**Module Order:**
1. idea
2. literature
3. methodology
4. analysis
5. paper
6. review

### 4. State Persistence

Research state is automatically saved and can be resumed later.

**Automatic Saving:**
```python
assistant = ResearchAssistant(state, env_manager="pixi")
assistant.initialize()
assistant.run_idea_generation(mode="interactive")
assistant.cleanup()  # State automatically saved to .research_state.json
```

**Manual State Management:**
```python
from research_assistant.state import ResearchState

# Save state explicitly
state.save_state()

# Load existing state
state = ResearchState.load_state("./my_research")

# Check iteration history
for module in ["idea", "literature", "methodology"]:
    count = state.get_module_iteration_count(module)
    print(f"{module}: {count} iterations")
```

**State File Location:**
State is saved to `.research_state.json` in the project directory. This file contains:
- All module iteration history
- Current workflow stage
- Environment manager preference
- File paths and metadata

### 5. Iteration History Viewing

View complete iteration history from the CLI.

## 6. Resource Management

Specify and manage available computational resources to ensure generated code respects hardware constraints.

### Resource Configuration

**Interactive Setup:**
```bash
research-assistant resources my_research --configure
```

This will prompt for:
- CPU cores and RAM
- GPU availability, type, count, and memory
- Cluster/HPC access and scheduler type
- MPI and OpenMP availability
- Resource constraints (max memory, CPUs, runtime)
- Quota information

**View Configuration:**
```bash
research-assistant resources my_research --show
```

**Manual Configuration:**

Edit `resources.json` directly:
```json
{
  "resources": {
    "cpu_cores": 64,
    "cpu_memory_gb": 256,
    "gpu_available": true,
    "gpu_count": 4,
    "gpu_type": "A100",
    "gpu_memory_gb": 80,
    "cluster_available": true,
    "cluster_type": "SLURM",
    "cluster_partition": "gpu",
    "max_nodes": 10,
    "max_walltime_hours": 72,
    "storage_gb": 10000,
    "scratch_dir": "/scratch/username",
    "mpi_available": true,
    "openmp_available": true,
    "internet_access": true
  },
  "constraints": {
    "max_memory_per_job_gb": 200,
    "max_cpu_per_job": 32,
    "max_gpu_per_job": 2,
    "max_runtime_hours": 48,
    "prefer_cpu": false,
    "prefer_parallel": true,
    "has_quota": true,
    "quota_details": "1000 GPU-hours per month, 50TB storage",
    "required_packages": ["numpy", "scipy", "mpi4py"],
    "forbidden_packages": ["tensorflow"]
  }
}
```

### How Resources Are Used

The resource manager provides information to the agents that:

1. **Code Generation**: Engineers write code that respects memory limits and available parallelization
2. **Execution Planning**: Analysts determine optimal execution strategies based on resources
3. **Cluster Scripts**: Automatic generation of SLURM/PBS submission scripts with appropriate resource requests
4. **Validation**: Requirements validation before execution to prevent resource violations

**Example - GPU Code Generation:**
```python
# If resources show GPU available:
resources = state.resource_manager.resources
if resources.gpu_available:
    # Agent will generate GPU-accelerated code
    import cupy as cp
    data_gpu = cp.array(data)
else:
    # Falls back to CPU code
    import numpy as np
    data_cpu = np.array(data)
```

**Example - Cluster Submission:**
```python
# Generate SLURM script based on resources
script = state.resource_manager.generate_cluster_script(
    job_name="analysis",
    command="pixi run python analysis.py"
)
# Automatically includes:
# - Partition from resources.cluster_partition
# - GPU requests if available
# - Memory limits from constraints
# - Walltime from constraints
```

### Resource Validation

Before execution, the system can validate requirements:

```python
requirements = {
    'min_cpu_cores': 16,
    'min_memory_gb': 64,
    'requires_gpu': True,
    'min_gpu_memory_gb': 40,
    'requires_mpi': True,
}

can_run, issues = state.resource_manager.validate_requirements(requirements)
if not can_run:
    print("Cannot run analysis:")
    for issue in issues:
        print(f"  - {issue}")
```

### Use Cases

**1. Laptop Development:**
```json
{
  "resources": {
    "cpu_cores": 8,
    "cpu_memory_gb": 16,
    "gpu_available": false
  },
  "constraints": {
    "max_memory_per_job_gb": 12,
    "max_runtime_hours": 2
  }
}
```
Agents will generate lightweight, CPU-only code suitable for prototyping.

**2. Workstation:**
```json
{
  "resources": {
    "cpu_cores": 32,
    "cpu_memory_gb": 128,
    "gpu_available": true,
    "gpu_count": 2,
    "gpu_type": "RTX4090",
    "gpu_memory_gb": 24
  }
}
```
Agents can use GPU acceleration and multi-GPU strategies.

**3. HPC Cluster:**
```json
{
  "resources": {
    "cpu_cores": 128,
    "cpu_memory_gb": 512,
    "gpu_available": true,
    "gpu_count": 8,
    "gpu_type": "A100",
    "gpu_memory_gb": 80,
    "cluster_available": true,
    "cluster_type": "SLURM",
    "cluster_partition": "gpu",
    "max_nodes": 4,
    "mpi_available": true
  },
  "constraints": {
    "max_walltime_hours": 72,
    "has_quota": true,
    "quota_details": "10000 GPU-hours/month"
  }
}
```
Agents will generate:
- MPI-parallel code for multi-node execution
- SLURM submission scripts
- Efficient GPU utilization strategies
- Code that respects walltime limits

## 7. Iteration History Viewing (continued)

**All Modules Summary:**
```bash
research-assistant iterations my_research
```

Output:
```
┏━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Module      ┃ Iterations ┃ Last Run             ┃ Status  ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ IDEA        │ 3          │ 2024-01-15 14:23:45  │ success │
│ LITERATURE  │ 2          │ 2024-01-15 15:10:12  │ success │
│ METHODOLOGY │ 2          │ 2024-01-15 16:05:33  │ success │
│ ANALYSIS    │ 4          │ 2024-01-15 17:30:21  │ success │
│ PAPER       │ 1          │ 2024-01-15 18:45:10  │ success │
│ REVIEW      │ 1          │ 2024-01-15 19:12:55  │ success │
└─────────────┴────────────┴──────────────────────┴─────────┘
```

**Detailed Module History:**
```bash
research-assistant iterations my_research --module analysis
```

Output:
```
Iteration History for ANALYSIS

┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property  ┃ Value                                             ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Timestamp │ 2024-01-15 17:30:21                               │
│ Status    │ success                                           │
│ Input     │ output/methodology.md, input/data_description.md  │
│ Output    │ output/code/analysis.py, output/plots/result.png  │
│ Notes     │ Analysis iteration 4: Data visualization complete │
└───────────┴───────────────────────────────────────────────────┘
```

## Implementation Details

### ModuleIteration Model

Each iteration is stored as a Pydantic model:

```python
class ModuleIteration(BaseModel):
    """Record of a single module iteration."""
    iteration: int
    timestamp: datetime
    input_files: List[Path]
    output_files: List[Path]
    notes: str
    status: str  # "success", "failed", "in-progress"
```

### ResearchState Enhancements

The state now tracks iterations and environment preferences:

```python
class ResearchState(BaseModel):
    """Research project state with iteration tracking."""
    project_dir: Path
    env_manager: str = "pixi"
    module_iterations: Dict[str, List[ModuleIteration]] = {}
    
    def add_module_iteration(
        self,
        module: str,
        input_files: List[Path],
        output_files: List[Path],
        notes: str,
        status: str = "success"
    ) -> int:
        """Add an iteration and return iteration number."""
        ...
    
    def get_module_iteration_count(self, module: str) -> int:
        """Get number of iterations for a module."""
        ...
    
    def get_latest_iteration(self, module: str) -> Optional[ModuleIteration]:
        """Get most recent iteration for a module."""
        ...
    
    def save_state(self):
        """Save state to JSON file."""
        ...
    
    @classmethod
    def load_state(cls, project_dir: Path) -> "ResearchState":
        """Load state from JSON file."""
        ...
```

### EnvironmentManager Class

Manages isolated execution environments:

```python
class EnvironmentManager:
    """Manage isolated execution environments."""
    
    def __init__(self, project_dir: Path, env_type: str = "pixi"):
        ...
    
    def initialize_environment(self) -> Tuple[bool, str]:
        """Set up the execution environment."""
        ...
    
    def execute_code(
        self,
        code: str,
        timeout: int = 60
    ) -> Tuple[bool, str, str]:
        """Execute code in isolated environment."""
        ...
    
    def install_package(self, package: str) -> Tuple[bool, str]:
        """Install a package in the environment."""
        ...
```

## Usage Examples

### Example 1: Full Workflow with Iteration Tracking

```python
from research_assistant import ResearchAssistant
from research_assistant.state import ResearchState

# Create new project
state = ResearchState(project_dir="./cancer_research", env_manager="pixi")
assistant = ResearchAssistant(state, env_manager="pixi")

try:
    assistant.initialize()
    
    # Run complete workflow
    assistant.run_idea_generation(mode="interactive")
    print(f"Idea iterations: {state.get_module_iteration_count('idea')}")
    
    assistant.run_literature_review(mode="interactive")
    print(f"Literature iterations: {state.get_module_iteration_count('literature')}")
    
    assistant.run_methodology_design(mode="interactive")
    assistant.run_analysis_execution(mode="interactive", require_approval=True)
    assistant.run_paper_writing(mode="interactive")
    assistant.run_review_synthesis(mode="interactive")
    
finally:
    assistant.cleanup()  # Saves state automatically

# Later, resume the project
state = ResearchState.load_state("./cancer_research")
print(f"Project has {len(state.module_iterations)} modules with iterations")

# View latest analysis iteration
latest = state.get_latest_iteration("analysis")
if latest:
    print(f"Last analysis: {latest.timestamp}")
    print(f"Generated files: {latest.output_files}")
```

### Example 2: Resume After Manual Edits

```bash
# Initial run
research-assistant init cancer_research --env-manager pixi
research-assistant run --project cancer_research --interactive

# Make manual edits to methodology.md
# Resume from methodology onwards
research-assistant run --project cancer_research --start-from methodology

# View what changed
research-assistant iterations cancer_research --module methodology
```

### Example 3: Multiple Environment Types

```python
# Start with pixi for fast iteration
state = ResearchState(project_dir="./experiment", env_manager="pixi")
assistant = ResearchAssistant(state, env_manager="pixi")
assistant.initialize()
assistant.run_analysis_execution(mode="interactive")
assistant.cleanup()

# Switch to apptainer for HPC deployment
state = ResearchState.load_state("./experiment")
state.env_manager = "apptainer"
state.save_state()

assistant = ResearchAssistant(state, env_manager="apptainer")
assistant.initialize()
assistant.run_analysis_execution(mode="autonomous")  # Re-run in apptainer
assistant.cleanup()

# Compare results from different environments
pixi_iter = state.module_iterations["analysis"][0]
apptainer_iter = state.module_iterations["analysis"][1]
print(f"Pixi outputs: {pixi_iter.output_files}")
print(f"Apptainer outputs: {apptainer_iter.output_files}")
```

## Best Practices

1. **Use pixi for Development**: Fast dependency resolution and modern workflow
2. **Use apptainer for HPC**: Reproducibility on shared computing clusters
3. **Use nix for Full Reproducibility**: Bit-for-bit reproducible builds
4. **Use guix for Open Science**: Freedom-respecting, fully auditable software stack
5. **Track Iterations**: Always review iteration history before re-running modules
6. **Save State Frequently**: Call `state.save_state()` after important changes
7. **Resume Workflows**: Use `run_from_module()` instead of re-running everything
8. **Review Notes**: Add descriptive notes to iterations for future reference
9. **Environment Consistency**: Stick with one environment manager per project when possible
10. **HPC Considerations**: Use apptainer for batch jobs, nix/guix for local reproducibility

## Troubleshooting

### State File Corruption
```python
# Backup state file
import shutil
shutil.copy(".research_state.json", ".research_state.json.backup")

# Reset state if needed
state = ResearchState(project_dir="./my_research")
state.save_state()
```

### Environment Issues
```bash
# For pixi
rm -rf .pixi pixi.lock
research-assistant run --project my_research --env-manager pixi

# For apptainer
rm research_env.sif
research-assistant run --project my_research --env-manager apptainer

# For nix
nix-collect-garbage
research-assistant run --project my_research --env-manager nix

# For guix
guix gc
research-assistant run --project my_research --env-manager guix
```

### Iteration History Cleanup
```python
# Remove old iterations (keep last N)
state = ResearchState.load_state("./my_research")
for module in state.module_iterations:
    if len(state.module_iterations[module]) > 5:
        state.module_iterations[module] = state.module_iterations[module][-5:]
state.save_state()
```

## Future Enhancements

Potential improvements for consideration:

1. **Iteration Comparison**: Diff tool for comparing iterations
2. **Checkpointing**: Save intermediate states within modules
3. **Parallel Environments**: Run same analysis in multiple environments simultaneously
4. **Cloud Environments**: Support for cloud-based execution (AWS, GCP, Azure)
5. **Iteration Tags**: Tag important iterations for easy reference
6. **Rollback**: Restore project to previous iteration state
7. **Export**: Package specific iteration for sharing

## References

- [Denario Project](https://github.com/jzoubian/Denario)
- [Denario Paper (arXiv:2510.26887)](https://arxiv.org/abs/2510.26887)
- [pixi Documentation](https://prefix.dev/docs/pixi/overview)
- [GitHub Copilot SDK](https://github.com/copilot-extensions/copilot-sdk)
