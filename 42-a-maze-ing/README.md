# A-Maze-Ing Project From 1337/42 Coding School

This project has been created as part of the 42 curriculum by **ottalhao** and **mrbib**.

## Description

A-Maze-Ing is a maze generator and solver written in Python.
It allows users to generate mazes of customizable sizes, visualize them in ASCII graphics, and save the generated mazes to files.
The project emphasizes modularity, OOP, type hints, and clean code structure, while practicing algorithms such as DFS and BFS for maze generation and solving.

---

## Instructions

### Requirements

- Python >= 3.10
- Optional: flake8, mypy (for linting and type checking)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/r3dBust3r/42-a-maze-ing.git
cd 42-a-maze-ing
```

2. **Install development tools (optional)**

```bash
make install
```

3. **Run common tasks**

```bash
make run      # run the program
make lint     # lint and type check
make debug    # run with debugger
make clean    # remove temporary files
```
---

## Configuration File

The configuration file allows you to control maze dimensions, entry/exit points, output, and generation behavior.

Example `config.txt`:

```
WIDTH           = 25
HEIGHT          = 9
ENTRY           = 0,0
EXIT            = 24,8
OUTPUT_FILE     = maze.txt
PERFECT         = True
SEED            = 42
```

* `WIDTH` and `HEIGHT`: dimensions of the maze
* `ENTRY` and `EXIT`: coordinates of the maze start and finish
* `OUTPUT_FILE`: path to save the maze
* `PERFECT`: if `True`, generates a maze with a single solution; if `False`, multiple paths may exist
* `SEED`: optional, ensures deterministic maze generation

---

## Chosen Maze Algorithm

* **Algorithm:** DFS & BFS
* **Reason for choice:** Simple to implement, efficient, and well-suited for small projects requiring full control over the maze generation process

---

## Maze Generator Module

### MazeGenerator Class

* **`render_frame(maze_color=WHITE, save=False, wall_style="█")`**
  Display or render the maze frame as ASCII. Can return a string if `save=True`.
  **Usage:**

  ```python
  maze.render_frame()
  ```

* **`save_rendered()`**
  Save the current maze rendering to a file in ASCII format.
  **Usage:**

  ```python
  maze.save_rendered()
  ```

* **`display_solution(maze_color=WHITE, custom_solution=" ● ")`**
  Show the solution path visually in the maze.
  **Usage:**

  ```python
  maze.display_solution()
  ```

* **`get_maze_str()`**
  Convert the maze into a string in hex format.
  **Usage:**

  ```python
  s = maze.get_maze_str()
  ```

* **`save_maze()`**
  Save the maze to the output file in hex format, including entry, exit, and solution.
  **Usage:**

  ```python
  maze.save_maze()
  ```

* **`dfs_generate()`**
  Generate the maze using Depth-First Search.
  **Usage:**

  ```python
  maze.dfs_generate()
  ```

* **`make_maze(x: int, y: int)`**
  Internal DFS function to carve paths starting at `(x, y)`.
  **Usage:**

  ```python
  maze.make_maze(0, 0)
  ```

* **`create_multiple_paths()`**
  Modify maze to add additional paths for non-perfect mazes.
  **Usage:**

  ```python
  maze.create_multiple_paths()
  ```

* **`bfs_generate()`**
  Generate the maze using Breadth-First Search.
  **Usage:**

  ```python
  maze.bfs_generate()
  ```

* **`two_make_maze(x: int, y: int)`**
  Internal BFS function to carve paths starting at `(x, y)`.
  **Usage:**

  ```python
  maze.two_make_maze(0, 0)
  ```

- Example usage:

```python
from a_maze_ing import MazeGenerator

# Initialize the maze generator with config file and animation
maze = MazeGenerator("config.txt", animation=True)

# Generate the maze using DFS
maze.dfs_generate()

# Save the maze in hex format
maze.save_maze()

# Save the rendered ASCII maze
maze.save_rendered()
```

---

## Team & Project Management

We discussed each part together and decided on individual responsibilities while ensuring constant collaboration.

### Roles

**ottalhao:**

* Project initialization
* Maze display and ASCII graphics rendering
* Saving mazes to a file
* Type hints
* Packaging
* Validation and testing
* README.md

**mrbib:**

* Algorithms implementation (Backtracking, DFS, BFS)
* Configuration parsing
* Writing docstrings
* Makefile

---

## Planning & Evolution

Our initial plan focused on a simple maze generator and solver.
As the project progressed, we added type hints, configuration handling, and ASCII rendering, evolving the project from a basic script into a modular and reusable package.

---

## Lessons Learned

* **What worked well:** Collaboration, modular design, type hints, and testing strategy
* **What could be improved:** Advanced maze generation options, automated testing coverage

---

## Tools Used

* Python 3.10+
* flake8 (linting)
* mypy (type checking)
* Makefile for task automation

---

## Resources

* Python official documentation
* 42 curriculum project guidelines
* AI assistance was used for general code organization, Makefile structuring
* Algorithm references for DFS & BFS implementation [Maze_generation_algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)

---

## Additional Notes

* The project emphasizes readability, maintainability, and adherence to Python best practices
* Designed to be easily extendable for future features such as GUI visualization or alternative maze generation algorithms.
