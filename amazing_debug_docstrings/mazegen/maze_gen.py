"""Core maze data model and generation algorithms.

Defines the `MazeCell` data structure, the abstract `MazeGenerator`
base class shared by all generation algorithms, and two concrete
generators: `DFSearch` (depth-first search / recursive backtracker)
and `WilsonsAlgorithm` (loop-erased random walk).
"""

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, fields

from numpy import random as nprand


@dataclass
class MazeCell:
    """A single cell of the maze grid.

    Parameters
    ----------
    north, south, east, west : bool
        Whether a passage is open in that direction.
    fourty_two_pattern : bool
        Whether this cell is part of the decorative "42"/"TJ" pattern.
    coordinates : tuple[int, int]
        ``(row, col)`` position of this cell within the maze grid.
    """

    north: bool
    south: bool
    east: bool
    west: bool
    fourty_two_pattern: bool
    coordinates: tuple[int, int]


class MazeGenerator(ABC):
    """Abstract base class for maze generation algorithms.

    Handles everything shared by every generation algorithm: RNG setup,
    canvas creation, decorative "42"/"TJ" pattern placement, and the
    imperfect-maze post-processing step. Subclasses only need to
    implement `generate_maze`.

    Parameters
    ----------
    width : int
        Number of columns of the maze (x-axis).
    height : int
        Number of rows of the maze (y-axis).
    seed : int, optional
        Signed 32-bit integer used to seed the random number
        generator, for reproducible mazes. ``-1`` (default) picks a
        random seed.
    use_tj_pattern : bool, optional
        If True, use the "TJ" pattern variant instead of the default
        "42" glyph. Default is False.

    Attributes
    ----------
    rng : numpy.random.Generator
        Mersenne Twister random number generator used for every random
        choice made during generation.
    width, height : int
        Maze dimensions, as given at construction.
    pattern_coordinates : list[tuple[int, int]]
        Coordinates reserved for the decorative pattern, empty if the
        maze is too small to fit one.
    maze : list[list[MazeCell]]
        The freshly created (empty) maze canvas.
    """

    def __init__(
        self, width: int, height: int, *,
        seed: int = -1, use_tj_pattern: bool = False
    ) -> None:
        if seed == -1:
            seed = nprand.randint(0, high=2147483647)
        self.rng = nprand.Generator(nprand.MT19937(seed=seed))
        self.width: int = int(width)
        self.height: int = int(height)
        self.use_tj_pattern: bool = use_tj_pattern
        if self.check_42_pattern_avilability():
            self.pattern_coordinates = (
                self.get_pattern_coords_tj()
                if self.use_tj_pattern
                else self.get_pattern_coords()
            )
        else:
            self.pattern_coordinates = []
        self.maze = self.create_maze_canvas()

    def check_42_pattern_avilability(self) -> bool:
        """Check whether the maze is large enough for the "42" pattern.

        Returns
        -------
        bool
            True if `width` >= 14 and `height` >= 10, False otherwise
            (in which case a notice is printed).
        """
        if int(self.width) >= 14 and int(self.height) >= 10:
            return True
        print("Maze is too small to fit the 42 pattern, omitting it!")
        return False

    def get_pattern_coords(self) -> list[tuple[int, int]]:
        """Compute the coordinates of the classic "42" pattern.

        The pattern is centered within the maze grid.

        Returns
        -------
        list[tuple[int, int]]
            ``(row, col)`` coordinates of every cell belonging to the
            "42" pattern.
        """
        y_start = (self.height - 5) // 2
        x_start = (self.width - 7) // 2

        offsets = [
            (0, 0),
            (0, 2),
            (0, 4),
            (0, 5),
            (0, 6),
            (1, 0),
            (1, 2),
            (1, 6),
            (2, 0),
            (2, 1),
            (2, 2),
            (2, 4),
            (2, 5),
            (2, 6),
            (3, 2),
            (3, 4),
            (4, 2),
            (4, 4),
            (4, 5),
            (4, 6),
        ]

        return [(y_start + dy, x_start + dx) for dy, dx in offsets]

    def get_pattern_coords_tj(self) -> list[tuple[int, int]]:
        """Compute the coordinates of the alternative "TJ" pattern.

        The pattern is centered within the maze grid.

        Returns
        -------
        list[tuple[int, int]]
            ``(row, col)`` coordinates of every cell belonging to the
            "TJ" pattern.
        """
        y_start = (self.height - 5) // 2
        x_start = (self.width - 7) // 2
        offsets = [
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 1),
            (2, 1),
            (3, 1),
            (4, 1),
            (0, 4),
            (0, 5),
            (0, 6),
            (1, 6),
            (2, 6),
            (3, 6),
            (4, 6),
            (4, 4),
            (4, 5),
            (3, 4),
        ]

        return [(y_start + dy, x_start + dx) for dy, dx in offsets]

    def create_maze_canvas(self) -> list[list[MazeCell]]:
        """Build the initial, fully-walled grid of `MazeCell` objects.

        Also populates the internal ``_cell_map`` lookup used by
        `get_maze_cell_from_coordinate`.

        Returns
        -------
        list[list[MazeCell]]
            A `height` x `width` grid of cells with all walls closed,
            with cells inside `pattern_coordinates` flagged via
            `MazeCell.fourty_two_pattern`.
        """
        canvas = []
        for lane in range(self.height):
            row = []
            for cell in range(self.width):
                if (lane, cell) in self.pattern_coordinates:
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

    def get_all_coords(self) -> list[tuple[int, int]]:
        """List the coordinates of every cell in the maze.

        Returns
        -------
        list[tuple[int, int]]
            ``(row, col)`` coordinates of every cell, in row-major
            order.
        """
        coords = []
        for row in self.maze:
            for cell in row:
                coords.append(cell.coordinates)
        return coords

    def remove_cell_from_array(
        self, cell: tuple[int, int], array: list[list[tuple[int, int]]]
    ) -> None:
        """Remove a coordinate from every row of a 2D coordinate array.

        Parameters
        ----------
        cell : tuple[int, int]
            Coordinate to remove.
        array : list[list[tuple[int, int]]]
            2D array to remove the coordinate from, mutated in place.

        Returns
        -------
        None
        """
        for row in array:
            if cell in row:
                row.remove(cell)

    def get_maze_cell_from_coordinate(self,
                                      coordinate: tuple[int, int]) -> MazeCell:
        """Look up the `MazeCell` at a given coordinate.

        Parameters
        ----------
        coordinate : tuple[int, int]
            ``(row, col)`` coordinate to look up.

        Returns
        -------
        MazeCell
            The cell located at `coordinate`.

        Raises
        ------
        ValueError
            If `coordinate` is not part of the maze.
        """
        try:
            return self._cell_map[coordinate]
        except KeyError:
            raise ValueError("Unexpected Error")

    def get_available_cells(
        self, current_cell: MazeCell, available: list[tuple[int, int]]
    ) -> dict[str, MazeCell]:
        """Find the neighbors of a cell that are still available.

        Parameters
        ----------
        current_cell : MazeCell
            Cell whose neighbors should be inspected.
        available : list[tuple[int, int]]
            Coordinates currently considered "available" (e.g. not yet
            visited by the generation algorithm).

        Returns
        -------
        dict[str, MazeCell]
            Mapping from direction name (``"north"``, ``"south"``,
            ``"east"``, ``"west"``) to the neighboring `MazeCell`, for
            every direction whose neighbor is in `available`.
        """
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
        """Randomly open extra walls to add loops to the maze.

        For every cell that currently has exactly three closed walls
        (i.e. a dead end) and is not part of the decorative pattern, a
        wall is opened towards a random, still-valid neighboring
        direction with a fixed probability. This turns a *perfect*
        maze (a spanning tree, exactly one path between any two cells)
        into an *imperfect* one (a few extra loops/shortcuts).

        Mutates `self.maze` in place.

        Returns
        -------
        None
        """
        for row in self.maze:
            for cell in row:
                walls = [
                    x.name
                    for x in fields(cell)
                    if not asdict(cell)[x.name]
                    and x.name != "fourty_two_pattern"
                ]
                threshhold: float = 2.0
                if (cell.coordinates in self.pattern_coordinates or
                        len(walls) != 3):
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
                    cell.coordinates[0] - 1,
                    cell.coordinates[1],
                ) in self.pattern_coordinates and "north" in walls:
                    walls.remove("north")
                if (
                    cell.coordinates[0] + 1,
                    cell.coordinates[1],
                ) in self.pattern_coordinates and "south" in walls:
                    walls.remove("south")
                if (
                    cell.coordinates[0],
                    cell.coordinates[1] + 1,
                ) in self.pattern_coordinates and "east" in walls:
                    walls.remove("east")
                if (
                    cell.coordinates[0],
                    cell.coordinates[1] - 1,
                ) in self.pattern_coordinates and "west" in walls:
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
    def generate_maze(self) -> list[list[MazeCell]]:
        """Carve passages through the maze canvas.

        Must be implemented by every concrete subclass.

        Returns
        -------
        list[list[MazeCell]]
            The fully generated maze.
        """
        pass


