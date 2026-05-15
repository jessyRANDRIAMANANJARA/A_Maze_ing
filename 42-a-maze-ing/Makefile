PACKAGE  = a_maze_ing
NAME     = a_maze_ing.py
SRC      = a_maze_ing.py a_maze_ing
PYTHON   = python3
PIP      = pip


all: run

install:
	$(PYTHON) -m $(PIP) install --user flake8 mypy

run:
	$(PYTHON) $(NAME)

debug:
	$(PYTHON) -m pdb $(NAME)

lint:
	$(PYTHON) -m flake8 $(SRC)
	$(PYTHON) -m mypy . \
	--warn-return-any \
	--warn-unused-ignores \
	--ignore-missing-imports \
	--disallow-untyped-defs \
	--check-untyped-defs

package:
	$(PYTHON) setup.py sdist bdist_wheel
	mv dist/*.tar.gz .
	mv dist/*.whl .

clean:
	rm -rf dist/ build/ *.egg-info
	rm -rf *.tar.gz *.whl
	find . -type d \( -name "__pycache__" -o -name ".mypy_cache" \) -exec rm -rf {} \;

.PHONY: all install run debug lint clean
