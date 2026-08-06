PYTHON := $(shell command -v python3.11 2>/dev/null)
UV := $(shell command -v uv 2>/dev/null)
ARGS := $(wordlist 2, 999, $(MAKECMDGOALS))

install:
	@if [ -z "$(UV)" ]; then \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
		export PATH=$$PATH:$$HOME/.local/bin/uv; \
	fi
	@if [ -z "$(PYTHON)" ]; then \
		uv python install 3.11; \
	fi
	@if [ ! -d "./.venv" ]; then \
		uv venv; \
	fi
	uv pip install numpy termcolor readchar flake8 mypy pydocstyle

run:
	@if [ ! -d .venv ]; then \
		echo "Run make install please"; \
		exit 1; \
	fi
	uv run python a_maze_ing.py $(ARGS)

debug:
	@if [ ! -d .venv ]; then \
		echo "Run make install please"; \
		exit 1; \
	fi
	uv run python -m pdb a_maze_ing.py $(ARGS)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -name .pytest_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "output.txt" -delete

lint:
	uv run flake8 **/*.py
	uv run flake8 --select=D **/*.py
	uv run flake8 --max-line-length=79 --select=D .
	uv run mypy . --warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

.PHONY: install run debug clean lint

%:
	@: