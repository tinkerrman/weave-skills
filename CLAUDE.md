# Weave Skills - Claude Code Instructions

This project provides W&B Weave integration skills for Claude Code.

## Structure

```
weave-skills/
├── .claude-plugin/
│   └── marketplace.json      # Plugin marketplace metadata
├── plugins/weave/            # Standalone plugin package
│   ├── .claude-plugin/
│   │   └── plugin.json       # Plugin metadata
│   ├── skills/weave/
│   │   └── SKILL.md          # Router skill (mirror)
│   ├── assets/               # Assets (mirror)
│   └── references/           # References (mirror)
├── skills/weave/             # Main skill definition
│   ├── SKILL.md              # Router (~140 lines)
│   ├── assets/               # All code examples
│   └── references/           # Detailed feature guides
├── demo/                     # Demo project
└── README.md
```

## Skill: /weave

The `/weave` skill provides comprehensive W&B Weave support:

### Features

| Feature | Description | Reference |
|---------|-------------|-----------|
| init | Initialize Weave project | references/init.md |
| add-tracing | Add @weave.op tracing | references/add-tracing.md |
| create-scorer | Create evaluation scorers | references/create-scorer.md |
| create-eval | Build evaluation pipelines | references/create-eval.md |
| create-dataset | Create evaluation datasets | references/create-dataset.md |
| create-model | Create weave.Model subclasses | references/create-model.md |
| create-prompt | Create versioned prompts | references/create-prompt.md |
| add-guardrails | Add production guardrails | references/add-guardrails.md |

### Usage

1. **Explicit request**: "initialize weave", "add tracing", "create scorer"
2. **Ambiguous request**: Skill analyzes codebase and recommends features
3. **Analysis only**: "check weave status", "what needs to be done"

### Workflow

The router SKILL.md handles:
1. Request classification via keyword matching
2. Codebase analysis for ambiguous requests
3. Feature execution by reading appropriate reference
4. Complementary feature suggestions after completion

## Assets

Code examples in `assets/`:
- `init_examples.py` - weave.init() patterns
- `tracing_examples.py` - @weave.op usage
- `scorer_examples.py` - Scorer implementations
- `eval_examples.py` - Evaluation workflows
- `dataset_examples.py` - Dataset creation
- `model_examples.py` - weave.Model patterns
- `prompt_examples.py` - Prompt management
- `guardrail_examples.py` - Guardrail implementations

## References

Detailed guides in `references/`:
- `init.md` - Project initialization workflow
- `add-tracing.md` - Tracing addition workflow
- `create-scorer.md` - Scorer creation workflow
- `create-eval.md` - Evaluation pipeline workflow
- `create-dataset.md` - Dataset creation workflow
- `create-model.md` - Model creation workflow
- `create-prompt.md` - Prompt management workflow
- `add-guardrails.md` - Guardrail addition workflow
