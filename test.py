from mazegen import DFSearch, BFS

generator = DFSearch(width=20, height=20, seed=42)
maze = generator.generate_maze()
generator.make_imperfect()

solver = BFS()
path = solver.pathfind(maze, start=(0, 0), end=(19, 19))
directions = solver.path_to_directions(path)