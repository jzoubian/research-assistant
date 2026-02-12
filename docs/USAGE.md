# Research Assistant Usage Guide

## Installation

```bash
cd research-assistant
pip install -e .
```

## Quick Start

### 1. Initialize a New Project

```bash
research-assistant init my_research
```

This creates the following structure:
```
my_research/
├── input/
│   └── data_description.md
└── output/
    ├── plots/
    ├── code/
    └── intermediate/
```

### 2. Edit Data Description

Edit `my_research/input/data_description.md` to describe:
- Your available data sources
- Tools and computational resources
- Research domain and context
- Key questions of interest

### 3. Run Research Workflow

#### Option A: Interactive Mode (Recommended)

Run each module step-by-step with manual review:

```bash
# Generate research idea
research-assistant idea --project my_research --interactive

# Review and edit output/idea.md if needed, then continue...

# Literature review
research-assistant literature --project my_research

# Methodology development
research-assistant methodology --project my_research

# Analysis execution (will prompt for code approval)
research-assistant analysis --project my_research --approve-code

# Paper writing
research-assistant paper --project my_research --format nature

# Final review
research-assistant review --project my_research
```

#### Option B: Full Pipeline

Run complete workflow with pauses for editing:

```bash
research-assistant run --project my_research --interactive
```

#### Option C: Automatic Mode

Run without user intervention:

```bash
research-assistant run --project my_research --no-interactive --no-approve-code
```

### 4. Resume from Checkpoint

If you need to resume from a specific module:

```bash
research-assistant resume my_research --from methodology
```

## Python API Usage

### Basic Example

```python
import asyncio
from research_assistant import ResearchAssistant

async def main():
    # Initialize
    assistant = ResearchAssistant(project_dir="./my_research")
    await assistant.initialize()
    
    # Load data description
    assistant.load_data_description("input/data_description.md")
    
    # Run modules
    await assistant.generate_idea(mode="interactive")
    await assistant.review_literature()
    await assistant.develop_methodology()
    await assistant.execute_analysis(require_approval=True)
    await assistant.write_paper(journal_format="nature")
    await assistant.review_paper()
    
    # Cleanup
    await assistant.cleanup()

asyncio.run(main())
```

### Custom Agent Configuration

```python
from research_assistant import ResearchAssistant, AgentConfig

# Define custom agents
custom_agents = {
    "idea_maker": AgentConfig(
        name="idea_maker",
        role="idea_maker",
        model="claude-sonnet-4.5",
        temperature=0.9,
        system_message="You are a creative physicist...",
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

# Initialize with custom config
assistant = ResearchAssistant(
    project_dir="./my_research",
    agent_configs=custom_agents
)
```

## Agent Configuration

### Default Agents

| Agent | Role | Default Model | Purpose |
|-------|------|---------------|---------|
| idea_maker | Creative generation | gpt-4o | Generate research ideas |
| idea_critic | Critical evaluation | o3-mini | Critique and refine ideas |
| literature_researcher | Literature search | gpt-4o | Find and synthesize papers |
| methodologist | Method design | gpt-4o | Develop methodology |
| engineer | Code writing | gpt-4o | Write and debug code |
| executor | Code execution | gpt-4o | Execute code safely |
| analyst | Result interpretation | o3-mini | Analyze results scientifically |
| writer | Paper writing | gpt-4o | Write manuscript |
| reviewer | Editorial review | o3-mini | Review and improve paper |

### Configurable Parameters

```python
AgentConfig(
    name="agent_name",
    role="agent_role",
    model="gpt-4o",  # Model name
    temperature=0.7,  # Sampling temperature (0-1)
    reasoning_effort="high",  # For O3 models: low/medium/high/xhigh
    system_message="...",  # Custom instructions
    tools=["read_file", "write_file"],  # Available tools
    streaming=True,  # Stream responses
    provider={...},  # Custom provider config
)
```

### Using Local Models (Ollama)

