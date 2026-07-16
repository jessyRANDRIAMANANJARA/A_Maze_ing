#!/usr/bin/env python3
from collections import deque
from mazegen import MazeCell


class BFS:
    """Time complexity: O(V + E), where V is the number of cells and E
    is the number of connections between cells
    """

    def pathfind(
        self,
        maze: list[list[MazeCell]],
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> list[tuple[int, int]] | None:
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
        """Convert a path of coordinates
        to a list of directions (N, E, S, W)"""
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
