# ToyWorks Agent Skills

This repository hosts public agent skills maintained by the ToyWorks Team.

## What are Agent Skills?

Agent Skills are folders of instructions, scripts, and resources that agents can discover and use to do things more accurately and efficiently. They work across any AI agent that supports the [open Agent Skills standard](https://agentskills.io).

## Available Skills
<!-- START:Available-Skills -->

| Skill | Description |
| ----- | ----------- |
| t3-hardware-scoring | The MantaBase T3 Hardware Audit System classifies a hardware product as Tool, Toy, or Trash. It brand-blinds the source material, scores it with three independent auditors working from fixed rubrics and verbatim evidence, revalidates the high-risk findings with an Eagle Eye pass, and applies a safety veto in the final synthesis. |

<!-- END:Available-Skills -->

## Installation

### Skills

Use [npx skills](https://skills.sh/) to install skills directly:

```bash
# Install all skills
npx skills add toyworks/agent-skills

# Install specific skills
npx skills add toyworks/agent-skills --skill t3-hardware-scoring

# List available skills
npx skills add toyworks/agent-skills --list
```

### Claude Code Plugin

Install via Claude Code's plugin system. The marketplace is defined in
[.claude-plugin/marketplace.json](.claude-plugin/marketplace.json) and is named
`toyworks-agent-skills`:

```bash
/plugin marketplace add ToyWorks/agent-skills
```

```bash
/plugin install t3-hardware-scoring@toyworks-agent-skills
```

> Claude Code plugins are also supported in Factory's [Droid](https://docs.factory.ai/cli/configuration/plugins#claude-code-compatibility).

### Other Installation Methods

Agent skills can also be installed by using the below commands from [Playbooks](https://playbooks.com/skills) or [Context7](https://context7.com/docs/skills):

```bash
# Playbooks
npx playbooks add skill toyworks/agent-skills

# Context7
npx ctx7 skills install /toyworks/agent-skills
```

## Adding New Skills

Create `skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`,
`description`), add any supporting `references/` and `scripts/`, then add a row
to the table above.

The `description` is what an agent matches against when deciding whether to load
the skill, so write it as a trigger, not a summary: name the user phrasings and
artifacts that should invoke it.

## Testing

Skills that ship scripts should ship tests for them. `t3-hardware-scoring` is
the reference:

```bash
skills/t3-hardware-scoring/tests/run_tests.sh
```

Its `tests/fixtures/` holds a complete worked example — a fictional product's
brand-blinded source text, the three auditor reports, and the classification
they synthesize to. It serves as both a regression test and the reference for
what correct output looks like.

CI runs each skill's test suite plus a link check on every push and pull
request. See [.github/workflows/test.yml](.github/workflows/test.yml).

## Contributing

We welcome contributions to improve existing skills or add new skills. Please
submit a pull request, and make sure `run_tests.sh` passes.

## License

MIT