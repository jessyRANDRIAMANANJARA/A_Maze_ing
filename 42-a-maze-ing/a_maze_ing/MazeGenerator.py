from typing import List, Dict, Tuple, Union
from random import randint, seed, choice, shuffle
from sys import setrecursionlimit
from time import sleep
from os import system

from a_maze_ing.Parser import Parsing
from a_maze_ing.Cell import Cell
from a_maze_ing.Colors import WHITE, MAGENTA, CYAN


class MazeGenerator:
    """Maze generator class"""
    def __init__(
        self,
        config_file: str,
        animation: bool
    ) -> None:
        """initialize the maze generator object"""
        setrecursionlimit(10000)
        p: Parsing = Parsing(config_file)
        p.set_config()
        self.WIDTH: int = p.WIDTH
        self.HEIGHT: int = p.HEIGHT
        self.ANIMATION: bool = animation

        self.maze: List[List[Cell]] = []
        if p.SEED is None:
            self.seed: int = randint(0, 99999999)
        else:
            self.seed = p.SEED
        self.OUTPUT_FILE: str = p.OUTPUT_FILE
        self.PERFECT: Union[None, bool] = p.PERFECT
        self.ENTRY: Dict[str, int] = p.ENTRY
        self.EXIT: Dict[str, int] = p.EXIT
        self.solutions: List[List[str]] = []
        seed(self.seed)
        self.maze_init()

    def maze_init(self) -> None:
        """initialize the gird and set 42 position"""
        for y in range(self.HEIGHT):
            row: List = []
            for x in range(self.WIDTH):
                cell: Cell = Cell(15, False, False)
                row.append(cell)
            self.maze.append(row)

        offset_x: int = (self.WIDTH - 7) // 2
        offset_y: int = (self.HEIGHT - 5) // 2

        if self.WIDTH >= 7 and self.HEIGHT >= 5:
            pattern_42: List[Tuple[int, int]] = [
                (0, 0), (0, 1), (0, 2), (1, 2), (2, 0),
                (2, 1), (2, 2), (2, 3), (2, 4),  # '4'

                (4, 0), (5, 0), (6, 0), (6, 1), (6, 2), (5, 2),
                (4, 2), (4, 3), (4, 4), (5, 4), (6, 4)  # '2'
            ]

            for rel_x, rel_y in pattern_42:
                tx, ty = offset_x + rel_x, offset_y + rel_y

                if (
                    (self.ENTRY['x'] == tx and self.ENTRY['y'] == ty) or
                    (self.EXIT['x'] == tx and self.EXIT['y'] == ty)
                ):
                    print("Entry & Exit must not be in 42 position")
                    exit(0)

                self.maze[ty][tx].walls = 15
                self.maze[ty][tx].static = True
                self.maze[ty][tx].visited = True
        else:
            print("Error: Maze size too small for '42' pattern.")
            exit(0)

    def render_frame(
        self,
        maze_color: str = WHITE,
        save: bool = False,
        wall_style: str = "█"
    ) -> str:
        """rerender the frame of the maze"""
        w: str = wall_style
        BULLET_COLOR: str = MAGENTA
        rendered: str = ""

        if save:
            rendered = "========== RENDERED MAZE ==========\n"
            rendered += f"Entry Coordinates: {self.ENTRY}\n"
            rendered += f"Exit Coordinates: {self.EXIT}\n"
            rendered += f"Solution: {self.shortest()}\n"
            rendered += "===================================\n\n"
            BULLET_COLOR = ""
            maze_color = ""
        else:
            system('clear')
        for y in range(len(self.maze)):
            row = self.maze[y]
            left: str = ""
            right: str = ""
            line1: str = ""
            line2: str = ""

            for x in range(len(row)):
                cell: Cell = row[x]

                if (x == self.ENTRY['x'] and y == self.ENTRY['y']):
                    cell_representation = f"{BULLET_COLOR} ● {maze_color}"

                elif (x == self.EXIT['x'] and y == self.EXIT['y']):
                    cell_representation = f"{BULLET_COLOR} ● {maze_color}"

                else:
                    cell_representation = "   "

                if (cell.walls & 1):
                    line1 += f"{w}{w}{w}{w}{w}"
                else:
                    line1 += f"{w}   {w}"

                if (cell.walls & 8):
                    left = f"{w}"
                else:
                    left = " "

                if (cell.walls & 2):
                    right = f"{w}"
                else:
                    right = " "

                if (cell.walls == 15):
                    line2 += f"{w}{w}{w}{w}{w}"
                else:
                    line2 += f"{left}{cell_representation}{right}"

            if save:
                rendered += f"{line1}\n"
                rendered += f"{line2}\n"

            else:
                print(f"{maze_color}{line1}")
                print(f"{maze_color}{line2}")

        if save:
            rendered += f"{w}{w}{w}{w}{w}" * len(self.maze[0])
            return f"{rendered}\n\n"

        else:
            print(f"{maze_color}{w}{w}{w}{w}{w}" * len(self.maze[0]))
            if self.ANIMATION:
                sleep(.03)
            return ""

    def save_rendered(self) -> None:
        """save rendered to a file as ascii"""
        try:
            with open(f"rendered_{self.OUTPUT_FILE}", "w") as output:
                output.write(self.render_frame(save=True))
                print(f"[+] Maze saved to: rendered_{self.OUTPUT_FILE}")

        except Exception as e:
            print(f"[!] Unable to save your maze: {e}")

    def shortest(self) -> str:
        try:
            target: List[str] = self.solutions[0]
            for path in self.solutions:
                if len(path) < len(target):
                    target = path
            return "".join(target)
        except IndexError:
            return ""

    def display_solution(
        self,
        maze_color: str = WHITE,
        custom_solution: str = " ● "
    ) -> None:
        """show solution in the maze"""
        if not len(self.solutions):
            self.render_frame()
            print("\n[!] No maze to find solutions!")
            return

        path: str = self.shortest()
        solution_cells: List = []
        current: List = [
            self.ENTRY['x'],
            self.ENTRY['y']
        ]

        for char in path:

            if char == 'N':
                current = [current[0], current[1] - 1]
            if char == 'E':
                current = [current[0] + 1, current[1]]
            if char == 'S':
                current = [current[0], current[1] + 1]
            if char == 'W':
                current = [current[0] - 1, current[1]]

            solution_cells.append(current)

            system('clear')
            for y in range(len(self.maze)):
                row = self.maze[y]
                line1 = ""
                line2 = ""

                cell_representation: str = ""

                for x in range(len(row)):
                    cell = row[x]

                    if (
                        ([x, y] in solution_cells)
                        and not (
                            x == self.ENTRY['x'] and
                            y == self.ENTRY['y']
                        )
                        and not (x == self.EXIT['x'] and y == self.EXIT['y'])
                    ):
                        cell_representation = f"{CYAN}{custom_solution}"
                        cell_representation += maze_color

                    elif (x == self.ENTRY['x'] and y == self.ENTRY['y']):
                        cell_representation = f"{MAGENTA} ● {maze_color}"

                    elif (x == self.EXIT['x'] and y == self.EXIT['y']):
                        cell_representation = f"{MAGENTA} ● {maze_color}"

                    else:
                        cell_representation = "   "

                    if (cell.walls & 1):
                        line1 += "█████"
                    else:
                        line1 += "█   █"

                    if (cell.walls & 8):
                        left = "█"
                    else:
                        left = " "

                    if (cell.walls & 2):
                        right = "█"
                    else:
                        right = " "

                    if cell.walls == 15:
                        line2 += "█████"
                    else:
                        line2 += f"{left}{cell_representation}{right}"

                print(f"{maze_color}{line1}")
                print(f"{maze_color}{line2}")

            print(f"{maze_color}█████" * len(self.maze[0]))
            if self.ANIMATION:
                sleep(.1)

    def get_maze_str(self) -> str:
        """turn the maze into a string"""
        output: str = ""
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                val: int = self.maze[y][x].walls
                output += f"{val:X}"
            output += "\n"
        return output

    def save_maze(self) -> None:
        """save the maze to an output file in hex format"""
        with open(self.OUTPUT_FILE, "w") as f:
            f.write(self.get_maze_str())
            f.write(f"\n{self.ENTRY['x']},{self.ENTRY['y']}")
            f.write(f"\n{self.EXIT['x']},{self.EXIT['y']}\n")
            smallest: str = self.shortest()
            f.write("".join(smallest))

    def open_wall(self, cell: Cell, direction: str) -> None:
        """open wall in the cell"""
        match direction:
            case "N":
                cell.walls &= ~(1 << 0)  # 0001
            case "E":
                cell.walls &= ~(1 << 1)  # 0010
            case "S":
                cell.walls &= ~(1 << 2)  # 0100
            case "W":
                cell.walls &= ~(1 << 3)  # 1000

    def dfs_generate(self) -> None:
        """choose random position call the deep first search algo"""
        x: int = self.seed % self.WIDTH
        y: int = self.seed % self.HEIGHT
        while self.maze[y][x].static:
            x = (self.seed * 10) % self.WIDTH
            y = (self.seed * 10) % self.HEIGHT

        self.make_maze(x, y)
        if not self.PERFECT:
            self.create_multiple_paths()

    def make_maze(self, x: int, y: int) -> None:
        """apply the DFS algo"""
        self.render_frame(maze_color=WHITE)
        options: List = []
        self.maze[y][x].visited = True
        if y - 1 >= 0 and not self.maze[y - 1][x].visited:
            options.append((x, y - 1, "N"))
        if x + 1 < self.WIDTH and not self.maze[y][x + 1].visited:
            options.append((x + 1, y, "E"))
        if y + 1 < self.HEIGHT and not self.maze[y + 1][x].visited:
            options.append((x, y + 1, "S"))
        if x - 1 >= 0 and not self.maze[y][x - 1].visited:
            options.append((x - 1, y, "W"))

        shuffle(options)
        for tx, ty, direction in options:
            if not self.maze[ty][tx].visited:
                self.open_wall(self.maze[y][x], direction)
                match direction:
                    case "N":
                        self.open_wall(self.maze[ty][tx], "S")
                    case "E":
                        self.open_wall(self.maze[ty][tx], "W")
                    case "S":
                        self.open_wall(self.maze[ty][tx], "N")
                    case "W":
                        self.open_wall(self.maze[ty][tx], "E")
                self.make_maze(tx, ty)

    def reset_maze_visited(self) -> None:
        """reset all visited cells in the maze"""
        for y in self.maze:
            for x in y:
                x.visited = False

    def start_solving(self) -> None:
        """call the find solution method with the start and the end point"""
        self.solve_maze(
            self.ENTRY['x'],
            self.ENTRY['y'],
            self.EXIT['x'],
            self.EXIT['y'],
            []
        )

    def solve_maze(
        self,
        x: int,
        y: int,
        sx: int,
        sy: int,
        solve: List
    ) -> None:
        """find the solution and give the paths"""
        if x == sx and y == sy:
            self.solutions.append(list(solve))
            return

        options: List = []
        self.maze[y][x].visited = True

        if y - 1 >= 0 and (self.maze[y][x].walls & (1 << 0)) == 0:
            options.append((x, y - 1, "N"))
        if x + 1 < self.WIDTH and (self.maze[y][x].walls & (1 << 1)) == 0:
            options.append((x + 1, y, "E"))
        if y + 1 < self.HEIGHT and (self.maze[y][x].walls & (1 << 2)) == 0:
            options.append((x, y + 1, "S"))
        if x - 1 >= 0 and (self.maze[y][x].walls & (1 << 3)) == 0:
            options.append((x - 1, y, "W"))

        for tx, ty, direction in options:
            if not self.maze[ty][tx].static and not self.maze[ty][tx].visited:
                solve.append(direction)
                self.solve_maze(tx, ty, sx, sy, solve)
                solve.pop()
        self.maze[y][x].visited = False

    def create_multiple_paths(self) -> None:
        """create non perfect maze"""
        x: int = 0
        y: int = 0
        options = []
        for row in self.maze:
            x = 0
            for cell in row:
                if randint(0, 9) < 1 and not cell.static:
                    if y - 1 >= 0 and not self.maze[y - 1][x].static:
                        options.append((x, y - 1, "N"))
                    if x + 1 < self.WIDTH and not self.maze[y][x + 1].static:
                        options.append((x + 1, y, "E"))
                    if y + 1 < self.HEIGHT and not self.maze[y + 1][x].static:
                        options.append((x, y + 1, "S"))
                    if x - 1 >= 0 and not self.maze[y][x - 1].static:
                        options.append((x - 1, y, "W"))
                    choise = choice(options)
                    self.open_wall(cell, choise[2])
                    match choise[2]:
                        case "N":
                            self.open_wall(
                                self.maze[choise[1]][choise[0]], "S"
                            )
                        case "E":
                            self.open_wall(
                                self.maze[choise[1]][choise[0]], "W"
                            )
                        case "S":
                            self.open_wall(
                                self.maze[choise[1]][choise[0]], "N"
                            )
                        case "W":
                            self.open_wall(
                                self.maze[choise[1]][choise[0]], "E"
                            )
                    options.clear()
                x += 1
            y += 1
        self.render_frame(maze_color=WHITE)

    def bfs_generate(self) -> None:
        """choose random position call the breadth first search algo"""
        x: int = self.seed % self.WIDTH
        y: int = self.seed % self.HEIGHT
        while self.maze[y][x].static:
            x = (self.seed * 10) % self.WIDTH
            y = (self.seed * 10) % self.HEIGHT

        self.two_make_maze(x, y)
        self.render_frame(maze_color=WHITE)
        if not self.PERFECT:
            self.create_multiple_paths()

    def two_make_maze(self, x: int, y: int) -> None:
        """apply the BFS algo"""
        self.maze[y][x].visited = True
        que: List = []
        que.insert(0, (self.maze[y][x], y, x))
        while que != []:
            options: List = []
            y = que[0][1]
            x = que[0][2]

            que.pop(0)
            if y - 1 >= 0 and not self.maze[y - 1][x].visited:
                options.append((x, y - 1, "N"))
            if x + 1 < self.WIDTH and not self.maze[y][x + 1].visited:
                options.append((x + 1, y, "E"))
            if y + 1 < self.HEIGHT and not self.maze[y + 1][x].visited:
                options.append((x, y + 1, "S"))
            if x - 1 >= 0 and not self.maze[y][x - 1].visited:
                options.append((x - 1, y, "W"))

            shuffle(options)

            for tx, ty, direction in options:
                if not self.maze[ty][tx].visited:
                    self.open_wall(self.maze[y][x], direction)
                    match direction:
                        case "N":
                            self.open_wall(self.maze[ty][tx], "S")
                        case "E":
                            self.open_wall(self.maze[ty][tx], "W")
                        case "S":
                            self.open_wall(self.maze[ty][tx], "N")
                        case "W":
                            self.open_wall(self.maze[ty][tx], "E")
                    self.maze[ty][tx].visited = True
                    que.insert(0, (self.maze[ty][tx], ty, tx))
                    self.render_frame(maze_color=WHITE)
