# A-MAZE-Ing

**Generate mazes, watch them solve themselves in the terminal, and export the result**

![Example maze rendered in the terminal with walls, path, and 42 pattern](maze_example.png)

---

## What you get

- **Interactive terminal UI** — live maze drawing, colors you can change on the fly, and animated BFS pathfinding  
- **Two maze generators** — **DFS** (fast, long corridors) and **Wilson** (more uniform, slower on large grids)  
- **Shortest-path solving** — **BFS** from entry to exit  
- **Optional “42” pattern** — woven into the maze on large enough grids  
- **Reproducible runs** — optional random **seed**  
- **File output** — maze encoding plus a direction sequence (`N` / `S` / `E` / `W`)

---

## Quick start

### 1. Requirements

- **Python 3.11+**
- Recommended: **[uv](https://github.com/astral-sh/uv)** (the project’s `Makefile` uses it)

### 2. Install

From the project root:

```bash
make install
```

This creates a `.venv` and installs **numpy**, **termcolor**, **readchar**, plus dev tools (**flake8**, **mypy**).

*Manual alternative:* activate a venv and run `uv pip install numpy termcolor readchar` (same packages as in the Makefile).

### 3. Run

Use the included `config.txt` or copy it and edit values:

```bash
make run config.txt
```

Or, with the virtual environment activated:

```bash
python a_maze_ing.py config.txt
```

---

## Controls (in the app)

| Key | Action |
| ----- | -------- |
| **Space** | Generate / regenerate the maze (with animated pathfinding) |
| **P** | Toggle path visibility |
| **C** | Open the color menu (walls, “42”, path, background + preview) |
| **Q** | Quit |

---

## Configuration (`config.txt`)

Mandatory keys define size and start/end. Optional keys control perfection, output file, seed, and algorithm.

```ini
width = 20
height = 20
entry = 0, 0
exit = 19, 19

perfect = false
output_file = output.txt
seed = 42          # omit or use -1 for a random seed
algorithm = dfs    # dfs or wilson
```

- **`perfect = true`** — spanning tree: no loops, one path between any two cells.  
- **`perfect = false`** — the generator *may* add imperfections (loops); it is not guaranteed every time.  
- **`algorithm`** — `dfs` (default) or `wilson`.

See **`config.txt`** in the repo for comments and the exact format expected by the parser.

---

## Output file

By default **`output.txt`** (or whatever you set in `output_file`) contains:

1. Encoded maze data  
2. Entry coordinates (row/column order as produced by the program)  
3. Exit coordinates  
4. A **direction sequence** using **`N`**, **`S`**, **`E`**, **`W`**

---

## Algorithms (short)

| | DFS | Wilson |
| --- | ----- | -------- |
| **Character** | Fast; bias toward long corridors | Closer to uniform over mazes; slower on big grids |
| **Perfect mode** | Produces a perfect maze | Produces a perfect maze |

**BFS** finds a **shortest** path in the grid graph for the current walls (used for animation and for the exported directions).

---

## Project layout

```
A-MAZE-Ing/
├── mazegen/           # Core generation + BFS (installable package)
│   ├── maze_gen.py
│   └── bfs.py
├── a_maze_ing.py      # CLI entry point
├── render.py          # Terminal UI
├── config_reader.py
├── output_file_generation.py
├── output_validator.py
└── config.txt         # Example config
```

---

## Using `mazegen` from Python

```python
from mazegen import DFSearch, BFS

generator = DFSearch(width=20, height=20, seed=42)
maze = generator.generate_maze()
generator.make_imperfect()

solver = BFS()
path = solver.pathfind(maze, start=(0, 0), end=(19, 19))
directions = solver.path_to_directions(path)
```

`WilsonsAlgorithm` and types like `MazeCell` are available from the same package — see `mazegen/__init__.py` and `mazegen/maze_gen.py`.

---

## Team

| | Focus |
| --- | -------- |
| **hrandri2** | BFS, terminal UI / rendering, architecture, docs & tests |
| **tusandri** | DFS & Wilson, config system, build/Makefile & packaging, output format & validation, docs & tests |

---

## References

- [Maze generation algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm) (Wikipedia)  
- [BFS](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/) — GeeksforGeeks  
- Video: [BFS for mazes](https://www.youtube.com/watch?v=D14YK-0MtcQ), [DFS intuition](https://www.youtube.com/watch?v=Hr5cWUld4vU)
- <https://pythonwheels.com/?ref=blog.ippon.fr>
- <https://blog.ippon.fr/2025/05/12/uv-un-package-manager-python-adapte-a-la-data-partie-1-theorie-et-fonctionnalites/>
- <https://blog.ippon.fr/2025/05/14/uv-un-package-manager-python-adapte-a-la-data-partie-2-travaux-pratiques/>
- <https://blog.ippon.fr/2025/05/12/uv-un-package-manager-python-adapte-a-la-data-partie-1-theorie-et-fonctionnalites/>

---

## AI usage (transparency)

AI assistance was used for:
- refactoring and **mypy**-oriented typing fixes, bug fixes, docstrings, README text, and general code-review suggestions across the codebase.

- Interactive Visualization — DFS vs. Wilson: 
A step-by-step animation (`maze_dfs_vs_wilson_stepper.html`, which can be opened directly in any browser without any dependencies) illustrates the inner workings of the project’s two generation algorithms and its solution algorithm, based precisely on the actual code:
    - **DFS (`DFSearch.generate_maze()`)** — reconstructs `move_stack` in real time, calls to `get_available_cells()`, opening walls cell by cell (`current_cell.east = True` / `next_cell.west = True`), and backtracking when encountering a dead end.
    - **Wilson (`WilsonsAlgorithm.generate_maze()`)** — visualizes `existing_maze`, `move_stack`/`movements`, the random walk, and loop removal (`while newest in move_stack: pop()`), and validating all the walls of a step at once using `add_walk_to_maze()`.
    - **Solution (`BFS.pathfind()`)** — shows `queue.popleft()`, the construction of `parent{}`, and the final reconstruction of the path.

    - Usage
    Open `maze_dfs_vs_wilson_stepper.html` in a browser, then:

    | Key / Button | Action |
    |---|---|
    | `Space` | Auto-play / pause |
    | `←` / `→` | Previous / next step |
    | `D` / `W` | Toggle between DFS and Wilson |
    | `R` | Reset |
    | Speed slider | Adjust the auto-play tempo |

    A badge labeled `ƒ function_name()` shows at all times which function in the code is "currently running," and a log at the bottom of the screen details each operation (variables, broken walls, etc.) as it happens.

    > Educational tool generated for this project— not part of the executable program (`a_maze_ing.py`), used solely to understand and explain the algorithms.

**Made with care at 42 Antananarivo**
