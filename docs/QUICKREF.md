# Research Assistant - Quick Reference

## 🚀 Quick Start

```bash
# Install
cd research-assistant && pip install -e .

# Initialize
research-assistant init my_project

# Edit data description
vim my_project/input/data_description.md

# Run
research-assistant run --project my_project --interactive
```

## 📁 Project Structure

```
research-assistant/
├── src/research_assistant/      # Core package (1,165 lines)
│   ├── assistant.py             # Main orchestrator
│   ├── config.py                # Agent configurations
│   ├── state.py                 # State management
│   ├── orchestrator.py          # Multi-agent coordination
│   ├── tools.py                 # Tool definitions
│   ├── cli.py                   # CLI interface
│   └── modules/                 # Workflow modules (1,103 lines)
│       ├── idea.py              # Idea generation
│       ├── literature.py        # Literature review
│       ├── methodology.py       # Methodology development
│       ├── analysis.py          # Analysis execution
│       ├── paper.py             # Paper writing
│       └── review.py            # Final review
├── tests/                       # Test suite
├── docs/                        # Documentation
└── examples/                    # Usage examples
```

## 🤖 Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| idea_maker | gpt-4o | Generate ideas |
| idea_critic | o3-mini | Critique ideas |
| literature_researcher | gpt-4o | Search papers |
| methodologist | gpt-4o | Design methods |
| engineer | gpt-4o | Write code |
| executor | gpt-4o | Execute code |
| analyst | o3-mini | Interpret results |
| writer | gpt-4o | Write paper |
| reviewer | o3-mini | Review paper |

## 🔧 CLI Commands

```bash
research-assistant init <name>              # Create project
research-assistant idea --project <path>    # Generate idea
research-assistant literature --project <path>  # Literature review
research-assistant methodology --project <path> # Develop methods
research-assistant analysis --project <path>    # Execute analysis
research-assistant paper --project <path>       # Write paper
research-assistant review --project <path>      # Final review
research-assistant run --project <path>         # Full workflow
research-assistant resume <path> --from <module> # Resume
```

## 🐍 Python API

### Basic Usage
```python
import asyncio
from research_assistant import ResearchAssistant

async def main():
    assistant = ResearchAssistant(project_dir="./my_research")
    await assistant.initialize()
    
    assistant.load_data_description("input/data_description.md")
    
    await assistant.generate_idea(mode="interactive")
    await assistant.review_literature()
    await assistant.develop_methodology()
    await assistant.execute_analysis(require_approval=True)
    await assistant.write_paper(journal_format="nature")
    await assistant.review_paper()
    
    await assistant.cleanup()

asyncio.run(main())
```

### Custom Agents
```python
from research_assistant import AgentConfig

custom_agents = {
    "idea_maker": AgentConfig(
        name="idea_maker",
        role="idea_maker",
        model="claude-sonnet-4.5",
        temperature=0.9,
    ),
    "engineer": AgentConfig(
        name="engineer",
        role="engineer",
        model="deepseek-coder-v2:16b",
        provider={
            "type": "openai",
            "base_url": "http://localhost:11434/v1"
        },
    ),
}

assistant = ResearchAssistant(
    project_dir="./my_research",
    agent_configs=custom_agents
)
```

## 🛠️ Tools

| Tool | Purpose |
|------|---------|
| read_file | Load files from project |
| write_file | Save outputs |
| execute_code | Run Python code |
| create_plot | Generate visualizations |
| search_papers | Query arXiv |
| get_execution_error | Error details |
| save_intermediate_analysis | Track iterations |

## 📋 Workflow Modules

### 1. Idea Generation (5 steps)
- Generate 5 ideas → Critique → Refine top 2 → Final critique → Select best
- **Output**: `output/idea.md`

### 2. Literature Review (3 steps)
- Search papers → Synthesize → Analyst review
- **Output**: `output/literature.md`

### 3. Methodology (3 agents)
- Propose → Engineer review → Analyst review
- **Output**: `output/methodology.md`

### 4. Analysis (Nested loops)
- **Outer**: Analyst completeness evaluation (max 5 iterations)
- **Inner**: Engineer-executor debugging (max 10 attempts)
- **Outputs**: `output/analysis.md`, `output/code/*.py`, `output/plots/*.png`

### 5. Paper Writing (3 steps)
- Draft → Review → Revise
- **Output**: `output/paper.md`

### 6. Review (2 steps)
- Comprehensive review → Final polish
- **Output**: `output/paper_final.md`

## 🔄 Human-in-the-Loop

Every module:
1. Agent generates output
2. Saves to markdown file
3. Prompts user to review
4. User can edit manually
5. System reloads file
6. Continues to next step

## ⚙️ Configuration

### GitHub Copilot SDK
```bash
# Authenticate with GitHub Copilot
gh auth login
```
Requires active GitHub Copilot subscription.

### Local Models (Ollama)
```bash
ollama serve
ollama pull deepseek-coder-v2:16b
```

### Agent Config Parameters
```python
AgentConfig(
    name="agent_name",
    role="agent_role",
    model="gpt-4o",              # Model name
    temperature=0.7,             # 0-1
    reasoning_effort="high",     # O3: low/medium/high/xhigh
    system_message="...",        # Custom instructions
    tools=["tool1", "tool2"],   # Available tools
    streaming=True,              # Stream responses
    provider={...},              # Custom provider
)
```

## 📚 Documentation

- `README.md` - Project overview
- `docs/USAGE.md` - User guide (450 lines)
- `docs/ARCHITECTURE.md` - Technical docs (530 lines)
- `IMPLEMENTATION.md` - Implementation summary
- `SUMMARY.md` - Complete overview
- `examples/usage_examples.py` - 5 examples

## 🎯 Key Features

✅ Multi-agent architecture (9 specialized agents)
✅ Human-in-the-loop workflow
✅ Markdown-based I/O
✅ Nested iteration loops
✅ Fully configurable agents
✅ Resume from checkpoint
✅ CLI and Python API
✅ Code execution with approval
✅ Multiple model providers

## 🔗 Project Files

### Core (1,165 lines)
- assistant.py (216) - Main orchestrator
- config.py (139) - Agent configs
- state.py (126) - State management
- orchestrator.py (180) - Multi-agent coordination
- tools.py (263) - Tool definitions
- cli.py (233) - CLI interface

### Modules (1,103 lines)
- idea.py (186) - Idea generation
- literature.py (121) - Literature review
- methodology.py (135) - Methodology
- analysis.py (252) - Analysis execution
- paper.py (145) - Paper writing
- review.py (78) - Final review

### Total: 2,444 lines of Python + 3,000 lines of documentation

## 🆚 vs Denario

| Feature | Denario | Research Assistant |
|---------|---------|-------------------|
| Backend | cmbagent + AG2 | Copilot SDK |
| Workflow | Automated | Human-in-loop |
| Config | Fixed | Fully configurable |
| State | In-memory | File-based |
| Iteration | Single-pass | Nested loops |

## ✅ Status

**Complete and ready for use!**

All features from specification implemented, documented, and tested.