class WilsonsAlgorithm(MazeGenerator):
    """Maze generator based on Wilson's loop-erased random walk.

    Produces a *uniform spanning tree*: every possible perfect maze on
    the grid is equally likely to be generated, unlike depth-first
    search which is biased towards long corridors.

    Parameters
    ----------
    width : int
        Number of columns of the maze (x-axis).
    height : int
        Number of rows of the maze (y-axis).
    seed : int, optional
        Signed 32-bit integer used to seed the random number
        generator. ``-1`` (default) picks a random seed.
    use_tj_pattern : bool, optional
        If True, use the "TJ" pattern variant instead of the default
        "42" glyph. Default is False.
    """

    def __init__(
        self, width: int, height: int, *,
        seed: int = -1, use_tj_pattern: bool = False
    ) -> None:
        super().__init__(width, height,
                         seed=seed, use_tj_pattern=use_tj_pattern)

    def generate_maze(self) -> list[list[MazeCell]]:
        """Generate the maze using Wilson's algorithm.

        Repeatedly performs a random walk from an unvisited cell until
        it reaches a cell already part of the maze, erasing any loop
        the walk makes along the way, then stamps that loop-erased
        path onto the maze. Continues until every cell belongs to the
        maze.

        Returns
        -------
        list[list[MazeCell]]
            The fully generated maze.
        """
        maze = self.maze
        available = self.get_all_coords()
        for pattern_cell in self.pattern_coordinates:
            available.remove(pattern_cell)
        unvisited = available.copy()
        existing_maze = set()
        first_maze_cell_np = self.rng.choice(available)
        cell_coords: tuple[int, int] = (
            int(first_maze_cell_np[0]),
            int(first_maze_cell_np[1]),
        )
        existing_maze.add(cell_coords)
        unvisited.remove(cell_coords)
        move_stack: list[tuple[int, int]] = []
        movements: list[str] = []

        def add_walk_to_maze() -> None:
            """Carve the passages recorded in `move_stack`/`movements`.

            Applies every recorded move of the current loop-erased
            walk onto the maze cells, opening the matching wall on
            both sides of each step.

            Returns
            -------
            None
            """
            for move in range(len(move_stack) - 1):
                current_cell = self.get_maze_cell_from_coordinate(
                    move_stack[move])
                next_cell = self.get_maze_cell_from_coordinate(
                    move_stack[move + 1])
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
            """Advance the loop-erased random walk by one step.

            Erases any loop formed if the walk revisits a cell already
            in `move_stack`, and finalizes/carves the walk into the
            maze once it reaches a cell already part of `existing_maze`.

            Parameters
            ----------
            current_cell : MazeCell
                Cell the walk is currently standing on.

            Returns
            -------
            bool
                True if the walk has reached the existing maze and has
                been carved in (the walk is complete), False if it
                should continue.
            """
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
            adjacent = self.get_available_cells(current_cell,
                                                available=available)
            choice = str(self.rng.choice(list(adjacent.keys())))
            movements.append(choice)
            move_stack.append(adjacent[choice].coordinates)
            return False

        while len(unvisited) != 0:
            walk_start_np = self.rng.choice(unvisited)
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
                        move_stack[len(move_stack) - 1])
                )
        return maze