```python
AgentConfig(
    name="engineer",
    role="engineer",
    model="deepseek-coder-v2:16b",
    provider={
        "type": "openai",
        "base_url": "http://localhost:11434/v1",
    },
)
```

## Workflow Modules

### Module 1: Idea Generation

Multi-agent workflow with iterative refinement:
1. Generate 5 initial ideas
2. Critique all ideas
3. Refine top 2 ideas
4. Final evaluation
5. Select best idea

**Output**: `output/idea.md`

### Module 2: Literature Review

Search and synthesize relevant papers:
1. Search academic databases
2. Synthesize findings
3. Identify research gaps

**Output**: `output/literature.md`

### Module 3: Methodology Development

Design detailed research methods:
1. Propose methodology
2. Engineer reviews feasibility
3. Analyst reviews scientific validity

**Output**: `output/methodology.md`

### Module 4: Analysis Execution

Execute analysis with nested iteration loops:

**Outer loop** (analyst-driven):
- Analyst evaluates if analysis is complete
- Requests additional analyses if needed
- Continues until scientifically sufficient

**Inner loop** (debugging):
- Engineer writes code
- Executor runs code
- Engineer debugs on errors
- Continues until successful execution

**Outputs**: 
- `output/analysis.md`
- `output/code/*.py`
- `output/plots/*.png`
- `output/intermediate/analysis_*.md`

### Module 5: Paper Writing

Write complete manuscript:
1. Writer creates draft
2. Reviewer provides feedback
3. Writer incorporates suggestions

**Output**: `output/paper.md`

### Module 6: Review & Refinement

Final editorial review:
1. Comprehensive review
2. Final improvements

**Outputs**:
- `output/paper_final.md`
- `output/review_notes.md`

## Tips & Best Practices

### 1. Data Description Quality

A detailed data description leads to better ideas and methodologies. Include:
- Specific data formats and sizes
- Available computational resources
- Domain-specific context
- Known challenges or constraints

### 2. Interactive Review

Always review outputs after each module:
- Ideas may need refinement based on your expertise
- Literature searches might miss key papers you know about
- Methodology may need adjustments for your specific setup
- Code should be reviewed before execution

### 3. Code Execution Safety

The `--approve-code` flag (default: True) prompts before running code. This is important because:
- Code might access file system
- Execution could take significant time
- You want to verify the approach first

### 4. Iteration Loops

The analysis module supports nested iterations:
- Let the analyst request additional analyses (outer loop)
- Let the engineer debug code automatically (inner loop)
- This creates more rigorous scientific results

### 5. Model Selection

Choose models based on task requirements:
- **Creative tasks** (ideas, writing): Higher temperature, GPT-4 or Claude
- **Critical analysis** (critique, review): O3-mini with high reasoning
- **Coding**: GPT-4.1 or local DeepSeek-coder
- **Fast tasks**: Gemini-2.5-flash

### 6. Resuming Work

If interrupted, you can resume from any module:
```bash
research-assistant resume my_research --from analysis
```

The system loads all previous outputs automatically.

## Troubleshooting

### API Keys

Ensure you have API keys configured for your chosen models:
```bash
export OPENAI_API_KEY="..."
export ANTHROPIC_API_KEY="..."
```

### Ollama for Local Models

To use local models:
```bash
# Start Ollama server
ollama serve

# Pull model
ollama pull deepseek-coder-v2:16b
```

### Code Execution Errors

If code execution fails repeatedly:
1. Check the error messages in terminal
2. Review generated code in `output/code/`
3. Edit the code manually if needed
4. The engineer will try to debug automatically (up to 10 attempts)

### Memory Issues

For large projects, consider:
- Using streaming mode (default: True)
- Breaking analysis into smaller steps
- Limiting literature search results

## Advanced Usage

See `examples/usage_examples.py` for:
- Custom agent orchestration
- Multi-agent conversations
- Specialized model configurations
- Automatic workflows

## Support

For issues or questions:
- Check examples in `examples/`
- Review source code documentation
- Consult the Copilot SDK documentation
