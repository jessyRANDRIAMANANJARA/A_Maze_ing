*This project has been created as part of the 42 curriculum by tusandri, hrandri2.*

# A-MAZE-Ing

A terminal-based, procedurally generated maze engine written in Python: it
builds a maze from a config file, solves it, renders it live in colored
ASCII/Unicode art, and writes the result to disk in a compact custom format.

---

## Table of contents

- [Description](#description)
- [Instructions](#instructions)
- [Interactions — how the maze behaves in the terminal](#interactions--how-the-maze-behaves-in-the-terminal)
- [Configuration file](#configuration-file)
- [Maze generation algorithm](#maze-generation-algorithm)
- [Why ASCII/Unicode instead of a graphical (MLX-style) display](#why-asciiunicode-instead-of-a-graphical-mlx-style-display)
- [Tools and libraries used](#tools-and-libraries-used)
- [Reusable code — the `mazegen` package](#reusable-code--the-mazegen-package)
- [Team and project management](#team-and-project-management)
- [Project planning](#project-planning)
- [Resources](#resources)

---

## Description

**A-MAZE-Ing** is a maze generator and solver. Given a small text
configuration file describing the size of the maze, its entry/exit points,
and a few generation options, the program:

1. Builds a grid of cells and carves passages between them using one of two
   generation algorithms (Depth-First Search or Wilson's algorithm), so that
   the maze is fully connected from any cell to any other.
2. Optionally "breaks" a few extra walls to turn the maze from a *perfect*
   maze (exactly one path between any two cells, no loops) into an
   *imperfect* one (a few loops/shortcuts), which is more interesting to
   explore.
3. Solves the maze with a Breadth-First Search pathfinder to find the
   shortest path between the entry and the exit.
4. Renders everything live in the terminal as colored Unicode box-drawing
   characters, with an interactive menu to regenerate mazes, toggle the
   solution path, change colors, and switch the decorative "42" pattern
   style.
5. Writes a compact, machine-readable snapshot of the maze (walls, entry,
   exit, solution path) to an output file.

The goal of the project is to practice designing and implementing several
classic maze-generation algorithms, work with a non-trivial CLI/TUI
(terminal UI) written entirely in Python, and structure the code so that the
core maze-generation logic (`mazegen`) is fully decoupled from the
rendering/config layer and reusable as a standalone, installable Python
package.

## Instructions

### Requirements

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) (the `Makefile` installs it
  automatically if it's missing)
- A terminal that supports ANSI colors and Unicode box-drawing characters
  for the best experience (any modern terminal emulator works)

### Installation

```sh
make install
```

This creates a `.venv` virtual environment (via `uv`) and installs all
dependencies: `numpy`, `termcolor`, `readchar`, plus the dev tools `flake8`,
`mypy`, and `pydocstyle`.

### Running

```sh
make run config.txt
```

(`config.txt` can be replaced by the path to any valid configuration file,
see below.) This is equivalent to:

```sh
uv run python a_maze_ing.py config.txt
```

### Other Makefile targets

| Target        | What it does                                                        |
|---------------|----------------------------------------------------------------------|
| `make install`| Sets up the virtual environment and installs all dependencies        |
| `make run`    | Runs the program (`ARGS` after `run` is passed as the config path)   |
| `make debug`  | Runs the program under `pdb`                                        |
| `make lint`   | Runs `flake8`, `flake8 --select=D` (docstrings) and `mypy`           |
| `make clean`  | Removes caches, build artifacts and any generated `output.txt`       |

## Interactions — how the maze behaves in the terminal

Once launched, the program clears the screen and shows a small banner and a
key-driven menu. All interaction happens through single keypresses, read
instantly (no need to press Enter) via the `readchar` library:

| Key     | Effect                                                                |
|---------|------------------------------------------------------------------------|
| `SPACE` | Generate a brand-new maze with the configured size/algorithm          |
| `P`     | Toggle whether the solution path is shown                             |
| `C`     | Open the color menu (wall color, "42" pattern color, path color, background) |
| `T`     | Toggle between the two variants of the decorative "42" pattern        |
| `Q`     | Quit                                                                    |

When a maze is generated with the solution path visible, it is **animated**:
the path is revealed step by step from the entry to the exit (with a short
delay between each step), before the final view (with the full menu) is
shown. The maze itself is drawn with Unicode box-drawing characters
(`║ ═ ╔ ╗ ╚ ╝ ...`) so that walls form continuous lines; the entry and exit
cells are marked with emoji (🧍 for the entry, 🎖️ for the exit), and every
render is colorized through `termcolor`.

Every time a maze is generated, a snapshot is also written to the
`output_file` configured in `config.txt` (see below) — this happens
automatically, no extra key press is required.

## Configuration file

The program takes exactly one argument: the path to a configuration file
(`config.txt` by default). The file is a simple `key = value` list, one
setting per line. Lines starting with `#` are comments and are ignored;
inline comments are also supported (`entry = 8, 8  # top-right corner`),
as long as the `#` is separated from the value by at least one space
(a `#` glued directly to a value is treated as part of that value, not a
comment).

```txt
# Mandatory Configuration Keys
WIDTH       = 13
height      = 9
entry       = 0, 0
exit        = 8, 8
perfect     = true
output_file = output.txt

# optional keys
# seed = 42
# Options are 'dfs' for Depth First Search or 'wilson' for Wilson's algorithm.
# The default algorithm is 'dfs'.
algorithm   = dfs
```

Keys are case-insensitive. If **any** mandatory key is missing, the program
prints a single, unified error message listing exactly which ones are
missing, and exits with status `1` — you don't have to fix and re-run the
program six times to discover every missing key at once. When a value is
invalid, the error always describes the **first problem found while
checking the keys in the order above** (`width` → `height` → `entry` →
`exit` → `perfect` → `output_file`), regardless of the order in which the
lines actually appear in the file.

### Mandatory keys

| Key           | Description                                                                                     |
|---------------|---------------------------------------------------------------------------------------------------|
| `WIDTH`       | Number of columns of the maze (x-axis). Must be an integer strictly between 5 and 60.             |
| `HEIGHT`      | Number of rows of the maze (y-axis). Must be an integer strictly between 5 and 60.                 |
| `ENTRY`       | Starting cell of the maze, as `x,y` (0-indexed). Must be inside the grid (`0 <= x < WIDTH`, `0 <= y < HEIGHT`). |
| `EXIT`        | Ending cell of the maze, as `x,y` (0-indexed), same constraints as `ENTRY`. It must be different from `ENTRY`. |
| `PERFECT`     | `true` or `false`. `true` keeps the maze *perfect* (a unique path between any two cells, no loops). `false` randomly breaks a few extra walls, adding loops/shortcuts (an *imperfect*/braided maze). |
| `OUTPUT_FILE` | Path of the file the program writes the generated maze, entry/exit coordinates and solution path to, every time a maze is generated. |

### Optional keys

| Key         | Description                                                                                  |
|-------------|-------------------------------------------------------------------------------------------------|
| `SEED`      | Signed 32-bit integer used to seed the random number generator, for reproducible mazes. If omitted, empty, or out of range, a random seed is used instead. |
| `ALGORITHM` | `dfs` (default) or `wilson`, selects the generation algorithm (see below).                      |

## Maze generation algorithm

Two algorithms are implemented, selectable via `ALGORITHM` in the config
file:

- **`dfs` (Depth-First Search / "recursive backtracker") — default.**
  Starting from a random cell, the algorithm repeatedly walks to a random
  unvisited neighbor, carving a passage as it goes, and backtracks (pops the
  move stack) whenever it reaches a dead end, until every cell has been
  visited.
- **`wilson` (Wilson's algorithm, loop-erased random walk).** Starting from
  a maze made of a single random cell, the algorithm repeatedly performs a
  random walk from an unvisited cell until it hits the existing maze,
  erasing any loop the walk makes along the way, then "stamps" that
  loop-erased path onto the maze. This is repeated until every cell belongs
  to the maze.

Once a maze has been generated (with either algorithm), `BFS (Breadth-First Search)` — an algorithm that explores the maze level by level, guaranteeing the shortest path is found — is used as the pathfinder to compute the route from ENTRY to EXIT, this is what gets animated in the terminal and written to output_file.

### Why this algorithm?

`dfs` was chosen as the **default** because it is simple to implement
correctly, very fast (`O(V)`, one pass, no loop-erasure bookkeeping), and it
produces mazes with long, winding corridors and comparatively few short
dead ends — visually satisfying to explore and to watch being generated in
the terminal.

`wilson` was added as a **second option** specifically because DFS is
statistically biased: it tends to favor long corridors over frequent
branching. Wilson's algorithm generates a *uniform spanning tree* — every
possible perfect maze on the grid is equally likely to be produced — which
gives a structurally different, more "branchy" and less predictable maze.
It is more expensive (random walks can revisit cells many times before
reaching the maze, especially early on), which is exactly the trade-off we
wanted to illustrate: DFS for speed and long corridors, Wilson's for
statistical fairness and topology diversity. Having both lets the user pick
based on what they want to see or use for a given maze size.

Both algorithms share the same base class (`MazeGenerator`), the same cell
representation (`MazeCell`), the same optional decorative "42" pattern
placement, and the same `make_imperfect()` post-processing step — only the
core "how do we carve the maze" logic differs between the two subclasses.

## Why ASCII/Unicode instead of a graphical (MLX-style) display

The project intentionally renders the maze as text (Unicode box-drawing
characters + ANSI colors) in the terminal rather than through a graphical
window (e.g. an MLX/MLX42-style pixel canvas), for several reasons:

- **No native graphics dependency.** MLX/MLX42 is a C library; this project
  is written entirely in Python, so pulling in a C graphics library and
  writing/maintaining Python bindings for it would add a large amount of
  complexity (and a hard dependency on a windowing system / OpenGL context)
  for very little functional benefit here.
- **Portability and grading convenience.** A terminal renderer runs
  identically over SSH, inside a headless CI/grading environment, in a
  Docker container, or on any OS with any terminal emulator — no display
  server, no window manager, no risk of "it works on my machine but not on
  the evaluator's".
- **Faster iteration.** Redrawing a grid of characters is essentially free
  compared to managing a pixel buffer, event loop, and window lifecycle;
  this let us focus development time on the generation algorithms and the
  interactive controls (live regeneration, color menu, animated path)
  instead of on graphics plumbing.
- **The maze is fundamentally a grid**, so a character grid is already a
  natural, lossless representation of it — walls become box-drawing glyphs,
  cells become single characters, and color is used purely as an extra
  layer of information (walls vs. path vs. "42" pattern vs. entry/exit)
  rather than something the display *needs* to convey the maze's structure.

## Tools and libraries used

| Tool / library | Role in the project |
|---|---|
| **numpy** (`numpy.random`) | Provides the Mersenne Twister PRNG (`Generator(MT19937(seed=...))`) used to generate mazes deterministically from a `SEED`, and to make random choices during generation (`rng.choice`, `rng.random`). |
| **termcolor** | Colorizes the terminal output (walls, "42" pattern, solution path, entry/exit markers, background) without manually handling raw ANSI escape codes. |
| **readchar** | Reads single keypresses from the terminal instantly (no `Enter` needed), used to drive the interactive menu (`SPACE`/`P`/`C`/`T`/`Q`). |
| **mypy** | Static type checker; the whole codebase is fully type-hinted (`dict[str, str | int | bool]`, `Callable[...]`, etc.) and checked with `--warn-return-any --disallow-untyped-defs --check-untyped-defs` to catch type errors before runtime. |
| **flake8** (+ `pydocstyle` via `--select=D`) | Linter enforcing PEP 8 style and docstring conventions (`make lint`), keeping the codebase consistent across contributors. |
| **uv** | Fast Python package/venv manager used by the `Makefile` to install the correct Python version, create the virtual environment, and install dependencies reproducibly. |
| **setuptools / wheel** (via `pyproject.toml`) | Build backend used to package the `mazegen` module into a distributable wheel (`.whl`) and source distribution (`.tar.gz`) — see below. |

## Reusable code — the `mazegen` package

The maze-generation core (`mazegen/`) is deliberately isolated from the
config parsing (`config_reader.py`) and rendering (`render.py`) layers: it
only depends on `numpy`, has its own `pyproject.toml`, and exposes a small,
clean public API (`MazeCell`, `MazeGenerator`, `DFSearch`, `WilsonsAlgorithm`,
`BFS`). This means it can be built and reused as a standalone Python
package in any other project, without pulling in the terminal UI code at
all.

### Building the distributable files (`.whl` and `.tar.gz`)

From the `mazegen/` directory:

```sh
cd mazegen
python -m pip install --upgrade build
python -m build
```

This produces, in a new `dist/` folder:

```
dist/
├── mazegen-1.0.0-py3-none-any.whl
└── mazegen-1.0.0.tar.gz
```

- The **`.whl`** (wheel) is the pre-built, ready-to-install format — pip
  installs it directly, no build step needed on the target machine.
- The **`.tar.gz`** is the source distribution — useful if the target
  environment needs to (re)build the package itself, or as an archival/
  source-inspection format.

### Installing it elsewhere

```sh
pip install mazegen-1.0.0-py3-none-any.whl
# or, from source:
pip install mazegen-1.0.0.tar.gz
```

`numpy>=2.4.1` will be installed automatically as a dependency (declared in
`mazegen/pyproject.toml`).

mazegen on its own is display-agnostic — it only generates and solves mazes, it doesn't print or animate anything. If you also want to reuse the animated, colored terminal rendering and interactive controls (render.py/a_maze_ing.py), you additionally need termcolor (colored output) and readchar (instant single-keypress input), since those two libraries are what the animation and the interactive menu are built on:

```sh
pip install termcolor readchar
```

### Example usage

```python
from mazegen import DFSearch, BFS

# Generate a 16x16 perfect maze, reproducible via the seed
gen = DFSearch(width=16, height=16, seed=42)
maze = gen.generate_maze()          # list[list[MazeCell]]

# Solve it from the top-left to the bottom-right corner
solver = BFS()
path = solver.pathfind(maze, start=(0, 0), end=(15, 15))
directions = solver.path_to_directions(path)   # e.g. ["E", "E", "S", ...]
```

- `gen.generate_maze()` returns a grid of `MazeCell` objects, each exposing
  `north`/`south`/`east`/`west` booleans (whether a passage exists in that
  direction) and its `coordinates`.
- `BFS().pathfind(maze, start, end)` returns the shortest path as a list of
  `(row, col)` coordinates, or `None` if the maze has no path between the
  two points (should not happen on a maze produced by `generate_maze()`,
  but can happen with a hand-built/modified maze).
- Swap `DFSearch` for `WilsonsAlgorithm` to use the other generation
  algorithm — both share the exact same constructor signature and public
  methods, so no other code needs to change.

## Team and project management

*(This section reflects a two-person team; roles below are a starting
template — adjust the specifics to match how the work was actually split.)*

### Roles

- **tusandri** — focused on the maze-generation core (`mazegen/`): the
  `MazeCell`/`MazeGenerator` data model, the `DFSearch` and `WilsonsAlgorithm`
  implementations, the "42" pattern placement, the `make_imperfect()`
  post-processing step, and the `BFS` pathfinder.
- **hrandri2** — focused on the application layer: `config_reader.py`
  (parsing/validating `config.txt`), `render.py` (the terminal UI, colored
  rendering, interactive controls), `output_file_generation.py`, and
  packaging/tooling (`Makefile`, `mazegen`'s `pyproject.toml`, lint/type
  setup).

Both contributed to integration, debugging, and code review across the two
areas.

### What worked well

- Splitting the project along a clean boundary (pure generation logic vs.
  I/O and terminal rendering) we both worked in parallel without
  stepping on each other's files most of the time.
- Adding full type hints and running `mypy`/`flake8` continuously caught a
  number of small bugs (wrong tuple order, `Optional` mismatches) early,
  before we turned into confusing runtime behavior.
- Packaging `mazegen` as its own installable module early on forced a clean
  public API, which made it easy to plug in a second algorithm
  (`WilsonsAlgorithm`) later without touching the rendering code at all.

### What could be improved

- A width/height axis mismatch between the maze-generation base class and
  its subclasses went unnoticed for a while and was worked around with a
  compensating swap elsewhere in the code instead of being fixed at the
  source — better integration testing across the two areas from the start
  would have caught this sooner.
- Config validation error messages were originally reported in whatever
  order the file happened to list its keys, and some mandatory-key checks
  exited the program differently (via silent `sys.exit` vs. a raised
  exception caught upstream); this was only unified into one consistent,
  ordered error-reporting path after the fact — it should have been
  designed that way from the beginning.
- No automated test suite exists yet; testing was mostly manual
  (`config.txt` variations, the interactive terminal, `make lint`). Adding
  unit tests for `config_reader.py` and the two generation algorithms would
  make future changes safer.

### Specific tools used

See the [Tools and libraries](#tools-and-libraries-used) table above
(`numpy`, `termcolor`, `readchar`, `mypy`, `flake8`/`pydocstyle`, `uv`,
`setuptools`/`wheel`).

## Project planning

*(Anticipated plan vs. actual outcome)*

1. **Week 1 — Core generation.** Implement `MazeCell`/`MazeGenerator`,
   `DFSearch`, and a basic ASCII-only renderer to validate that mazes were
   generated correctly.
2. **Week 2 — Solving & config.** Add the `BFS` pathfinder, `config_reader.py`
   and the `config.txt` format, `output_file_generation.py`.
3. **Week 3 — Polish.** Add `WilsonsAlgorithm`, the imperfect-maze option,
   colored/Unicode rendering with `termcolor`, the interactive
   `readchar`-driven menu, and the "42" pattern.
4. **Week 4 — Packaging & hardening.** Package `mazegen` as an installable
   module, add `mypy`/`flake8` checks and the `Makefile`, fix the
   width/height and config-validation issues found during review, and
   write documentation.

Overall the plan held up reasonably well; the main deviation was that
config-file validation and error-message ordering needed a second pass
near the end of the project once real-world "malformed config" testing
surfaced inconsistencies that weren't obvious from the happy path alone.

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm) — overview of DFS/recursive-backtracker, Wilson's algorithm, and other classic maze-generation approaches.
- [Jamis Buck — "Maze Generation: Algorithm Recap"](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap) — visual walkthroughs and comparisons of multiple maze algorithms (DFS, Wilson's, Kruskal's, Prim's...).
- [Wilson's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Loop-erased_random_walk#Wilson's_algorithm) — loop-erased random walk and uniform spanning trees.
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search) — reference for the pathfinding algorithm used in `BFS`.
- [NumPy `Generator`/`MT19937` documentation](https://numpy.org/doc/stable/reference/random/generator.html) — the PRNG API used for seeded, reproducible generation.
- [`termcolor` documentation](https://pypi.org/project/termcolor/) and [`readchar` documentation](https://pypi.org/project/readchar/) — the terminal-color and single-keypress-input libraries used for the interactive renderer.
- [Python Packaging User Guide — Building and publishing](https://packaging.python.org/en/latest/tutorials/packaging-projects/) — reference for the `pyproject.toml` setup and building `mazegen`'s wheel/sdist.

### Use of AI

An AI assistant (Claude, Anthropic) was used during this project for:

- **Debugging**, specifically identifying the root cause of the
  width/height axis mismatch between `MazeGenerator` and its subclasses
  (`DFSearch`/`WilsonsAlgorithm`), and fixing it at the source instead of
  through the compensating workaround that existed in `a_maze_ing.py`.
- **Refactoring `config_reader.py`**: separating raw parsing from value
  validation so that (1) missing mandatory keys are reported in a single,
  unified error message instead of several different exit points, and
  (2) validation errors are always reported in a fixed, predictable order
  (matching the order keys are documented in `config.txt`) regardless of
  the physical order of lines in the actual file being read; and adding
  support for inline `#` comments in config values.
- **Drafting and structuring this `README.md`**, based on the project's requirements and also improve the `Makefile`and `docstrings`.
