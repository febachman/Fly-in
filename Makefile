PYTHON = python3

MAIN = src.main
CONFIG = config.txt
OUTPUT_TEST = simulation_output.txt

SRC = src
TESTS = tests

VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
VENV_PIP = $(VENV_PYTHON) -m pip

MYPY_FLAGS = \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

PIP_INDEX ?= https://pypi.org/simple


all: lint test run


$(VENV_PYTHON):
	$(PYTHON) -m venv $(VENV)


install: $(VENV_PYTHON)
	$(VENV_PIP) install --index-url $(PIP_INDEX) --upgrade pip
	$(VENV_PIP) install --index-url $(PIP_INDEX) \
		flake8 mypy pytest
	@echo "Development environment ready! ✅"


run: install
	$(VENV_PYTHON) -m $(MAIN) $(CONFIG)


debug: install
	$(VENV_PYTHON) -m pdb -m $(MAIN) $(CONFIG)


test: install
	PYTHONPATH=$(SRC) $(VENV_PYTHON) -m pytest
	@echo "Tests passed! ✅"


lint: install
	$(VENV_PYTHON) -m flake8 $(SRC) $(TESTS)
	$(VENV_PYTHON) -m mypy $(SRC) $(TESTS) $(MYPY_FLAGS)
	@echo "Lint and type checks passed! ✅"


lint-strict: install
	$(VENV_PYTHON) -m flake8 $(SRC) $(TESTS)
	$(VENV_PYTHON) -m mypy $(SRC) $(TESTS) --strict
	@echo "Strict type check passed! ✅"


clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache
	@echo "Cache files cleaned! ✅"


fclean: clean
	rm -rf $(VENV)
	rm -f $(OUTPUT_TEST)
	@echo "Full clean completed! ✅"


re: fclean install all


.PHONY: all install run debug test lint lint-strict \
	clean fclean re