#!/usr/bin/env bash
set -euo pipefail

# Pre-packages repo context into .triage-context/repo-profile.json
# so the triage agent can skip sequential file-by-file exploration.

OUTPUT_DIR=".triage-context"
OUTPUT_FILE="${OUTPUT_DIR}/repo-profile.json"
mkdir -p "${OUTPUT_DIR}"

# --- Language / framework detection ---
language="unknown"
framework=""
if [ -f "go.mod" ]; then
  language="go"
  framework=$(head -1 go.mod | sed 's/^module //')
elif [ -f "pyproject.toml" ]; then
  language="python"
elif [ -f "setup.py" ] || [ -f "setup.cfg" ]; then
  language="python"
elif [ -f "package.json" ]; then
  language="node"
  framework=$(python3 -c "
import json, sys
try:
    p = json.load(open('package.json'))
    deps = list(p.get('dependencies', {}).keys())
    for fw in ['react', 'vue', 'angular', 'next', 'express', 'fastify']:
        if fw in deps:
            print(fw); sys.exit(0)
except Exception:
    pass
" 2>/dev/null || true)
elif [ -f "Cargo.toml" ]; then
  language="rust"
fi

# --- Agent docs ---
has_agents_md=false
has_claude_md=false
has_contributing=false
has_readme=false
[ -f "AGENTS.md" ] && has_agents_md=true
[ -f "CLAUDE.md" ] && has_claude_md=true
[ -f "CONTRIBUTING.md" ] && has_contributing=true
[ -f "README.md" ] && has_readme=true

# Capture the content of the best orientation doc (priority order)
orientation_content=""
orientation_source=""
for doc in AGENTS.md CLAUDE.md CONTRIBUTING.md README.md; do
  if [ -f "$doc" ]; then
    orientation_content=$(head -200 "$doc")
    orientation_source="$doc"
    break
  fi
done

# --- Build / test infrastructure ---
makefile_targets=""
if [ -f "Makefile" ] || [ -f "makefile" ] || [ -f "GNUmakefile" ]; then
  makefile_targets=$(grep -Eh '^[[:alnum:]_.%/@+-]+:' Makefile makefile GNUmakefile 2>/dev/null \
    | sed 's/:.*//' | sort -u | tr '\n' ',' | sed 's/,$//')
fi

has_ci=false
ci_system=""
if [ -d ".github/workflows" ]; then
  has_ci=true
  ci_system="github-actions"
elif [ -f ".gitlab-ci.yml" ]; then
  has_ci=true
  ci_system="gitlab-ci"
elif [ -f "Jenkinsfile" ]; then
  has_ci=true
  ci_system="jenkins"
elif [ -f ".tekton" ] || [ -d ".tekton" ]; then
  has_ci=true
  ci_system="tekton"
fi

# --- Lint config ---
has_lint=false
lint_tool=""
for lf in .golangci.yml .golangci.yaml ruff.toml .flake8 .eslintrc.js .eslintrc.json .eslintrc.yml .eslintrc.yaml eslint.config.js eslint.config.mjs biome.json; do
  if [ -f "$lf" ]; then
    has_lint=true
    lint_tool="$lf"
    break
  fi
done
if [ "$has_lint" = "false" ] && [ -f "pyproject.toml" ] && grep -qE '\[tool\.(ruff|pylint|flake8|mypy|black)\]' pyproject.toml 2>/dev/null; then
  has_lint=true
  lint_tool="pyproject.toml"
fi

# --- Test infrastructure ---
has_tests=false
test_dirs=""
for td in test tests __tests__ spec test_* *_test; do
  if [ -d "$td" ]; then
    has_tests=true
    test_dirs="${test_dirs:+$test_dirs,}$td"
  fi
done
# Also check for inline test files
if [ "$language" = "go" ]; then
  if find . -maxdepth 3 -name '*_test.go' -print -quit 2>/dev/null | grep -q .; then
    has_tests=true
  fi
elif [ "$language" = "python" ]; then
  if find . -maxdepth 3 -name 'test_*.py' -print -quit 2>/dev/null | grep -q .; then
    has_tests=true
  fi
fi

# Check for test config files
test_config=""
for tc in pytest.ini tox.ini setup.cfg jest.config.js jest.config.ts vitest.config.ts vitest.config.js; do
  if [ -f "$tc" ]; then
    test_config="${test_config:+$test_config,}$tc"
  fi
done

# --- Top-level directory listing ---
top_dirs=$(find . -maxdepth 1 -type d ! -name '.' ! -name '.*' | sed 's|^\./||' | sort | tr '\n' ',' | sed 's/,$//')

# --- Write JSON output via jq (avoids shell-variable injection into python3 -c) ---
jq -n \
  --arg language "$language" \
  --arg framework "$framework" \
  --argjson has_agents_md "$has_agents_md" \
  --argjson has_claude_md "$has_claude_md" \
  --argjson has_contributing "$has_contributing" \
  --argjson has_readme "$has_readme" \
  --arg orientation_source "$orientation_source" \
  --arg makefile_targets "$makefile_targets" \
  --argjson has_ci "$has_ci" \
  --arg ci_system "$ci_system" \
  --argjson has_lint "$has_lint" \
  --arg lint_tool "$lint_tool" \
  --argjson has_tests "$has_tests" \
  --arg test_dirs "$test_dirs" \
  --arg test_config "$test_config" \
  --arg top_dirs "$top_dirs" \
  '{
    language: $language,
    framework: $framework,
    agent_docs: {
      has_agents_md: $has_agents_md,
      has_claude_md: $has_claude_md,
      has_contributing: $has_contributing,
      has_readme: $has_readme,
      orientation_source: $orientation_source
    },
    build_infra: {
      makefile_targets: ($makefile_targets | if . == "" then [] else split(",") end),
      has_ci: $has_ci,
      ci_system: $ci_system
    },
    lint: {
      has_lint_config: $has_lint,
      lint_tool: $lint_tool
    },
    tests: {
      has_tests: $has_tests,
      test_dirs: ($test_dirs | if . == "" then [] else split(",") end),
      test_configs: ($test_config | if . == "" then [] else split(",") end)
    },
    top_level_dirs: ($top_dirs | if . == "" then [] else split(",") end)
  }' > "${OUTPUT_FILE}"

# --- Append orientation doc content if found ---
if [ -n "${orientation_source}" ]; then
  ORIENT_FILE="${OUTPUT_DIR}/orientation.md"
  printf '%s\n' "${orientation_content}" > "${ORIENT_FILE}"
fi

echo "Repo profile written to ${OUTPUT_FILE}"
