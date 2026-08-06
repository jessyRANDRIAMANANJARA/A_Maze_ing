** This project has been created as part of the 42 curriculum by tusandri, hrandri2 **
# mazegen - Maze Generation Library

Core maze generation and pathfinding module for A-MAZE-Ing.

## Overview

`mazegen` provides the core algorithms and data structures for generating
and solving mazes. It features multiple maze generation algorithms, a
breadth-first search pathfinder, and support for the iconic "42" pattern.

## Components

### `MazeCell` (maze_gen.py)

A dataclass representing a single cell in a maze with:
- **Walls**: `north`, `south`, `east`, `west` (boolean flags)
- **42 Pattern**: `fourty_two_pattern` marker
- **Position**: `coordinates` tuple (row, col)

### `MazeGenerator` (maze_gen.py) - Abstract Base

Core base class for maze generation algorithms with:
- Configurable dimensions (width, height)
- Mersenne Twister PRNG with optional seed for reproducibility
- Automatic "42" pattern placement (14x10+ mazes only)
- Canvas creation and cell management

#### Derived Algorithms

**DFSearch** - Depth-First Search algorithm for maze generation

**WilsonsAlgorithm** - Loop-erased random walk algorithm

Both support:
- `generate_maze()` - Creates perfect maze
- `make_imperfect()` - Adds random wall removal (35% threshold)

### `BFS` - Pathfinder

Breadth-First Search implementation for maze solving:
- `pathfind(maze, start, end)` - Finds shortest path
- `path_to_directions(path)` - Converts coordinates to N/E/S/W

## Usage

```python
from mazegen import DFSearch, BFS
from output_file_generation import generate_output_file

gen = DFSearch(width=16, height=16, seed=42)
maze = gen.generate_maze()

solver = BFS()
path = solver.pathfind(maze, start=(0, 0), end=(15, 15))
directions = solver.path_to_directions(path)

generate_output_file(
    maze=maze,
    path=directions,
    start=(0, 0),
    end=(15, 15),
    filename="output.txt",
)
```

## Module Exports

- `MazeCell` - Cell data structure
- `MazeGenerator` - Base generator class
- `DFSearch` - DFS maze generation
- `WilsonsAlgorithm` - Wilson's algorithm
- `BFS` - Breadth-first search pathfinder
