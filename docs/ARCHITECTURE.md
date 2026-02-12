# Research Assistant Architecture

## Overview

The Research Assistant is a multi-agent system built on the Copilot SDK that implements a human-in-the-loop research workflow based on the Denario methodology.

## Core Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    ResearchAssistant                         │
│  (Main orchestrator coordinating workflow)                   │
└────────┬────────────────────────────────────────────────────┘
         │
         ├─► ResearchState (State management)
         │   ├─ data_description
         │   ├─ idea
         │   ├─ literature
         │   ├─ methodology
         │   ├─ analysis
         │   ├─ paper
         │   └─ agent_history
         │
         ├─► AgentOrchestrator (Multi-agent coordination)
         │   └─► Copilot SDK Sessions (one per agent)
         │       ├─ idea_maker
         │       ├─ idea_critic
         │       ├─ literature_researcher
         │       ├─ methodologist
         │       ├─ engineer
         │       ├─ executor
         │       ├─ analyst
         │       ├─ writer
         │       └─ reviewer
         │
         └─► Tools (Shared functionality)
             ├─ read_file
             ├─ write_file
             ├─ execute_code
             ├─ create_plot
             ├─ search_papers
             ├─ get_execution_error
             └─ save_intermediate_analysis
```

## Module Architecture

### Module 1: Idea Generation

**Pattern**: Multi-round agent conversation

```
┌──────────────┐     5 ideas      ┌──────────────┐
│              │ ───────────────► │              │
│  idea_maker  │                  │ idea_critic  │
│              │ ◄─────────────── │              │
└──────────────┘    critique      └──────────────┘
       │                                  │
       │ refine top 2                     │
       ▼                                  ▼
       └──────────► iteration ◄───────────┘
                        │
                        ▼
                  final idea
```

**Workflow**:
1. Generate 5 initial ideas → `01_initial_ideas.md`
2. Critique all ideas → `02_critique.md`
3. Refine top 2 → `03_refined_ideas.md`
4. Final critique → `04_final_critique.md`
5. Select best → `idea.md`

### Module 2: Literature Review

**Pattern**: Sequential with review

```
┌──────────────────────┐
│ literature_researcher│ ──► search papers
└──────────────────────┘      │
                              ▼
                         synthesize
                              │
                              ▼
                    ┌──────────────┐
                    │   analyst    │ ──► review
                    └──────────────┘
                              │
                              ▼
                      literature.md
```

### Module 3: Methodology Development

**Pattern**: Proposal with multi-agent review

```
┌──────────────┐
│methodologist │ ──► propose methodology
└──────────────┘          │
                          ▼
              ┌───────────────────────┐
              │                       │
    ┌─────────▼────────┐   ┌─────────▼────────┐
    │    engineer      │   │     analyst      │
    │ (feasibility)    │   │ (validity)       │
    └─────────┬────────┘   └─────────┬────────┘
              │                       │
              └───────────┬───────────┘
                          ▼
                  methodology.md
```

### Module 4: Analysis Execution

**Pattern**: Nested iteration loops

```
┌───────────────────────────────────────────────────────────┐
│             OUTER LOOP (Analyst-driven)                   │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │      INNER LOOP (Debugging)                      │   │
│  │                                                  │   │
│  │  ┌──────────┐      ┌──────────┐               │   │
│  │  │ engineer │ ───► │ executor │               │   │
│  │  │          │      │          │               │   │
│  │  └────┬─────┘      └─────┬────┘               │   │
│  │       │                  │                     │   │
│  │       │    error?        │                     │   │
│  │       └──────◄───────────┘                     │   │
│  │       │ debug             │                     │   │
│  │       │                   │ success             │   │
│  └───────┼───────────────────┼─────────────────────┘   │
│          │                   ▼                          │
│          │          ┌──────────────┐                    │
│          │          │   analyst    │                    │
│          │          │ (interpret)  │                    │
│          │          └──────┬───────┘                    │
│          │                 │                            │
│          │       complete? │ need more?                 │
│          │                 │                            │
│          │   ◄─────────────┴──────────►                 │
│          │   yes                    no                  │
│          ▼                           │                  │
│      DONE                            │                  │
│                                      │                  │
└──────────────────────────────────────┼──────────────────┘
                                       │
                     request additional analysis
                                       │
                              ┌────────▼────────┐
                              │    engineer     │
                              │ (implement)     │
                              └─────────────────┘
```

**Key Features**:
- **Inner loop**: Up to 10 debug attempts per analysis iteration
- **Outer loop**: Up to 5 analysis refinement iterations
- **Human approval**: Optional before code execution
- **Intermediate saving**: Each iteration saved separately

### Module 5: Paper Writing

**Pattern**: Write-review-revise

```
┌──────────┐      draft      ┌──────────┐
│  writer  │ ───────────────► │ reviewer │
│          │                  │          │
└────┬─────┘                  └─────┬────┘
     │                              │
     │        feedback              │
     │ ◄────────────────────────────┘
     │
     ▼
  revise
     │
     ▼
 paper.md
```

### Module 6: Review & Refinement

**Pattern**: Final polish

```
┌──────────┐              ┌──────────┐
│ reviewer │ ───review──► │  writer  │
│          │              │          │
└──────────┘              └─────┬────┘
                                │
                                ▼
                       paper_final.md
```

## Data Flow

### File-Based State Management

```
project_dir/
├── input/
│   └── data_description.md ──────► [Loaded into ResearchState]
│                                            │
└── output/                                  │
    ├── idea.md ◄────────────────────────────┤
    ├── literature.md ◄──────────────────────┤
    ├── methodology.md ◄─────────────────────┤
    ├── analysis.md ◄────────────────────────┤
    ├── paper.md ◄───────────────────────────┤
    ├── paper_final.md ◄─────────────────────┘
    │
    ├── plots/
    │   ├── figure_01.png
    │   └── figure_02.png
    │
    ├── code/
    │   ├── analysis_01.py
    │   └── analysis_02.py
    │
    └── intermediate/
        ├── analysis_01.md
        └── analysis_02.md
