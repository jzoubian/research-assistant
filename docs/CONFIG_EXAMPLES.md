# Research Assistant Configuration Examples

This directory contains example `research_config.toml` files for different research scenarios.

## Minimal Configuration (Quick Start)

**quick_start.toml**
```toml
project_name = "my_research"
env_manager = "pixi"

[execution]
mode = "interactive"
```

## Full Configuration (All Options)

**full_config.toml**
```toml
# Project metadata
project_name = "cosmology_analysis"
description = "CMB power spectrum analysis with Planck data"
version = "1.0.0"

# Environment configuration
env_manager = "pixi"  # Options: pixi, apptainer, nix, guix
python_version = "3.10"

# Execution settings
[execution]
mode = "interactive"  # Options: interactive, autonomous
require_code_approval = true
max_iterations = 3
timeout_seconds = 300

# Agent configurations
[agents.idea_maker]
name = "idea_maker"
model = "gpt-4"
temperature = 0.9

[agents.idea_critic]
name = "idea_critic"
model = "o3-mini"
temperature = 0.3
reasoning_effort = "high"

[agents.literature_researcher]
name = "literature_researcher"
model = "gpt-4"
temperature = 0.5

[agents.methodologist]
name = "methodologist"
model = "gpt-4"
temperature = 0.7

[agents.engineer]
name = "engineer"
model = "gpt-4.1"
temperature = 0.3

[agents.executor]
name = "executor"
model = "gpt-4.1"
temperature = 0.2

[agents.analyst]
name = "analyst"
model = "o3-mini"
temperature = 0.5
reasoning_effort = "medium"

[agents.writer]
name = "writer"
model = "gpt-4"
temperature = 0.7

[agents.reviewer]
name = "reviewer"
model = "o3-mini"
temperature = 0.5
reasoning_effort = "high"

# Module settings
[modules.idea]
enabled = true
max_iterations = 3

[modules.literature]
enabled = true
max_papers = 20

[modules.methodology]
enabled = true

[modules.analysis]
enabled = true
max_retries = 3

[modules.paper]
enabled = true
journal_format = "nature"

[modules.review]
enabled = true

# File paths
[paths]
input_dir = "input"
output_dir = "output"
data_description = "input/data_description.md"

# Custom parameters
[custom]
domain = "cosmology"
telescope = "Planck"
```

## Autonomous Mode (No Human Input)

**autonomous.toml**
```toml
project_name = "auto_research"
env_manager = "pixi"

[execution]
mode = "autonomous"  # No human interaction
require_code_approval = false
max_iterations = 5
timeout_seconds = 600

[agents.idea_maker]
name = "idea_maker"
model = "gpt-4"
temperature = 0.8

[agents.analyst]
name = "analyst"
model = "o3-mini"
reasoning_effort = "high"

# All modules enabled by default
```

## HPC/Cluster Configuration

**hpc_cluster.toml**
```toml
project_name = "hpc_simulation"
description = "Large-scale cosmological simulation analysis"
env_manager = "apptainer"  # Best for HPC
python_version = "3.10"

[execution]
mode = "interactive"
require_code_approval = true  # Review before submitting jobs
max_iterations = 2
timeout_seconds = 3600  # Longer timeout for cluster jobs

[agents.engineer]
name = "engineer"
model = "gpt-4.1"
temperature = 0.2  # More conservative for expensive cluster jobs

[agents.analyst]
name = "analyst"
model = "o3-mini"
temperature = 0.3
reasoning_effort = "high"

[modules.analysis]
enabled = true
max_retries = 1  # Fewer retries to save cluster resources

[custom]
cluster_type = "SLURM"
partition = "gpu"
use_mpi = true
```

## Quick Prototyping

**prototype.toml**
```toml
project_name = "prototype"
env_manager = "pixi"

[execution]
mode = "interactive"
require_code_approval = false  # Quick iteration
max_iterations = 5
timeout_seconds = 120  # Short timeout

[agents.engineer]
name = "engineer"
model = "gpt-4.1"
temperature = 0.5  # More creative for exploration

# Disable expensive modules
[modules.literature]
enabled = false  # Skip literature review

[modules.review]
enabled = false  # Skip review for prototyping
```

## Publication-Ready

**publication.toml**
```toml
project_name = "publication_draft"
description = "Final analysis for Nature submission"
version = "1.0.0"
env_manager = "nix"  # Maximum reproducibility

[execution]
mode = "interactive"
require_code_approval = true
max_iterations = 3
timeout_seconds = 600

[agents.writer]
name = "writer"
model = "gpt-4"
temperature = 0.7
max_tokens = 4000

[agents.reviewer]
name = "reviewer"
model = "o3-mini"
temperature = 0.3
reasoning_effort = "high"

[modules.paper]
enabled = true
journal_format = "nature"

[modules.review]
enabled = true

[custom]
target_journal = "Nature"
word_limit = 3000
figures_limit = 4
```

## Domain-Specific: Astrophysics

**astrophysics.toml**
```toml
project_name = "supernova_analysis"
description = "Type Ia supernova cosmology"
env_manager = "pixi"

[execution]
mode = "interactive"
max_iterations = 3

[modules.literature]
enabled = true
max_papers = 50  # More papers for comprehensive review

[modules.paper]
journal_format = "arxiv"  # Astrophysics preprint style

[custom]
domain = "astrophysics"
subdomain = "cosmology"
data_source = "Pantheon+ catalog"
redshift_range = [0.01, 2.3]
```

## Domain-Specific: Machine Learning

**machine_learning.toml**
```toml
project_name = "ml_experiment"
description = "Neural network architecture search"
env_manager = "pixi"

[execution]
mode = "interactive"
require_code_approval = true  # Review before training
timeout_seconds = 7200  # Long training times

[agents.engineer]
name = "engineer"
model = "gpt-4.1"
temperature = 0.4

[modules.analysis]
enabled = true
max_retries = 3

[custom]
domain = "machine_learning"
framework = "pytorch"
use_gpu = true
wandb_logging = true
```

## Multi-Stage Analysis

**multistage.toml**
```toml
project_name = "multistage_analysis"
description = "Analysis with multiple phases"

[execution]
mode = "interactive"

# First stage: exploration
[modules.idea]
enabled = true
max_iterations = 5

[modules.literature]
enabled = true
max_papers = 30

# Second stage: methodology
[modules.methodology]
enabled = true

[modules.analysis]
enabled = true
max_retries = 3

# Third stage: publication
[modules.paper]
enabled = true
journal_format = "pnas"

[modules.review]
enabled = true

[custom]
stage = "full_pipeline"
checkpoint_after_each_module = true
```

## Usage

To use an example configuration:

```bash
# Copy example to your project
cp config_examples/hpc_cluster.toml my_project/research_config.toml

# Edit as needed
research-assistant config my_project --edit

# Validate
research-assistant config my_project --validate

# Run with configuration
research-assistant run my_project
```

## Creating Custom Configurations

```bash
# Export template
research-assistant config . --export-template --output my_custom.toml

# Edit template
nano my_custom.toml

# Copy to project
cp my_custom.toml my_project/research_config.toml
```

## Version Control

Add configuration to git:

```bash
git add research_config.toml
git commit -m "Add project configuration"
```

Share with collaborators:
```bash
# Clone and run
git clone <repo>
cd <project>
research-assistant run .
```
