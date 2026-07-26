# from mazegen import DFSearch, BFS

# generator = DFSearch(width=20, height=20, seed=42)
# maze = generator.generate_maze()
# generator.make_imperfect()

# solver = BFS()
# path = solver.pathfind(maze, start=(0, 0), end=(19, 19))
# directions = solver.path_to_directions(path)


def check_42_pattern_avilability(height: int, width: int) -> bool:
    if int(width) >= 14 and int(height) >= 10:
        return True
    print("Maze is too small to fit the 42 pattern, omitting it!")
    return False


def main() -> None:
    check_42_pattern_avilability(13, 9)

main()