```

### Human-in-the-Loop Pattern

```
1. Agent generates output
         │
         ▼
2. Save to markdown file
         │
         ▼
3. Prompt user to review
         │
         ▼
4. User can edit file manually
         │
         ▼
5. System reloads (potentially modified) file
         │
         ▼
6. Continue to next step
```

## Agent Communication

### Single Agent Call

```python
response = await orchestrator.send_to_agent(
    agent_name="idea_maker",
    prompt="Generate research ideas...",
    context={"data_description": "..."}
)
```

### Multi-Agent Conversation

```python
result = await orchestrator.multi_agent_conversation(
    agents=["idea_maker", "idea_critic", "idea_maker"],
    initial_prompt="Generate ideas...",
    rounds=3,
    context={"data_description": "..."}
)
```

## Tool System

Each agent has access to specific tools based on their role:

| Agent | Available Tools |
|-------|----------------|
| idea_maker | read_file, write_file |
| idea_critic | read_file |
| literature_researcher | read_file, write_file, search_papers |
| methodologist | read_file, write_file |
| engineer | read_file, write_file, create_plot |
| executor | execute_code, get_execution_error |
| analyst | read_file, write_file, save_intermediate_analysis |
| writer | read_file, write_file |
| reviewer | read_file, write_file |

## Configuration System

### Agent Configuration Hierarchy

```
DEFAULT_AGENTS (config.py)
        │
        ▼
AgentConfig objects ──► Merged with user overrides
        │
        ▼
ResearchAssistant initialization
        │
        ▼
AgentOrchestrator.create_agent()
        │
        ▼
Copilot SDK Session
```

### Configurable Parameters

```python
AgentConfig(
    name="agent_name",           # Unique identifier
    role="agent_role",           # Role type (affects default system message)
    model="gpt-4o",             # Model name
    temperature=0.7,            # Sampling temperature
    reasoning_effort="high",    # O3 models only
    system_message="...",       # Custom instructions
    tools=["tool1", "tool2"],  # Available tools
    streaming=True,             # Stream responses
    provider={...},             # Custom provider (e.g., Ollama)
    session_config={...}        # Additional session options
)
```

## Error Handling

### Code Execution Error Flow

```
engineer writes code
        │
        ▼
executor runs code ──── success ───► continue
        │
        │ error
        ▼
executor reports error
        │
        ▼
engineer debugs
        │
        ▼
attempt < max_attempts? ──yes──► retry
        │
        │ no
        ▼
    fail gracefully
```

### Session Error Handling

- Each agent session is independent
- Session failures don't crash entire workflow
- Errors logged to agent_history
- User can intervene via interactive mode

## State Management

### ResearchState Fields

```python
class ResearchState:
    # Project metadata
    project_dir: Path
    data_description: str
    
    # Research artifacts
    idea: str
    literature: str
    methodology: str
    analysis: str
    paper: str
    
    # File tracking
    plot_paths: list[Path]
    code_files: list[Path]
    intermediate_analyses: list[Path]
    
    # History
    agent_history: list[dict]
    completed_modules: set[str]
```

### State Persistence

- **Input**: Loaded from `input/data_description.md`
- **Output**: Saved to `output/*.md` files
- **Recovery**: State can be loaded from files to resume work
- **History**: All agent interactions logged

## Extension Points

### Adding New Agents

1. Define AgentConfig in `config.py`
2. Add system message for role
3. Assign appropriate tools
4. Create or modify module to use agent

### Adding New Tools

1. Define parameter model (Pydantic BaseModel)
2. Implement async tool function
3. Add to `tool_map` in `tools.py`
4. Assign to relevant agents

### Adding New Modules

1. Create module file in `modules/`
2. Implement `run_<module_name>()` function
3. Add method to ResearchAssistant
4. Update CLI with new command

## Performance Considerations

### Token Usage

- Streaming reduces memory for long responses
- Context management: Only relevant history passed to agents
- File-based state: Markdown files kept on disk

### Parallelization

- Independent agent sessions can run concurrently
- Current implementation: Sequential for clarity
- Future: Parallel tool calls where appropriate

### Caching

- Copilot SDK handles response caching
- State files cache intermediate results
- Can resume without re-running completed modules

## Security Considerations

### Code Execution

- Runs in subprocess (isolated from main process)
- Timeout limits prevent infinite loops
- User approval required (default) before execution
- Sandboxing depends on system configuration

### File Access

- Tools restricted to project directory
- Paths validated before file operations
- No arbitrary file system access

### API Keys

- Managed via environment variables
- Not stored in code or config files
- Different keys for different providers

## Comparison with Denario

| Aspect | Denario | Research Assistant |
|--------|---------|-------------------|
| Backend | cmbagent + AG2 | Copilot SDK |
| Workflow | Automated | Human-in-the-loop |
| State | In-memory | File-based |
| Editing | Post-generation | Per-module |
| Code execution | Automatic | User approval |
| Agent flexibility | Fixed | Fully configurable |
| Dependencies | Heavy | Minimal |
| Analysis iteration | Single-pass | Nested loops |

## Future Enhancements

- [ ] Web UI for project management
- [ ] Git integration for version control
- [ ] Template system for different research domains
- [ ] Parallel agent execution
- [ ] Advanced caching strategies
- [ ] Export to LaTeX/PDF
- [ ] Integration with reference managers (Zotero, Mendeley)
- [ ] Collaborative multi-user support
