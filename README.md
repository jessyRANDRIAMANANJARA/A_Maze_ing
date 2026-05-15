# A_Maze_ing

A tiny Python maze solver that finds the shortest path between two points in a
2D maze using breadth-first search (BFS).

## Maze format

- `#` = wall
- `.` = walkable cell

## Usage

```python
from maze_solver import solve_maze

maze = [
    ".#.",
    "...",
    "##.",
]

path = solve_maze(maze, (0, 0), (2, 2))
print(path)  # [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)]
```
