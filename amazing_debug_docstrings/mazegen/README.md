*This project has been created as part of the 42 curriculum by tusandri, hrandri2.*

# mazegen

`mazegen` is the standalone maze-generation and pathfinding library that
powers [A-MAZE-Ing](../README.md). It is a small, dependency-light Python
package (only `numpy`) with **no terminal/UI code at all**, so it can be
built, installed, and reused independently in any other project.

## Table of contents

- [Description](#description)
- [Installation](#installation)
- [Usage](#usage)
- [API reference](#api-reference)
- [Building the package yourself](#building-the-package-yourself)
- [Project structure](#project-structure)
- [Resources](#resources)

## Description

`mazegen` provides everything needed to generate and solve a rectangular
maze, without caring about how it's displayed:

- A simple `MazeCell` data model (walls + coordinates + optional decorative
  marker).
- Two maze-generation algorithms sharing a common base class:
  - **`DFSearch`** — Depth-First Search / recursive backtracker.
  - **`WilsonsAlgorithm`** — loop-erased random walk, producing a uniform
    spanning tree (no bias towards long corridors).
- An optional post-processing step, `make_imperfect()`, that turns a
  *perfect* maze (exactly one path between any two cells) into an
  *imperfect* one by randomly opening a few extra walls (loops/shortcuts).
- Automatic placement of a decorative "42" pattern inside large-enough
  mazes (two styles available: a classic "42" glyph, or a "TJ" variant).
- A **`BFS`** pathfinder that finds the shortest path between two cells and
  can convert it into a list of cardinal directions (`N`/`S`/`E`/`W`).
- Deterministic generation: every generator accepts an optional `seed` so
  the exact same maze can be reproduced across runs.

## Installation

### From the pre-built wheel

```sh
pip install mazegen-1.0.0-py3-none-any.whl
```

### From the source distribution

```sh
pip install mazegen-1.0.0.tar.gz
```

### From source, in editable/development mode

From inside the `mazegen/` directory:

```sh
pip install -e .
```

In every case, `numpy>=2.4.1` is installed automatically as a declared
dependency — no extra step needed. *`mazegen`* itself has no other dependency: it only generates and solves mazes, it never prints or animates anything.

Optional: for the animated terminal display

termcolor and readchar are not dependencies of mazegen — but if you're pairing this library with the animated, colored terminal renderer and interactive controls from the parent A-MAZE-Ing project (render.py/a_maze_ing.py), install them too: the live step-by-step path animation and the single-keypress menu (SPACE/P/C/ T/Q) are built directly on top of these two libraries.

```sh
pip install termcolor readchar
```

## Usage

### Generate and solve a maze

```python
from mazegen import DFSearch, BFS

# 16x16 perfect maze, reproducible thanks to the seed
gen = DFSearch(width=16, height=16, seed=42)
maze = gen.generate_maze()          # list[list[MazeCell]]

solver = BFS()
path = solver.pathfind(maze, start=(0, 0), end=(15, 15))
directions = solver.path_to_directions(path)   # e.g. ["E", "E", "S", ...]

print(f"Solution length: {len(path)} cells")
print("Directions:", "".join(directions))
```

### Switching algorithm

`DFSearch` and `WilsonsAlgorithm` share the exact same constructor and
public methods, so switching is a one-line change:

```python
from mazegen import WilsonsAlgorithm

gen = WilsonsAlgorithm(width=16, height=16, seed=42)
maze = gen.generate_maze()
```

### Making the maze imperfect (adding loops)

```python
gen = DFSearch(width=20, height=20, seed=7)
maze = gen.generate_maze()
gen.make_imperfect()   # randomly opens a few extra walls in-place
```

### Enabling the "42" pattern

Mazes of at least 14x10 automatically get a decorative "42" pattern carved
into their center (a set of cells reserved and marked via
`cell.fourty_two_pattern`); mazes smaller than that simply skip it (a
message is printed to say so). Pass `use_tj_pattern=True` for the
alternative "TJ" glyph instead of the default "42":

```python
gen = DFSearch(width=20, height=15, seed=1, use_tj_pattern=True)
maze = gen.generate_maze()
print(gen.pattern_coordinates)  # list[tuple[int, int]] of the pattern cells
```

### Inspecting a cell

```python
cell = maze[0][0]
print(cell.north, cell.south, cell.east, cell.west)  # open passages
print(cell.fourty_two_pattern)                        # part of the "42" pattern?
print(cell.coordinates)                               # (row, col)
```

### Writing the maze to disk

`mazegen` itself does not write files — that responsibility lives in the
parent A-MAZE-Ing project (`output_file_generation.py`), which is a thin,
optional consumer of `mazegen`'s output:

```python
from output_file_generation import generate_output_file

generate_output_file(
    maze=maze,
    path=directions,
    start=(0, 0),
    end=(15, 15),
    filename="output.txt",
)
```

## API reference

### `MazeCell` (dataclass)

| Field                | Type                | Description                                  |
|-----------------------|---------------------|-----------------------------------------------|
| `north`, `south`, `east`, `west` | `bool`   | Whether a passage exists in that direction    |
| `fourty_two_pattern`  | `bool`              | Whether this cell is part of the "42" pattern |
| `coordinates`         | `tuple[int, int]`   | `(row, col)` position of the cell in the grid |

### `MazeGenerator` (abstract base class)

```python
MazeGenerator(width: int, height: int, *, seed: int = -1, use_tj_pattern: bool = False)
```

| Parameter        | Description                                                                 |
|-------------------|-------------------------------------------------------------------------------|
| `width`           | Number of columns (x-axis)                                                    |
| `height`          | Number of rows (y-axis)                                                       |
| `seed`            | Signed 32-bit int for reproducible generation. `-1` (default) picks a random seed. |
| `use_tj_pattern`  | Use the "TJ" pattern variant instead of the default "42" glyph                |

| Method / attribute        | Description                                                          |
|-----------------------------|--------------------------------------------------------------------|
| `generate_maze()` *(abstract, implemented by subclasses)* | Carves and returns the maze (`list[list[MazeCell]]`) |
| `make_imperfect()`          | Randomly opens a few extra walls to add loops/shortcuts             |
| `pattern_coordinates`       | List of `(row, col)` cells reserved by the "42"/"TJ" pattern, if any |
| `get_all_coords()`          | All `(row, col)` coordinates in the grid                            |
| `get_maze_cell_from_coordinate(coord)` | Look up a `MazeCell` by its coordinates                  |

#### `DFSearch(MazeGenerator)`

Depth-First Search / recursive-backtracker generator. Fast, produces long
winding corridors with few short dead ends.

#### `WilsonsAlgorithm(MazeGenerator)`

Loop-erased random walk generator. Produces a *uniform spanning tree*
(every possible perfect maze is equally likely), so it's structurally more
varied/branchy than DFS, at the cost of being slower to generate.

### `BFS`

| Method                                    | Description                                                        |
|---------------------------------------------|--------------------------------------------------------------------|
| `pathfind(maze, start, end)`                | Shortest path between two cells as `list[tuple[int, int]] \| None` |
| `path_to_directions(path)`                  | Converts a path of coordinates into `list[str]` of `N`/`S`/`E`/`W` |

Time complexity: `O(V + E)`, where `V` is the number of cells and `E` the
number of open passages between them.

## Building the package yourself

From inside the `mazegen/` directory:

```sh
python -m pip install --upgrade build
python -m build
```

This produces a `dist/` folder containing:

```
dist/
├── mazegen-1.0.0-py3-none-any.whl
└── mazegen-1.0.0.tar.gz
```

- **`.whl`** — pre-built wheel, the fastest to install (`pip install
  mazegen-1.0.0-py3-none-any.whl`), no build step on the target machine.
- **`.tar.gz`** — source distribution, useful if the target environment
  needs to rebuild the package itself, or for archival/inspection purposes.

The build configuration lives in [`pyproject.toml`](./pyproject.toml)
(build backend: `setuptools`, package name `mazegen`, version `1.0.0`,
`numpy>=2.4.1` as its only runtime dependency, requires Python `>=3.11`).

## Project structure

```
mazegen/
├── __init__.py       # public API: exposes MazeCell, MazeGenerator,
│                      # DFSearch, WilsonsAlgorithm, BFS
├── maze_gen.py        # MazeCell, MazeGenerator, DFSearch, WilsonsAlgorithm
├── bfs.py              # BFS pathfinder
├── pyproject.toml       # build/package metadata (setuptools backend)
└── README.md              # this file
```

## Resources

- [Maze generation algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Jamis Buck — "Maze Generation: Algorithm Recap"](https://weblog.jamisbuck.org/2011/2/7/maze-generation-algorithm-recap)
- [Wilson's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Loop-erased_random_walk#Wilson's_algorithm)
- [Breadth-first search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [NumPy `Generator`/`MT19937` documentation](https://numpy.org/doc/stable/reference/random/generator.html)
- [Python Packaging User Guide — Building and publishing](https://packaging.python.org/en/latest/tutorials/packaging-projects/)

For everything about the interactive terminal app built on top of this
library (configuration file, controls, rendering), see the
[root README](../README.md).