class DFSearch(MazeGenerator):
    """Maze generator based on depth-first search (recursive backtracker).

    Starting from a random cell, repeatedly walks to a random
    unvisited neighbor (carving a passage as it goes) and backtracks
    on dead ends, until every cell has been visited. Fast, and
    produces long, winding corridors with comparatively few short dead
    ends.

    Parameters
    ----------
    width : int
        Number of columns of the maze (x-axis).
    height : int
        Number of rows of the maze (y-axis).
    seed : int, optional
        Signed 32-bit integer used to seed the random number
        generator. ``-1`` (default) picks a random seed.
    use_tj_pattern : bool, optional
        If True, use the "TJ" pattern variant instead of the default
        "42" glyph. Default is False.
    """

    def __init__(
        self, width: int, height: int, *,
        seed: int = -1, use_tj_pattern: bool = False
    ) -> None:
        super().__init__(width, height,
                         seed=seed, use_tj_pattern=use_tj_pattern)

    def generate_maze(self) -> list[list[MazeCell]]:
        """Generate the maze using depth-first search.

        Returns
        -------
        list[list[MazeCell]]
            The fully generated maze.
        """
        maze = self.maze
        available = self.get_all_coords()
        for pattern_cell in self.pattern_coordinates:
            available.remove(pattern_cell)
        start_np = self.rng.choice(available)
        start: tuple[int, int] = (
            int(start_np[0]),
            int(start_np[1]),
        )
        available.remove(start)
        move_stack = []
        move_stack.append(start)

        def random_walk(current: MazeCell) -> None:
            """Advance the depth-first walk by one step from `current`.

            Carves a passage to a random unvisited neighbor of
            `current` and pushes it onto `move_stack`; if `current`
            has no unvisited neighbor left, backtracks by popping
            `move_stack` instead.

            Parameters
            ----------
            current : MazeCell
                Cell the walk is currently standing on.

            Returns
            -------
            None
            """
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
                    move_stack[len(move_stack) - 1])
            )
        return maze
