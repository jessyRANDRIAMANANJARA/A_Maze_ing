from numpy import random as nprand
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict, fields


@dataclass
class MazeCell:
    north: bool
    south: bool
    east: bool
    west: bool
    fourty_two_pattern: bool
    coordinates: Tuple[int, int]


class MazeGenerator(ABC):
    """The core maze generator"""

    def __init__(self, height: int, width: int, *, seed: int = -1) -> None:
        if seed == -1:
            seed = nprand.randint(0, high=2147483647)
        self.rng = nprand.Generator(nprand.MT19937(seed=seed))
        self.width: int = int(width)
        self.height: int = int(height)
        if self.check_42_pattern_avilability():
            self.pattern_coordinates = self.get_pattern_coords()
        else:
            self.pattern_coordinates = []
        self.maze = self.create_maze_canvas()

    def check_42_pattern_avilability(self) -> bool:
        if int(self.width) >= 14 and int(self.height) >= 10:
            return True
        print("Maze is too small to fit the 42 pattern, omitting it!")
        return False

    def get_pattern_coords(self) -> List[Tuple[int, int]]:
        coordinates: List[Tuple[int, int]] = []
        upper_left: tuple[int, int] = (
            int((self.height - 5) / 2),
            int((self.width - 7) / 2),
        )
        coordinates.append(upper_left)
        coordinates.append((upper_left[0] + 1, upper_left[1]))
        coordinates.append((upper_left[0] + 2, upper_left[1]))
        coordinates.append((upper_left[0] + 2, upper_left[1] + 1))
        coordinates.append((upper_left[0] + 2, upper_left[1] + 2))
        coordinates.append((upper_left[0] + 3, upper_left[1] + 2))
        coordinates.append((upper_left[0] + 4, upper_left[1] + 2))
        coordinates.append((upper_left[0], upper_left[1] + 4))
        coordinates.append((upper_left[0] + 2, upper_left[1] + 4))
        coordinates.append((upper_left[0] + 3, upper_left[1] + 4))
        coordinates.append((upper_left[0] + 4, upper_left[1] + 4))
        coordinates.append((upper_left[0], upper_left[1] + 5))
        coordinates.append((upper_left[0] + 2, upper_left[1] + 5))
        coordinates.append((upper_left[0] + 4, upper_left[1] + 5))
        coordinates.append((upper_left[0], upper_left[1] + 6))
        coordinates.append((upper_left[0] + 1, upper_left[1] + 6))
        coordinates.append((upper_left[0] + 2, upper_left[1] + 6))
        coordinates.append((upper_left[0] + 4, upper_left[1] + 6))
        return coordinates

    def create_maze_canvas(self) -> List[List[MazeCell]]:
        canvas = []
        for lane in range(self.height):
            row = []
            for cell in range(self.width):
                if tuple([lane, cell]) in self.pattern_coordinates:
                    row.append(
                        MazeCell(
                            False,
                            False,
                            False,
                            False,
                            True,
                            (lane, cell),
                        )
                    )
                else:
                    row.append(
                        MazeCell(
                            False,
                            False,
                            False,
                            False,
                            False,
                            (lane, cell),
                        )
                    )
            canvas.append(row)
        self._cell_map = {c.coordinates: c for r in canvas for c in r}
        return canvas

    def get_all_coords(self) -> List[tuple[int, int]]:
        coords = []
        for row in self.maze:
            for cell in row:
                coords.append(cell.coordinates)
        return coords

    def remove_cell_from_array(
        self, cell: tuple[int, int], array: List[List[tuple[int, int]]]
    ) -> None:
        for row in array:
            if cell in row:
                row.remove(cell)

    def get_maze_cell_from_coordinate(
        self, coordinate: tuple[int, int]
    ) -> MazeCell:
        try:
            return self._cell_map[coordinate]
        except KeyError:
            raise ValueError("Unexpected Error")

    def get_available_cells(
        self, current_cell: MazeCell, available: list[tuple[int, int]]
    ) -> Dict[str, MazeCell]:
        cells = {}
        north = (current_cell.coordinates[0] - 1, current_cell.coordinates[1])
        south = (current_cell.coordinates[0] + 1, current_cell.coordinates[1])
        east = (current_cell.coordinates[0], current_cell.coordinates[1] + 1)
        west = (current_cell.coordinates[0], current_cell.coordinates[1] - 1)
        if north in available:
            cells["north"] = self.get_maze_cell_from_coordinate(north)
        if south in available:
            cells["south"] = self.get_maze_cell_from_coordinate(south)
        if east in available:
            cells["east"] = self.get_maze_cell_from_coordinate(east)
        if west in available:
            cells["west"] = self.get_maze_cell_from_coordinate(west)
        return cells

    def make_imperfect(self) -> None:
        for row in self.maze:
            for cell in row:
                walls = [
                    x.name
                    for x in fields(cell)
                    if not asdict(cell)[x.name]
                    and x.name != "fourty_two_pattern"
                ]
                threshhold: float = 0.35
                if (
                    cell.coordinates in self.pattern_coordinates
                    or len(walls) != 3
                ):
                    continue
                if self.rng.random() <= 1 - threshhold:
                    continue
                if cell.coordinates[0] == 0:
                    walls.remove("north")
                if cell.coordinates[0] == self.height - 1:
                    walls.remove("south")
                if cell.coordinates[1] == 0:
                    walls.remove("west")
                if cell.coordinates[1] == self.width - 1:
                    walls.remove("east")
                if (
                    tuple([cell.coordinates[0] - 1, cell.coordinates[1]])
                    in self.pattern_coordinates
                    and "north" in walls
                ):
                    walls.remove("north")
                if (
                    tuple([cell.coordinates[0] + 1, cell.coordinates[1]])
                    in self.pattern_coordinates
                    and "south" in walls
                ):
                    walls.remove("south")
                if (
                    tuple([cell.coordinates[0], cell.coordinates[1] + 1])
                    in self.pattern_coordinates
                    and "east" in walls
                ):
                    walls.remove("east")
                if (
                    tuple([cell.coordinates[0], cell.coordinates[1] - 1])
                    in self.pattern_coordinates
                    and "west" in walls
                ):
                    walls.remove("west")
                if len(walls) == 0:
                    continue
                choice = self.rng.choice(walls)
                if choice == "north":
                    cell.north = True
                    self.get_maze_cell_from_coordinate(
                        (cell.coordinates[0] - 1, cell.coordinates[1])
                    ).south = True
                if choice == "south":
                    cell.south = True
                    self.get_maze_cell_from_coordinate(
                        (cell.coordinates[0] + 1, cell.coordinates[1])
                    ).north = True
                if choice == "west":
                    cell.west = True
                    self.get_maze_cell_from_coordinate(
                        (cell.coordinates[0], cell.coordinates[1] - 1)
                    ).east = True
                if choice == "east":
                    cell.east = True
                    self.get_maze_cell_from_coordinate(
                        (cell.coordinates[0], cell.coordinates[1] + 1)
                    ).west = True

    @abstractmethod
    def generate_maze(self) -> List[List[MazeCell]]:
        pass


