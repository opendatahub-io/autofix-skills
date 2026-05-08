# Contributing to autofix-skills

Thank you for your interest in contributing to autofix-skills! This plugin provides the inner-layer orchestration for the Jira autofix pipeline.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/autofix-skills.git
   cd autofix-skills
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b my-change
   ```

## Repository Layout

```text
.claude-plugin/plugin.json   Plugin packaging metadata
skills/                      Skill directories (SKILL.md + prompts/)
scripts/                     Deterministic Python utilities called by skills
hooks/                       Claude Code event hooks
```

Read [AGENTS.md](AGENTS.md) for architecture details and conventions.

## Ways to Contribute

- **Add or improve a skill** in `skills/<skill-name>/`
- **Add or fix a script** in `scripts/`
- **Fix a bug** or improve existing functionality
- **Improve documentation**

## Development Setup

### Prerequisites

- **Python 3.10+** with [ruff](https://docs.astral.sh/ruff/) (`pip install ruff`)
- **shellcheck** (`dnf install ShellCheck` on Fedora)
- **Container runtime**: [Podman](https://podman.io/) or Docker (for claudelint)
- **Git**

### Validate Your Changes

Before submitting, always run:

```bash
make lint
```

The `lint` target runs:
- **claudelint** validates plugin structure
- **skilleval** validates skill frontmatter and content
- **ruff** checks and formats Python code
- **shellcheck** lints shell scripts

### Test Locally (Claude Code)

To test a skill with Claude Code before submitting:

1. Open `claude`
2. Run `/plugin marketplace add ./`
3. Run `/plugin` then install the local plugin
4. Test your skill
5. Remove the local marketplace when done testing

## Submitting Your Contribution

1. **Run validation** before committing:
   ```bash
   make lint
   ```
2. **Commit your changes** with a clear, descriptive commit message.
3. **Push to your fork** and open a Pull Request against `main`.
4. **Fill out the PR template**.

### Commit Messages

Write concise commit messages that explain *why* the change was made:

- `feat:` for new skills or features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `chore:` for maintenance tasks

Example: `feat: add retry logic to autofix-resolve orchestrator`

## Pull Request Process

1. **All PRs must pass CI checks**, including `make lint`.
2. **Fill out the PR template completely**.
3. **At least one maintainer review** is required before merging.
4. **Keep PRs focused**: one skill or logical change per PR.

## Style and Conventions

### Naming

- Use lowercase kebab-case for skill names: `autofix-my-skill`
- Skills in this plugin use the `autofix-` prefix to avoid collisions with ai-helpers skills

### Python

- Format with `ruff format`
- Pass `ruff check` with no errors
- Use Python 3.10+ type annotations

### Shell Scripts

- Always use `set -euo pipefail`
- Pass `shellcheck` with no warnings

### Skills

- Each skill lives in `skills/<name>/` with a `SKILL.md` and optional `prompts/` directory
- `SKILL.md` must include YAML frontmatter with at least `name` and `description`
- Prompt files in `prompts/` are self-contained agent personas

## Code of Conduct

We are committed to providing a welcoming and respectful environment for everyone. Be kind, constructive, and professional in all interactions.

## Getting Help

- **Questions?** Open a [blank issue](https://github.com/opendatahub-io/autofix-skills/issues/new) or reach out to the maintainers.
- **Extension skills** (team-specific) go in [ai-helpers](https://github.com/opendatahub-io/ai-helpers), not this repo.

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
