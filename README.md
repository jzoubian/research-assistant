# Personal Research Assistant

A human-in-the-loop research assistant based on the [Denario methodology](https://arxiv.org/abs/2510.26887), built with the GitHub Copilot SDK.

> **Generated with GitHub Copilot & Claude Sonnet 4.5** - This codebase was developed using GitHub Copilot powered by Claude Sonnet 4.5.

## About

This project reimagines the [Denario scientific discovery pipeline](https://github.com/jzoubian/Denario) with human-in-the-loop control. While Denario (described in [arXiv:2510.26887](https://arxiv.org/abs/2510.26887)) provides fully automated multi-agent scientific research, this assistant enables researchers to review and refine outputs at each stage, using markdown files as the interface.

## Features

- **Multi-Agent Architecture**: 9 specialized agents with configurable models and parameters
- **Human-in-the-Loop**: Review and edit outputs at each stage with full iteration tracking
- **Markdown-Based Workflow**: All research artifacts are human-readable markdown files
- **Flexible Configuration**: Customize agents, models, and workflows
- **Iterative Refinement**: Support for nested iteration loops in analysis
- **Reproducible Execution**: Isolated environments (pixi, apptainer, nix, guix) for code execution
- **State Persistence**: Automatic save/resume of research progress
- **Iteration History**: Track all iterations with timestamps, inputs, outputs, and notes
- **Resource Management**: Specify and respect computational constraints (GPU, cluster, memory limits)

## Installation

```bash
cd research-assistant
pip install -e .
```

## Quick Start

```python
from research_assistant import ResearchAssistant
from research_assistant.state import ResearchState

# Create or load project state
state = ResearchState(project_dir="./my_research", env_manager="pixi")
assistant = ResearchAssistant(state, env_manager="pixi")

try:
    assistant.initialize()
    
    # Run workflow with manual review at each step
    assistant.run_idea_generation(mode="interactive")
    assistant.run_literature_review(mode="interactive")
    assistant.run_methodology_design(mode="interactive")
    assistant.run_analysis_execution(mode="interactive", require_approval=True)
    assistant.run_paper_writing(mode="interactive", journal_format="nature")
    assistant.run_review_synthesis(mode="interactive")
    
finally:
    assistant.cleanup()  # Automatically saves state
```

## CLI Usage

```bash
# Initialize new research project
research-assistant init my_research --env-manager pixi

# Run individual steps (state is automatically saved/loaded)
research-assistant idea --project my_research --interactive
research-assistant literature --project my_research
research-assistant methodology --project my_research
research-assistant analysis --project my_research --approve-code
research-assistant paper --project my_research --format nature
research-assistant review --project my_research

# Run full pipeline
research-assistant run --project my_research --interactive

# Resume from specific module
research-assistant resume my_research --from methodology

# Run from specific module onwards (all remaining modules)
research-assistant run --project my_research --start-from analysis

# View iteration history
research-assistant iterations my_research
research-assistant iterations my_research --module analysis

# Configure computational resources
research-assistant resources my_research --configure
research-assistant resources my_research --show
```

## Resource Management

The assistant can track and respect your available computational resources and constraints. This ensures that generated analysis code and execution strategies are appropriate for your hardware.

### Configuring Resources

```bash
# Interactive configuration
research-assistant resources my_research --configure

# View current configuration
research-assistant resources my_research --show
```

### Supported Resources

**Hardware:**
- CPU cores and memory
- GPU availability, type, count, and memory
- Cluster/HPC access (SLURM, PBS, SGE)
- Storage and scratch space

**Software:**
- MPI availability
- OpenMP support
- Internet access

**Constraints:**
- Maximum memory per job
- Maximum CPUs per job
- Maximum GPU per job
- Maximum runtime limits
- Resource quotas

### Resource File Format

Resources are stored in `resources.json`:

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
    "mpi_available": true,
    "openmp_available": true
  },
  "constraints": {
    "max_memory_per_job_gb": 200,
    "max_cpu_per_job": 32,
    "max_gpu_per_job": 2,
    "max_runtime_hours": 48,
    "has_quota": true,
    "quota_details": "1000 GPU-hours per month"
  }
}
```

The agents will use this information to:
- Generate appropriate parallelization strategies
- Respect memory and runtime limits
- Generate cluster submission scripts
- Avoid requesting unavailable resources

## Environment Management

The assistant supports multiple environment managers optimized for reproducible scientific computation:

- **pixi** (default): Modern conda alternative with fast dependency resolution and `pixi.toml`. Best for rapid development with scientific Python packages.
- **apptainer** (formerly Singularity): HPC-focused containers with `apptainer.def`. Designed for shared computing clusters, no root required, native MPI support.
- **nix**: Declarative reproducible builds with `default.nix`. Bit-for-bit reproducibility with precise versioning.
- **guix**: Functional package manager with `guix.scm`. Transactional operations, complete auditability, freedom-respecting software.

```bash
# Specify environment manager during initialization
research-assistant init my_research --env-manager apptainer

# Override environment manager for a run
research-assistant run --project my_research --env-manager nix
```

**Why these tools for scientific computing?**
- **Reproducibility**: All support precise dependency specification and version locking
- **HPC Compatibility**: Apptainer/Singularity is the standard for shared supercomputers
- **No root required**: All can run without administrator privileges
- **Scientific libraries**: Excellent support for NumPy, SciPy, CUDA, MPI, etc.
- **Long-term stability**: Package manifests ensure results stay reproducible for years

## Iteration Tracking

Every module run is tracked as an iteration with:
- **Iteration number**: Sequential count for each module
- **Timestamp**: When the iteration was performed
- **Input files**: Files used as input
- **Output files**: Files generated
- **Notes**: Description of what was done
- **Status**: Success, failed, or in-progress

View iteration history:
```bash
# Summary for all modules
research-assistant iterations my_research

# Detailed history for specific module
research-assistant iterations my_research --module analysis
```

## Architecture

### Specialized Agents

- **idea_maker**: Creative idea generation (GPT-5, high temperature)
- **idea_critic**: Critical evaluation (O3-mini, high reasoning)
- **literature_researcher**: Paper search and synthesis (GPT-5)
- **methodologist**: Methodology design (GPT-5)
- **engineer**: Code writing and debugging (GPT-4.1 or DeepSeek-coder)
- **executor**: Code execution and error reporting (GPT-4.1)
- **analyst**: Result interpretation and completeness evaluation (O3-mini)
- **writer**: Paper writing (GPT-5 or Gemini-2.5-flash)
- **reviewer**: Editorial feedback (O3-mini)

### Research Workflow Modules

1. **Idea Generation**: Multi-agent brainstorming and refinement
2. **Literature Review**: Automated paper search and synthesis
3. **Methodology Development**: Detailed methods design
4. **Analysis Execution**: Code generation, execution, and interpretation with nested iteration
5. **Paper Writing**: Manuscript synthesis
6. **Review & Refinement**: Editorial improvements

## Acknowledgments

This project is inspired by and based on:
- **[Denario](https://github.com/jzoubian/Denario)** - The original multi-agent scientific discovery system
- **Paper**: Zoubian et al. "The Denario project: Deep knowledge AI agents for scientific discovery" [arXiv:2510.26887](https://arxiv.org/abs/2510.26887)

The workflow philosophy, module structure, and multi-agent patterns are adapted from Denario's research pipeline.

## License

GPL-3.0 License. See [LICENSE](./LICENSE) for details.
