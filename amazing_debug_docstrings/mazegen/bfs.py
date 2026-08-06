#!/usr/bin/env python3
"""Breadth-first search pathfinder for solving generated mazes."""

from collections import deque

from mazegen import MazeCell


class BFS:
    """Shortest-path solver for a maze, using breadth-first search.

    Notes
    -----
    Time complexity: ``O(V + E)``, where ``V`` is the number of cells
    and ``E`` is the number of open passages (connections) between
    cells.
    """

    def pathfind(
        self,
        maze: list[list[MazeCell]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> list[tuple[int, int]] | None:
        """Find the shortest path between two cells of the maze.

        Parameters
        ----------
        maze : list[list[MazeCell]]
            The maze to search, as a grid of `MazeCell`.
        start : tuple[int, int]
            ``(row, col)`` coordinate to start the search from.
        end : tuple[int, int]
            ``(row, col)`` coordinate to reach.

        Returns
        -------
        list[tuple[int, int]] or None
            The shortest sequence of coordinates from `start` to
            `end` (inclusive), or None if `start`/`end` are out of
            bounds or no path connects them.
        """
        height: int = len(maze)
        width: int = len(maze[0]) if height > 0 else 0

        if not (0 <= start[0] < height and 0 <= start[1] < width):
            return None
        if not (0 <= end[0] < height and 0 <= end[1] < width):
            return None

        queue: deque[tuple[int, int]] = deque([start])
        parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

        while queue:
            current = queue.popleft()

            if current == end:
                path: list[tuple[int, int]] = []
                node: tuple[int, int] | None = current
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path

            row, col = current
            current_cell: MazeCell = maze[row][col]

            neighbors = []

            if current_cell.north and row > 0:
                neighbors.append((row - 1, col))
            if current_cell.south and row < height - 1:
                neighbors.append((row + 1, col))
            if current_cell.east and col < width - 1:
                neighbors.append((row, col + 1))
            if current_cell.west and col > 0:
                neighbors.append((row, col - 1))

            for neighbor in neighbors:
                if neighbor not in parent:
                    parent[neighbor] = current
                    queue.append(neighbor)

        return None

    def path_to_directions(self, path: list[tuple[int, int]]) -> list[str]:
        """Convert a path of coordinates into a list of directions.

        Parameters
        ----------
        path : list[tuple[int, int]]
            Sequence of ``(row, col)`` coordinates, typically as
            returned by `pathfind`.

        Returns
        -------
        list[str]
            One direction character (``"N"``, ``"S"``, ``"E"`` or
            ``"W"``) per step of `path`. Empty if `path` has fewer
            than two coordinates.
        """
        if not path or len(path) < 2:
            return []

        directions: list[str] = []
        for i in range(len(path) - 1):
            current: tuple[int, int] = path[i]
            next_pos: tuple[int, int] = path[i + 1]

            row_diff: int = next_pos[0] - current[0]
            col_diff: int = next_pos[1] - current[1]

            if row_diff == -1:
                directions.append("N")
            elif row_diff == 1:
                directions.append("S")
            elif col_diff == 1:
                directions.append("E")
            elif col_diff == -1:
                directions.append("W")

        return directions
