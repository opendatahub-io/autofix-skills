# Container runtime (podman or docker)
CONTAINER_RUNTIME ?= $(shell command -v podman 2>/dev/null || echo docker)

# claudelint image
CLAUDELINT_IMAGE = ghcr.io/stbenjam/claudelint:main

# skilleval image
SKILLEVAL_IMAGE ?= ghcr.io/opendatahub-io/ai-helpers-skilleval:latest

.PHONY: help
help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: skilleval
skilleval: ## Run skilleval linter on skills
	@echo "Running skilleval on skills..."
	@if [ -n "$${SKILLEVAL_BIN:-}" ]; then \
		node "$${SKILLEVAL_BIN}" check skills/*/ --strict; \
	else \
		"$(CONTAINER_RUNTIME)" run --rm -v "$(PWD):/workspace:Z" "$(SKILLEVAL_IMAGE)" check skills/*/ --strict; \
	fi

.PHONY: lint
lint: ## Run claudelint, skilleval, ruff, and shellcheck
	@if [ "$$(uname -m)" = "x86_64" ]; then \
		echo "Running claudelint with $(CONTAINER_RUNTIME)..."; \
		$(CONTAINER_RUNTIME) run --rm -v $(PWD):/workspace:Z $(CLAUDELINT_IMAGE) -v --strict; \
	else \
		echo "Skipping claudelint on $$(uname -m) architecture (x86_64 required)"; \
	fi
	@$(MAKE) skilleval
	@echo "Running ruff syntax checker on Python scripts..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check .; \
	else \
		echo "ruff not found, skipping Python syntax checking. Install with: pip install ruff"; \
		exit 1; \
	fi
	@echo "Running ruff format checker on Python scripts..."
	@ruff format --check --diff .
	@echo "Running shellcheck on shell scripts..."
	@if command -v shellcheck >/dev/null 2>&1; then \
		find . -name '*.sh' -type f -exec shellcheck {} + && echo "All checks passed!"; \
	else \
		echo "shellcheck not found, skipping shell script linting. Install with: dnf install ShellCheck"; \
		exit 1; \
	fi

.DEFAULT_GOAL := help
