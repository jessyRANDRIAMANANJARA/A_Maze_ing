Things that need to be included:
- [+] Typehints -> `typing`
- [+] Docstrings (Classes, Functions, Methods)
- [+] Static type checking `mypy`
- [+] `.gitignore`

Makefile
- [+] dependencies installation using: `pip`, `uv`
- [+] run `python3 main.py` 
- [+] debug `pdb`
- [+] clean: remove `__pycache__`, `.mypy_cache`
- [+] lint: testing with `flake8` and `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs`
- [+] lint-strict: optional -> `flake8 .` and `mypy . --strict`

Additional Guidelines
- [+] Testing with `pytest` or `unittest` for unit tests
- [+] Using a virtual environment: `venv`

Mandatory part
- [+] config.txt with a default config (KEY=VALUE)
- [+] seed must randomly generated, the generator must generate the same maze with a specific seed
- [+] Walls representation: (North, Est, South, West)
- [+] Entrace and Exit must be on the bounds
- [+] No isolated cells
- [+] Coridors can't be wide open 3x3, it can be 2x3 or 3x2
- [+] Draw 42 at the center using closed cells
- [+] if there is not space to draw 42, print an error msg
- [+] Output File Format (Example: 0011 south:open, west:open, north: closed, east:closed | Cells row by row)
    - 0 (LSB) North
    - 1 East
    - 2 South
    - 3 West
- [+] After an empty line
    - Line 1: represent the entrace coordinates
    - Line 2: represent the exit coordinates
    - Line 3: NESW
- [+] Maze representation (MiniLibX) -> Switched to ASCII


# REMAINDER:
- [+] we should add the exit and entry position in the init of the maze class

## Bonus
- [+] Aditional Algo
- [+] Animation
- [+] Color
- [+] Output to file
- [+] Show/Hide solution
- [+] Change walls style
- [+] Change solution style
- [+] Config validation
- [+] Min,Max Entry & Exit
- [+] Entry, Exit coordinates validation
- [+] Makefile
- [+] Docstrings
- [+] Type hints
- [+] Code cleaning
- [+] Flake
- [+] Testing
- [+] README
- [+] Package: mazegen.tar.gz
