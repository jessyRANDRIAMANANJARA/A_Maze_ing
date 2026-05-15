"""Maze solving utilities."""

from collections import deque


def solve_maze(maze, start, end):
    """Return the shortest path from start to end, or None if no path exists."""
    if not maze:
        return None

    rows = len(maze)
    cols = len(maze[0])

    if any(len(row) != cols for row in maze):
        raise ValueError("Maze rows must all have the same length.")

    def in_bounds(point):
        r, c = point
        return 0 <= r < rows and 0 <= c < cols

    def walkable(point):
        r, c = point
        return maze[r][c] != "#"

    if not in_bounds(start) or not in_bounds(end):
        raise ValueError("Start and end must be inside maze bounds.")

    if not walkable(start) or not walkable(end):
        return None

    queue = deque([start])
    previous = {start: None}

    while queue:
        current = queue.popleft()
        if current == end:
            break

        r, c = current
        for nxt in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if in_bounds(nxt) and walkable(nxt) and nxt not in previous:
                previous[nxt] = current
                queue.append(nxt)

    if end not in previous:
        return None

    path = []
    node = end
    while node is not None:
        path.append(node)
        node = previous[node]

    path.reverse()
    return path
