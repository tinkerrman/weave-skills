# Weave Skills

Claude Code skills for W&B Weave. Helps you easily implement LLM observability and evaluation.

[한국어](README.md)

## Installation

### Method 1: Plugin Marketplace (Recommended)

```bash
# Register marketplace
/plugin marketplace add https://github.com/YOUR_USERNAME/weave-skills

# Install plugin
/plugin install weave
```

### Method 2: Copy to Project

```bash
# Copy skill to project directory
cp -r skills/weave .claude/skills/
```

### Method 3: Global Skill

```bash
# Copy to home directory (available in all projects)
cp -r skills/weave ~/.claude/skills/
```

## Features

The `/weave` skill provides:

| Feature | Description | Keywords |
|---------|-------------|----------|
| **init** | Initialize Weave project | init, initialize, setup |
| **add-tracing** | Add tracing to functions | trace, tracing, @weave.op |
| **create-scorer** | Create evaluation Scorers | scorer, score, judge |
| **create-eval** | Build evaluation pipelines | eval, evaluation, pipeline |
| **create-dataset** | Create evaluation datasets | dataset, data, csv |

## Usage Examples

### Explicit Requests

```
User: "initialize weave"
User: "add tracing to LLM call functions"
User: "create a relevance scorer"
```

### Ambiguous Requests

```
User: "set up weave"
Claude: Analyzes codebase and recommends features.
```

### Analysis Requests

```
User: "check weave status"
Claude: Analyzes current state and reports (no file modifications).
```

## Directory Structure

```
weave-skills/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace registration
├── plugins/weave/            # Standalone plugin package
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── skills/weave/
│   │   └── SKILL.md
│   ├── assets/
│   └── references/
├── skills/weave/             # Main skill definition
│   ├── SKILL.md              # Router skill
│   ├── assets/               # Code examples
│   └── references/           # Detailed guides
├── demo/
│   └── rag-qa/               # Demo project
├── CLAUDE.md
└── README.md
```

## Demo

See skill application examples in the [demo/rag-qa](demo/rag-qa) folder.

## Weave Resources

- [Weave Official Docs](https://docs.wandb.ai/weave)
- [Weave GitHub](https://github.com/wandb/weave)
- [W&B Dashboard](https://wandb.ai/weave)

## License

MIT License
