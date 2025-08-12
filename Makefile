.PHONY: help install install-dev test lint format clean run test-system

help: ## Show this help message
	@echo "Intelligent RSS Consumer - Available Commands"
	@echo "============================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install production dependencies
	poetry install --only main

install-dev: ## Install all dependencies including development tools
	poetry install

install-poetry: ## Install Poetry if not already installed
	@if ! command -v poetry &> /dev/null; then \
		echo "Installing Poetry..."; \
		curl -sSL https://install.python-poetry.org | python3 -; \
		export PATH="$$HOME/.local/bin:$$PATH"; \
	else \
		echo "Poetry is already installed: $$(poetry --version)"; \
	fi

shell: ## Activate Poetry shell
	poetry shell

test: ## Run tests
	poetry run pytest

test-system: ## Test system without LLM model
	poetry run python3 test_system.py

lint: ## Run linting checks
	poetry run flake8 src/
	poetry run mypy src/

format: ## Format code with black
	poetry run black src/ examples/ test_system.py main.py config.py

format-check: ## Check if code is properly formatted
	poetry run black --check src/ examples/ test_system.py main.py config.py

run: ## Run RSS consumer with help
	poetry run python3 main.py --help

run-example: ## Run basic usage example
	poetry run python3 examples/basic_usage.py

clean: ## Clean up generated files
	rm -rf .venv/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf coverage.xml
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

clean-db: ## Clean up database files
	rm -f *.db
	rm -f test_*.db

setup: ## Initial setup (install Poetry and dependencies)
	@$(MAKE) install-poetry
	@$(MAKE) install-dev

dev: ## Development workflow (format, lint, test)
	@$(MAKE) format
	@$(MAKE) lint
	@$(MAKE) test

build: ## Build package
	poetry build

publish: ## Publish to PyPI (requires authentication)
	poetry publish

check: ## Check package validity
	poetry check

update: ## Update dependencies
	poetry update

outdated: ## Show outdated dependencies
	poetry show --outdated

add: ## Add a new dependency (usage: make add DEP=package_name)
	@if [ -z "$(DEP)" ]; then \
		echo "Usage: make add DEP=package_name"; \
		exit 1; \
	fi
	poetry add $(DEP)

add-dev: ## Add a new development dependency (usage: make add-dev DEP=package_name)
	@if [ -z "$(DEP)" ]; then \
		echo "Usage: make add-dev DEP=package_name"; \
		exit 1; \
	fi
	poetry add --group dev $(DEP)

remove: ## Remove a dependency (usage: make remove DEP=package_name)
	@if [ -z "$(DEP)" ]; then \
		echo "Usage: make remove DEP=package_name"; \
		exit 1; \
	fi
	poetry remove $(DEP)

# RSS Consumer specific commands
rss-help: ## Show RSS consumer help
	poetry run python3 main.py --help

rss-stats: ## Show database statistics
	poetry run python3 main.py --stats

rss-results: ## Show relevant results
	poetry run python3 main.py --results

rss-run: ## Run RSS consumption (usage: make rss-run QUERY="your query" MODEL="path/to/model")
	@if [ -z "$(QUERY)" ] || [ -z "$(MODEL)" ]; then \
		echo "Usage: make rss-run QUERY='your query' MODEL='path/to/model'"; \
		echo "Example: make rss-run QUERY='artificial intelligence' MODEL='models/llama-2-7b.gguf'"; \
		exit 1; \
	fi
	poetry run python3 main.py --query "$(QUERY)" --model "$(MODEL)"

rss-scheduled: ## Run scheduled RSS consumption (usage: make rss-scheduled QUERY="your query" MODEL="path/to/model" INTERVAL=60)
	@if [ -z "$(QUERY)" ] || [ -z "$(MODEL)" ]; then \
		echo "Usage: make rss-scheduled QUERY='your query' MODEL='path/to/model' [INTERVAL=60]"; \
		echo "Example: make rss-scheduled QUERY='machine learning' MODEL='models/llama-2-7b.gguf' INTERVAL=30"; \
		exit 1; \
	fi
	poetry run python3 main.py --query "$(QUERY)" --model "$(MODEL)" --scheduled --interval $(or $(INTERVAL),60) 