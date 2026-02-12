# Personal Research Assistant

A human-in-the-loop research assistant based on the [Denario methodology](https://arxiv.org/abs/2510.26887), built with the GitHub Copilot SDK.

> **Generated with GitHub Copilot & Claude Sonnet 4.5** - This codebase was developed using GitHub Copilot powered by Claude Sonnet 4.5.

## About

This project reimagines the [Denario scientific discovery pipeline](https://github.com/jzoubian/Denario) with human-in-the-loop control. While Denario (described in [arXiv:2510.26887](https://arxiv.org/abs/2510.26887)) provides fully automated multi-agent scientific research, this assistant enables researchers to review and refine outputs at each stage, using markdown files as the interface.

## Features

- **Multi-Agent Architecture**: 9 specialized agents with configurable models and parameters
- **Human-in-the-Loop**: Review and edit outputs at each stage
- **Markdown-Based Workflow**: All research artifacts are human-readable markdown files
- **Flexible Configuration**: Customize agents, models, and workflows
- **Iterative Refinement**: Support for nested iteration loops in analysis

## Installation

```bash
cd research-assistant
pip install -e .
```

## Quick Start

```python
import asyncio
from research_assistant import ResearchAssistant

async def main():
    assistant = ResearchAssistant(project_dir="./my_research")
    await assistant.initialize()
    
    # Load data description
    assistant.load_data_description("input/data_description.md")
    
    # Run workflow with manual review at each step
    await assistant.generate_idea(mode="interactive")
    await assistant.review_literature()
    await assistant.develop_methodology()
    await assistant.execute_analysis(require_approval=True)
    await assistant.write_paper(journal_format="nature")
    await assistant.review_paper()
    
    await assistant.cleanup()

asyncio.run(main())
```

## CLI Usage

```bash
# Initialize new research project
research-assistant init my_research

# Run individual steps
research-assistant idea --project my_research --interactive
research-assistant literature --project my_research
research-assistant methodology --project my_research
research-assistant analysis --project my_research --approve-code
research-assistant paper --project my_research --format nature
research-assistant review --project my_research

# Run full pipeline
research-assistant run --project my_research --interactive
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
