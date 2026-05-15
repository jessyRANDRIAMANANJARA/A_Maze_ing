import unittest

from maze_solver import solve_maze


class MazeSolverTests(unittest.TestCase):
    def test_returns_shortest_path(self):
        maze = [
            ".#.",
            "...",
            "##.",
        ]

        self.assertEqual(
            solve_maze(maze, (0, 0), (2, 2)),
            [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)],
        )

    def test_returns_none_when_blocked(self):
        maze = [
            ".#.",
            "###",
            ".#.",
        ]

        self.assertIsNone(solve_maze(maze, (0, 0), (2, 0)))

    def test_raises_on_non_rectangular_maze(self):
        with self.assertRaises(ValueError):
            solve_maze(["..", "..."], (0, 0), (1, 2))


if __name__ == "__main__":
    unittest.main()