class WilsonsAlgorithm(MazeGenerator):
    def __init__(self, width: int, height: int, *, seed: int = -1) -> None:
        super().__init__(width, height, seed=seed)

    def generate_maze(self) -> List[List[MazeCell]]:
        maze = self.maze
        available = self.get_all_coords()
        for pattern_cell in self.pattern_coordinates:
            available.remove(pattern_cell)
        unvisited = available.copy()
        existing_maze = set()
        first_maze_cell_np = tuple(self.rng.choice(available))
        cell_coords = (int(first_maze_cell_np[0]), int(first_maze_cell_np[1]))
        existing_maze.add(cell_coords)
        unvisited.remove(cell_coords)
        move_stack: list[tuple[int, int]] = []
        movements: List[str] = []

        def add_walk_to_maze() -> None:
            for move in range(len(move_stack) - 1):
                current_cell = self.get_maze_cell_from_coordinate(
                    move_stack[move]
                )
                next_cell = self.get_maze_cell_from_coordinate(
                    move_stack[move + 1]
                )
                if movements[move] == "north":
                    current_cell.north = True
                    next_cell.south = True
                elif movements[move] == "south":
                    current_cell.south = True
                    next_cell.north = True
                elif movements[move] == "east":
                    current_cell.east = True
                    next_cell.west = True
                elif movements[move] == "west":
                    current_cell.west = True
                    next_cell.east = True

        def random_looperased_walk(current_cell: MazeCell) -> bool:
            newest = move_stack.pop()
            while newest in move_stack:
                move_stack.pop()
                movements.pop()
            move_stack.append(newest)
            if current_cell.coordinates in existing_maze:
                for cell in move_stack:
                    existing_maze.add(cell)
                    if cell in unvisited:
                        unvisited.remove(cell)
                add_walk_to_maze()
                move_stack.clear()
                movements.clear()
                return True
            adjacent = self.get_available_cells(
                current_cell, available=available
            )
            choice = str(self.rng.choice(list(adjacent.keys())))
            movements.append(choice)
            move_stack.append(adjacent[choice].coordinates)
            return False

        while len(unvisited) != 0:
            walk_start_np = tuple(self.rng.choice(unvisited))
            walk_start: tuple[int, int] = (
                int(walk_start_np[0]),
                int(walk_start_np[1]),
            )
            move_stack.append(walk_start)
            walk_ended = random_looperased_walk(
                self.get_maze_cell_from_coordinate(walk_start)
            )
            while not walk_ended:
                walk_ended = random_looperased_walk(
                    self.get_maze_cell_from_coordinate(
                        move_stack[len(move_stack) - 1]
                    )
                )
        return maze


class DFSearch(MazeGenerator):
    def __init__(self, width: int, height: int, *, seed: int = -1) -> None:
        super().__init__(width, height, seed=seed)

    def generate_maze(self) -> List[List[MazeCell]]:
        maze = self.maze
        available = self.get_all_coords()
        for pattern_cell in self.pattern_coordinates:
            available.remove(pattern_cell)
        start_np = tuple(self.rng.choice(available))
        start: tuple[int, int] = (int(start_np[0]), int(start_np[1]))
        available.remove(start)
        move_stack = []
        move_stack.append(start)

        def random_walk(current: MazeCell) -> None:
            adjacent = self.get_available_cells(current, available=available)
            if adjacent == {}:
                move_stack.pop()
                return
            choice = self.rng.choice(list(adjacent.keys()))
            if choice == "north":
                current.north = True
                adjacent["north"].south = True
                available.remove(adjacent["north"].coordinates)
                move_stack.append(adjacent["north"].coordinates)
                return
            elif choice == "south":
                current.south = True
                adjacent["south"].north = True
                available.remove(adjacent["south"].coordinates)
                move_stack.append(adjacent["south"].coordinates)
                return
            elif choice == "east":
                current.east = True
                adjacent["east"].west = True
                available.remove(adjacent["east"].coordinates)
                move_stack.append(adjacent["east"].coordinates)
                return
            elif choice == "west":
                current.west = True
                adjacent["west"].east = True
                available.remove(adjacent["west"].coordinates)
                move_stack.append(adjacent["west"].coordinates)
                return

        while len(available) != 0:
            random_walk(
                self.get_maze_cell_from_coordinate(
                    move_stack[len(move_stack) - 1]
                )
            )
        return maze
