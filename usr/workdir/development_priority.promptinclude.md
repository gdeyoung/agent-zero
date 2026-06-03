# Development Priority Rule (MANDATORY)

> **Created:** 2026-06-03
> **Source:** User directive

---

## THE RULE

**When adding ANY new functionality to the Agent Zero platform, always follow this priority order:**

| Priority | Approach | When to Use |
|----------|----------|-------------|
| **1. PLUGIN FIRST** | Create a plugin in `/a0/usr/plugins/<name>/` | Default choice for ALL new features. Bundles tools, extensions, prompts, API endpoints, config. Self-contained, survives updates. |
| **2. SKILL SECOND** | Create a skill in `/a0/usr/skills/<name>/` with `SKILL.md` | When the feature is instructional guidance or reusable instructions rather than executable code. |
| **3. PATCH LAST** | Modify core framework files (`/a0/agent.py`, `/a0/models.py`, etc.) | LAST RESORT only when plugin/skill approaches are technically impossible. Must be documented and tracked. |

## Why This Order

| Approach | Survives Updates | Self-Contained | Discoverable | Maintainable |
|----------|----------------|---------------|--------------|-------------|
| **Plugin** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Easy |
| **Skill** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Easy |
| **Patch** | ❌ No | ❌ No | ❌ No | ❌ Fragile |

## Examples

| Feature | Correct Approach | Why |
|---------|-----------------|-----|
| Session guard (intercept tool calls) | **Plugin** (`_session_guard`) | Needs extension hook + config + prompts |
| Backup automation | **Plugin** (`_backup_manager`) | Needs tools + pipeline + helpers |
| KG pipeline scripts | **Plugin** (`_kg_pipeline`) | Needs tools + config + helpers |
| Meeting intelligence docs | **Skill** (`meeting-intelligence`) | Instructional guidance |
| LLM response format fix | **Patch** | Core framework bug, no plugin hook available |

## Plugin Structure Reference
```
/a0/usr/plugins/<name>/
├── plugin.yaml                    # Manifest (always_enabled: true for system plugins)
├── default_config.yaml            # Configuration
├── tools/                         # Agent tools
│   └── my_tool.py
├── extensions/python/<hook_point>/ # Lifecycle extensions
│   └── _10_my_extension.py
├── prompts/                       # Prompt fragments
│   └── agent.system.tool.my_tool.md
├── api/                           # Web UI endpoints (optional)
│   └── my_endpoint.py
└── helpers/                       # Internal helpers (optional)
    └── my_helper.py
```

## Enforcement

Before implementing ANY new feature, ask:
1. **Can this be a plugin?** → Yes? → Make it a plugin.
2. **Can this be a skill?** → Yes? → Make it a skill.
3. **Must this patch core code?** → Document WHY in the commit message.
