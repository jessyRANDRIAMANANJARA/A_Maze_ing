#!/usr/bin/env python3
"""Terminal rendering and interactive controls for the maze application.

Turns a generated maze (from `mazegen`) into colored Unicode
box-drawing art in the terminal, animates the solution path, and
drives the interactive keypress menu (generate / toggle path / change
colors / change pattern / quit).
"""
import itertools
import os
from collections.abc import Callable
from enum import Enum
from typing import Any, Literal, Optional

from termcolor import colored

from mazegen import (
    MazeCell,
    MazeGenerator,
)
from output_file_generation import generate_output_file

WALL_MARKER = "⚠ "

def colorize(
    wall_color: str,
    fourty_two: str,
    path_color: Optional[str],
    background: Optional[str],
    start_color: str = "green",
    end_color: str = "red",
    start_marker: str = "S ",
    end_marker: str = "E ",
) -> Callable[[str, bool], str]:
    """Create a colorizer function for maze rendering.

    Parameters
    ----------
    wall_color : str
        Color for walls.
    fourty_two : str
        Color for the 42 pattern cells.
    path_color : str or None
        Color for path markers (the wall marker and its connectors).
        If None, falls back to the `fourty_two` color for those glyphs.
    background : str or None
        Background color applied to every colored glyph.
    start_color : str, optional
        Color for the start marker. Default is ``"green"``.
    end_color : str, optional
        Color for the end marker. Default is ``"red"``.
    start_marker : str, optional
        Character used for the start marker (before padding). Default
        is ``"S "``.
    end_marker : str, optional
        Character used for the end marker (before padding). Default
        is ``"E "``.

    Returns
    -------
    Callable[[str, bool], str]
        A function ``_colorize(text, is_wall)`` that returns `text`
        wrapped in the appropriate ANSI color codes.
    """

    def _colorize(text: str, is_wall: bool) -> Any:
        """Apply the appropriate color to a single rendered glyph.

        Parameters
        ----------
        text : str
            Glyph to colorize (a wall segment or a content-grid cell).
        is_wall : bool
            Whether `text` is a wall segment (True) or a content cell
            such as a path marker/endpoint marker/empty space (False).

        Returns
        -------
        str
            `text` wrapped in ANSI color codes.
        """
        if path_color and text == WALL_MARKER:
            return colored(text, path_color, background)

        if text == start_marker:
            return colored(text, start_color, background)

        if text == end_marker:
            return colored(text, end_color, background)

        color: str = wall_color if is_wall else fourty_two
        return colored(text, color, background)

    return _colorize


class Characters(Enum):
    """Maps a (north, south, east, west) wall-connection tuple to a glyph.

    Each member associates the four cardinal directions a wall segment
    connects to with the Unicode box-drawing character that should be
    drawn for that combination (e.g. a wall open to both north and
    south renders as ``║``).
    """

    NONE = ((False, False, False, False), " ")
    NORTH = ((True, False, False, False), "╵")
    SOUTH = ((False, True, False, False), "╷")
    EAST = ((False, False, True, False), "╶")
    WEST = ((False, False, False, True), "╴")

    NORTH_SOUTH = ((True, True, False, False), "║")
    EAST_WEST = ((False, False, True, True), "═")

    NORTH_EAST = ((True, False, True, False), "╚")
    NORTH_WEST = ((True, False, False, True), "╝")
    SOUTH_EAST = ((False, True, True, False), "╔")
    SOUTH_WEST = ((False, True, False, True), "╗")

    NORTH_SOUTH_EAST = ((True, True, True, False), "╠")
    NORTH_SOUTH_WEST = ((True, True, False, True), "╣")
    SOUTH_EAST_WEST = ((False, True, True, True), "╦")
    NORTH_EAST_WEST = ((True, False, True, True), "╩")

    NORTH_SOUTH_EAST_WEST = ((True, True, True, True), "╬")

    def __init__(self, tpl: tuple[bool, bool, bool, bool], char: str) -> None:
        """Store the connection tuple and its associated glyph.

        Parameters
        ----------
        tpl : tuple[bool, bool, bool, bool]
            ``(north, south, east, west)`` connection flags.
        char : str
            Unicode box-drawing character for that combination.

        Returns
        -------
        None
        """
        self.tuple: tuple[bool, bool, bool, bool] = tpl
        self.char: str = char


class MazeRenderer:
    """Renders maze data with wall characters and paths."""

    def __init__(self) -> None:
        """Build the wall-connection-tuple-to-glyph lookup table.

        Returns
        -------
        None
        """
        self.char_map: dict[tuple[bool, bool, bool, bool], str] = {
            member.tuple: member.char for member in Characters
        }

    def get_wall_char(self, n: bool, s: bool, e: bool, w: bool) -> str:
        """Get the wall glyph for a given combination of connections.

        Parameters
        ----------
        n, s, e, w : bool
            Whether the wall segment connects to the wall grid cell
            north, south, east and west of it, respectively.

        Returns
        -------
        str
            The matching Unicode box-drawing character, or a blank
            space if no wall connects in any direction.
        """
        return self.char_map.get((n, s, e, w), Characters.NONE.char)

    def render_maze_walls(
        self,
        maze: list[list[MazeCell]],
        colorizer: Callable[[str, bool], str] | None,
        path: list[tuple[int, int]] | None,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> str:
        """Render the full maze into a single, printable string.

        Builds a wall grid and a content grid twice the size of the
        maze (to leave room for wall segments between cells), carves
        the passages, marks the "42" pattern, the solution path (if
        any) and the entry/exit endpoints, then renders everything
        into colored text lines.

        Parameters
        ----------
        maze : list[list[MazeCell]]
            The maze to render.
        colorizer : Callable[[str, bool], str] or None
            Function used to colorize each rendered glyph, as returned
            by `colorize`. If None, no color is applied.
        path : list[tuple[int, int]] or None
            Solution path to draw, as a list of ``(row, col)``
            coordinates, or None to omit it.
        start : tuple[int, int]
            ``(row, col)`` coordinate of the maze entry.
        end : tuple[int, int]
            ``(row, col)`` coordinate of the maze exit.

        Returns
        -------
        str
            The fully rendered maze, as a multi-line string.
        """
        rows: int = len(maze)
        cols: int = len(maze[0])

        is_wall, content_grid, grid_h, grid_w = self._init_grids(rows, cols)
        self._carve_passages(maze, is_wall, rows, cols)
        self._apply_forty_two_pattern(maze, content_grid, rows, cols)
        self._apply_solved_path(content_grid, path)
        self._mark_endpoints(content_grid, start=start, end=end)

        return self._render_lines(is_wall, content_grid, grid_h, grid_w, colorizer)

    def _init_grids(
        self, rows: int, cols: int
    ) -> tuple[list[list[bool]], list[list[str]], int, int]:
        """Create the empty wall and content grids for rendering.

        The rendered grid is twice the size of the maze grid plus one,
        so that walls between cells have their own row/column.

        Parameters
        ----------
        rows : int
            Number of rows in the maze.
        cols : int
            Number of columns in the maze.

        Returns
        -------
        is_wall : list[list[bool]]
            Grid initialized to all True (every position is a wall
            until passages are carved).
        content_grid : list[list[str]]
            Grid initialized to blank spaces, used for non-wall
            content (path markers, endpoints, "42" pattern).
        grid_h : int
            Height of the rendered grid (``rows * 2 + 1``).
        grid_w : int
            Width of the rendered grid (``cols * 2 + 1``).
        """
        grid_h: int = rows * 2 + 1
        grid_w: int = cols * 2 + 1

        is_wall: list[list[bool]] = [
            [True for _ in range(grid_w)] for _ in range(grid_h)
        ]
        content_grid: list[list[str]] = [
            ["  " for _ in range(grid_w)] for _ in range(grid_h)
        ]

        return is_wall, content_grid, grid_h, grid_w

    def _carve_passages(
        self,
        maze: list[list[MazeCell]],
        is_wall: list[list[bool]],
        rows: int,
        cols: int,
    ) -> None:
        """Open passages in the wall grid based on maze cell connections.

        Parameters
        ----------
        maze : list[list[MazeCell]]
            The maze being rendered.
        is_wall : list[list[bool]]
            Wall grid to mutate in place, opening (setting to False)
            every position where a `MazeCell` has an open passage.
        rows : int
            Number of rows in the maze.
        cols : int
            Number of columns in the maze.

        Returns
        -------
        None
        """
        for r in range(rows):
            for c in range(cols):
                cell: MazeCell = maze[r][c]
                center_r, center_c = r * 2 + 1, c * 2 + 1

                is_wall[center_r][center_c] = False

                if cell.east:
                    is_wall[center_r][center_c + 1] = False
                if cell.south:
                    is_wall[center_r + 1][center_c] = False

    def _apply_forty_two_pattern(
        self,
        maze: list[list[MazeCell]],
        content_grid: list[list[str]],
        rows: int,
        cols: int,
    ) -> None:
        """Mark cells belonging to the decorative "42" pattern.

        Parameters
        ----------
        maze : list[list[MazeCell]]
            The maze being rendered.
        content_grid : list[list[str]]
            Content grid to mutate in place.
        rows : int
            Number of rows in the maze.
        cols : int
            Number of columns in the maze.

        Returns
        -------
        None
        """
        for r in range(rows):
            for c in range(cols):
                cell: MazeCell = maze[r][c]
                if not cell.fourty_two_pattern:
                    continue
                content_grid[r * 2 + 1][c * 2 + 1] = "⚡︎"

    def _apply_solved_path(
        self,
        content_grid: list[list[str]],
        path: list[tuple[int, int]] | None,
        marker: str = WALL_MARKER,
    ) -> None:
        """Draw the solution path (nodes and connectors) on the grid.

        No-op if `path` is empty or None.

        Parameters
        ----------
        content_grid : list[list[str]]
            Content grid to mutate in place.
        path : list[tuple[int, int]] or None
            Solution path as a list of ``(row, col)`` coordinates.
        marker : str, optional
            Glyph used to mark path nodes and connectors. Default is
            `WALL_MARKER`.

        Returns
        -------
        None
        """
        if not path:
            return
        self._mark_path_nodes(content_grid, path, marker)
        self._add_path_connectors(content_grid, path)

    def _mark_path_nodes(
        self,
        content_grid: list[list[str]],
        path: list[tuple[int, int]],
        marker: str,
    ) -> None:
        """Mark every cell of the path with `marker` on the content grid.

        Parameters
        ----------
        content_grid : list[list[str]]
            Content grid to mutate in place.
        path : list[tuple[int, int]]
            Solution path as a list of ``(row, col)`` coordinates.
        marker : str
            Glyph to place at each path cell.

        Returns
        -------
        None
        """
        for r, c in path:
            cr, cc = r * 2 + 1, c * 2 + 1
            content_grid[cr][cc] = marker

    def _add_path_connectors(
        self, content_grid: list[list[str]], path: list[tuple[int, int]]
    ) -> None:
        """Draw connector segments between consecutive path nodes.

        Fills the wall-grid position between each pair of consecutive
        path cells with `WALL_MARKER`, so the path appears as a
        continuous line rather than disconnected dots.

        Parameters
        ----------
        content_grid : list[list[str]]
            Content grid to mutate in place.
        path : list[tuple[int, int]]
            Solution path as a list of ``(row, col)`` coordinates.

        Returns
        -------
        None
        """
        for (r1, c1), (r2, c2) in itertools.pairwise(path):
            cr1, cc1 = r1 * 2 + 1, c1 * 2 + 1
            # Horizontal step
            if r1 == r2 and c2 == c1 + 1:
                # east corridor between centers
                content_grid[cr1][cc1 + 1] = WALL_MARKER
            elif r1 == r2 and c2 == c1 - 1:
                # west corridor between centers
                content_grid[cr1][cc1 - 1] = WALL_MARKER
            # Vertical step
            elif c1 == c2 and r2 == r1 + 1:
                # south corridor between centers
                content_grid[cr1 + 1][cc1] = WALL_MARKER
            elif c1 == c2 and r2 == r1 - 1:
                # north corridor between centers
                content_grid[cr1 - 1][cc1] = WALL_MARKER

    def _mark_endpoints(
        self,
        content_grid: list[list[str]],
        *,
        start: tuple[int, int],
        end: tuple[int, int],
        start_marker: str = "🧍",
        end_marker: str = "🎖️ ",
    ) -> None:
        """Mark the entry and exit cells on the content grid.

        Parameters
        ----------
        content_grid : list[list[str]]
            Content grid to mutate in place.
        start : tuple[int, int]
            ``(row, col)`` coordinate of the maze entry.
        end : tuple[int, int]
            ``(row, col)`` coordinate of the maze exit.
        start_marker : str, optional
            Glyph placed at the entry. Default is ``"🧍"``.
        end_marker : str, optional
            Glyph placed at the exit. Default is ``"🎖️ "``.

        Returns
        -------
        None
        """
        start_coord = start
        end_coord = end

        sr, sc = start_coord
        er, ec = end_coord

        content_grid[sr * 2 + 1][sc * 2 + 1] = start_marker
        content_grid[er * 2 + 1][ec * 2 + 1] = end_marker

    def _render_lines(
        self,
        is_wall: list[list[bool]],
        content_grid: list[list[str]],
        grid_h: int,
        grid_w: int,
        colorizer: Callable[[str, bool], str] | None,
    ) -> str:
        """Render the wall and content grids into the final output string.

        Walls are drawn with the appropriate box-drawing glyph based
        on their neighbors; rendered glyphs are cached per
        ``(text, is_wall)`` pair to avoid recomputing colors for
        repeated characters.

        Parameters
        ----------
        is_wall : list[list[bool]]
            Wall grid, as produced by `_init_grids`/`_carve_passages`.
        content_grid : list[list[str]]
            Content grid, as produced by `_init_grids` and populated by
            `_apply_forty_two_pattern`, `_apply_solved_path` and
            `_mark_endpoints`.
        grid_h : int
            Height of the rendered grid.
        grid_w : int
            Width of the rendered grid.
        colorizer : Callable[[str, bool], str] or None
            Function used to colorize each glyph, or None for no
            color.

        Returns
        -------
        str
            The fully rendered maze, as a multi-line string.
        """
        cache: dict[tuple[str, bool], str] = {}
        lines: list[str] = []

        for r in range(grid_h):
            is_wall_r = is_wall[r]
            line_chars: list[str] = []
            for c in range(grid_w):
                if is_wall_r[c]:
                    n: bool = r > 0 and is_wall[r - 1][c]
                    s: bool = r < grid_h - 1 and is_wall[r + 1][c]
                    w: bool = c > 0 and is_wall_r[c - 1]
                    e: bool = c < grid_w - 1 and is_wall_r[c + 1]

                    base_char = self.get_wall_char(n, s, e, w)
                    padding: Literal["─", " "] = "─" if e else " "
                    rendered = base_char + padding

                    if colorizer:
                        key = (rendered, True)
                        colored_rendered = cache.get(key)
                        if colored_rendered is None:
                            colored_rendered = colorizer(rendered, True)
                            cache[key] = colored_rendered
                        line_chars.append(colored_rendered)
                    else:
                        line_chars.append(rendered)
                else:
                    rendered = content_grid[r][c]
                    if colorizer:
                        key = (rendered, False)
                        colored_rendered = cache.get(key)
                        if colored_rendered is None:
                            colored_rendered = colorizer(rendered, False)
                            cache[key] = colored_rendered
                        line_chars.append(colored_rendered)
                    else:
                        line_chars.append(rendered)
            lines.append("".join(line_chars))

        return "\n".join(lines)


class Terminal:
    """Interactive terminal driver with configurable algorithms and sizing.

    Owns the maze/pathfinder configuration, the current color scheme,
    the currently generated maze/path, and the interactive keypress
    loop that lets the user regenerate mazes, toggle the path, and
    change colors/pattern from the terminal.

    Attributes
    ----------
    COLORS : dict[str, str]
        Menu choice number to foreground color name, used by the
        color-selection menu.
    BACKGROUND_COLORS : dict[str, str | None]
        Menu choice number to background color name (or None for no
        background), used by the color-selection menu.
    """

    COLORS: dict[str, str] = {
        "1": "red",
        "2": "green",
        "3": "blue",
        "4": "magenta",
        "5": "cyan",
        "6": "white",
        "7": "grey",
        "8": "light_red",
        "9": "light_yellow",
    }

    BACKGROUND_COLORS: dict[str, str | None] = {
        "1": None,
        "2": "on_red",
        "3": "on_green",
        "4": "on_yellow",
        "5": "on_blue",
        "6": "on_magenta",
        "7": "on_cyan",
        "8": "on_white",
        "9": "on_light_grey",
    }

    def __init__(
        self,
        *,
        maze_generator_cls: type[MazeGenerator],
        pathfinder_cls: type[Any],
        width: int,
        height: int,
        seed: int,
        entry: tuple[int, int],
        end: tuple[int, int],
        delay: float,
        perfect: bool,
        output: str,
    ) -> None:
        """Initialize the terminal session with maze and rendering config.

        Parameters
        ----------
        maze_generator_cls : type[MazeGenerator]
            Maze generation algorithm to use (`DFSearch` or
            `WilsonsAlgorithm`).
        pathfinder_cls : type[Any]
            Pathfinder class to use to solve the maze (`BFS`).
        width : int
            Number of columns of the maze (x-axis).
        height : int
            Number of rows of the maze (y-axis).
        seed : int
            Signed 32-bit integer used to seed the random number
            generator, or ``-1`` for a random seed.
        entry : tuple[int, int]
            ``(row, col)`` coordinate of the maze entry.
        end : tuple[int, int]
            ``(row, col)`` coordinate of the maze exit.
        delay : float
            Delay, in seconds, between each step of the path animation.
        perfect : bool
            Whether the maze should stay perfect (no loops) or be made
            imperfect (extra loops/shortcuts) after generation.
        output : str
            Path of the file every generated maze snapshot is written
            to.

        Returns
        -------
        None
        """
        self.maze_generator_cls: type[MazeGenerator] = maze_generator_cls
        self.pathfinder_cls: type[Any] = pathfinder_cls
        self.width: int = width
        self.height: int = height
        self.seed: int = seed
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = end
        self.delay: float = delay
        self.perfect: bool = perfect
        self.output: str = output

        self.renderer: MazeRenderer = MazeRenderer()
        self.wall_color: str = "blue"
        self.fourty_two: str = "light_yellow"
        self.path_color: str = "red"
        self.background: str | None = None
        self.colorizer = self._build_colorizer()

        self.maze: list[list[MazeCell]] | None = None
        self.path: list[tuple[int, int]] | None = None
        self.show_path: bool = True
        self.use_tj_pattern: bool = False

    @staticmethod
    def _clear_screen() -> None:
        """Clear the terminal screen.

        Returns
        -------
        None
        """
        os.system("clear")

    def _select_color_from_list(
        self, colors: tuple[str, ...] | list[str], prompt: str
    ) -> str | None:
        """Prompt the user to pick a color from a list of color names.

        Parameters
        ----------
        colors : tuple[str, ...] or list[str]
            Sequence of color names to choose from.
        prompt : str
            Prompt displayed above the selection menu.

        Returns
        -------
        str or None
            The selected color name, or None if the input was not a
            valid digit or was out of range.
        """
        import readchar

        self._clear_screen()
        print(f"{prompt}\n")
        for idx, color_name in enumerate(colors, 1):
            print(f"  {idx}. {colored(color_name, color_name)}")

        choice = readchar.readchar()
        if not choice.isdigit():
            return None

        idx = int(choice) - 1
        return colors[idx] if 0 <= idx < len(colors) else None

    def _build_colorizer(self) -> Callable[[str, bool], str]:
        """Build a colorizer function from the current color settings.

        Returns
        -------
        Callable[[str, bool], str]
            Colorizer built from `self.wall_color`, `self.fourty_two`,
            `self.path_color` and `self.background`, as returned by
            `colorize`.
        """
        base = colorize(
            wall_color=self.wall_color,
            fourty_two=self.fourty_two,
            path_color=self.path_color,
            background=self.background,
        )

        return base

    @staticmethod
    def _print_colored_color(color_name: str) -> Any:
        """Render a color's name in its own color, for display in menus.

        Parameters
        ----------
        color_name : str
            Name of the color (e.g. ``"red"``, as understood by
            `termcolor`).

        Returns
        -------
        str
            `color_name` wrapped in the matching ANSI color code.
        """
        return colored(text=color_name, color=color_name)

    def _color_menu(self) -> None:
        """Run the interactive color-configuration menu loop.

        Lets the user pick the wall, "42" pattern, path and
        background colors, and preview/regenerate the current maze
        with the chosen colors, until ``0`` is pressed to go back to
        the main menu.

        Returns
        -------
        None

        Raises
        ------
        ImportError
            If the `readchar` library is not installed.
        """
        try:
            import readchar
        except ImportError:
            raise ImportError(
                "Error: 'readchar' library not found. Install it with: "
                + "pip install readchar"
            )

        while True:
            self._clear_screen()
            print("\n=== Color Configuration Menu ===\n")
            print(f"1 - Wall Color: {self._print_colored_color(self.wall_color)}")
            print(f"2 - 42 Color: {self._print_colored_color(self.fourty_two)}")
            print(f"3 - Path Color: {self._print_colored_color(self.path_color)}")
            bg_display = (
                self.background.replace("on_", "") if self.background else "None"
            )
            print(f"4 - Background: {bg_display}")
            if self.maze and self.renderer:
                print("5 - Preview & Regenerate Maze")
            print("\n0 - Back to Main Menu\n")

            try:
                key: str = readchar.readchar()

                match key:
                    case "1":
                        selected = self._select_color_from_list(
                            list(self.COLORS.values()), "Select Wall Color:"
                        )
                        if selected:
                            self.wall_color = selected
                            self.colorizer = self._build_colorizer()

                    case "2":
                        selected = self._select_color_from_list(
                            list(self.COLORS.values()),
                            "Select 42 Color:",
                        )
                        if selected:
                            self.fourty_two = selected
                            self.colorizer = self._build_colorizer()

                    case "3":
                        selected = self._select_color_from_list(
                            list(self.COLORS.values()), "Select Path Color:"
                        )
                        if selected:
                            self.path_color = selected
                            self.colorizer = self._build_colorizer()

                    case "4":
                        self._clear_screen()
                        print("Select Background Color:\n")
                        for key, bg in self.BACKGROUND_COLORS.items():
                            if bg is None:
                                print("  1. None (Default)")
                            else:
                                bg_name = bg.replace("on_", "")
                                print(f"  {key}. {colored(bg_name, 'white', bg)}")
                        choice: str = readchar.readchar()
                        if choice in self.BACKGROUND_COLORS:
                            self.background = self.BACKGROUND_COLORS[choice]
                            self.colorizer = self._build_colorizer()

                    case "5" if self.maze:
                        self._render_current_maze(force_show_path=True)
                        print("\nPress any key to return to color menu...")
                        readchar.readchar()

                    case "0":
                        self.colorizer = self._build_colorizer()
                        return

            except KeyboardInterrupt:
                return

    def _render_current_maze(self, force_show_path: bool | None = None) -> None:
        """Render the current maze to the terminal, along with the menu.

        Parameters
        ----------
        force_show_path : bool or None, optional
            If given, overrides `self.show_path` for this render only
            (used for the "preview" option and the animation's final
            frame). If None (default), `self.show_path` is used.

        Returns
        -------
        None
        """
        if self.maze is None:
            print("No maze generated yet. Press SPACE to generate one.")
            return

        show_path = self.show_path if force_show_path is None else force_show_path
        rendered = self.renderer.render_maze_walls(
            self.maze,
            self.colorizer,
            path=self.path if (show_path and self.path) else None,
            start=self.entry,
            end=self.exit,
        )
        self._clear_screen()
        print(rendered)
        print(
            "==== MENU ===="
            + f"\n[Path: {'VISIBLE' if show_path else 'HIDDEN'}]\n"
            + "Press:\n"
            + "[SPACE] to regenerate the maze\n"
            + "[P]     to show the path\n"
            + "[C]     to change the colors\n"
            + "[T]     to change Pattern\n"
            + "[Q]     to quit.\n"
        )

    def _animate_path(self) -> None:
        """Reveal the solution path on the maze, one step at a time.

        Redraws the maze with an increasingly long prefix of
        `self.path`, pausing `self.delay` seconds between each frame,
        so the path appears to be walked from entry to exit. No-op if
        there is no maze or no (long enough) path.

        Returns
        -------
        None
        """
        import time

        if not self.maze or not self.path or len(self.path) < 2:
            print("No path to animate")
            return

        path_steps = self.path

        rendered = self.renderer.render_maze_walls(
            self.maze,
            self.colorizer,
            path=None,
            start=self.entry,
            end=self.exit,
        )
        print(rendered)
        time.sleep(self.delay)

        for i in range(1, len(path_steps) + 1):
            partial_path: list[tuple[int, int]] = path_steps[:i]
            rendered = self.renderer.render_maze_walls(
                self.maze,
                self.colorizer,
                path=partial_path,
                start=self.entry,
                end=self.exit,
            )
            self._clear_screen()
            print(rendered)
            time.sleep(self.delay)

    def _generate_maze_and_path(self) -> None:
        """Generate a new maze, solve it, and write it to the output file.

        Builds a new maze with `self.maze_generator_cls`, applies
        `make_imperfect` if `self.perfect` is False, solves it with
        `self.pathfinder_cls`, stores the result in `self.maze`/
        `self.path`, and writes a snapshot to `self.output` via
        `output_file_generation.generate_output_file`.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If the entry and exit coordinates are identical, or if
            either falls inside the decorative "42"/"TJ" pattern.
        """
        generator: MazeGenerator = self.maze_generator_cls(
            width=self.width,
            height=self.height,
            seed=self.seed,
            use_tj_pattern=self.use_tj_pattern,
        )
        self.maze = generator.generate_maze()
        if self.entry == self.exit:
            raise ValueError("maze entry and exit cannot be on the same tile")
        if (
            self.entry in generator.pattern_coordinates
            or self.exit in generator.pattern_coordinates
        ):
            raise ValueError("Start and end cannot be inside the 42 pattern")
        if not self.perfect:
            generator.make_imperfect()
        solver = self.pathfinder_cls()
        self.path = solver.pathfind(
            self.maze,
            start=self.entry,
            end=self.exit,
        )
        if self.path is None:
            self.path = []
        generate_output_file(
            self.maze,
            solver.path_to_directions(self.path),
            self.entry,
            self.exit,
            self.output,
        )

    def run(self) -> None:
        """Run the interactive terminal session until the user quits.

        Prints the banner and controls, then loops reading single
        keypresses (`readchar`) to generate a maze (SPACE), toggle the
        solution path (P), open the color menu (C), switch the
        decorative pattern (T), or quit (Q).

        Returns
        -------
        None

        Raises
        ------
        ImportError
            If the `readchar` library is not installed.
        """
        try:
            import readchar
        except ImportError:
            raise ImportError(
                "Error: 'readchar' library not found. Install it with: "
                + "pip install readchar"
            )

        # hides cursor
        print("\033[?25l")
        self._clear_screen()
        print("╔════════════════════════════════════════════╗")
        print("║         Interactive Maze Generator         ║")
        print("╠════════════════════════════════════════════╣")
        print("║  SPACE - Generate maze                     ║")
        print("║  P     - Toggle path visibility            ║")
        print("║  C     - Change colors                     ║")
        print("║  T     - Change Pattern                    ║")
        print("║  Q     - Quit                              ║")
        print("╚════════════════════════════════════════════╝")
        print(
            f"\nWidth={self.width}, Height={self.height}, Entry={self.entry}, "
            + f"Exit={self.exit}\n"
            + "Press SPACE to generate a maze...\n"
        )

        while True:
            try:
                key = readchar.readchar()

                match key.lower():
                    case "q":
                        print("\nGoodbye!")
                        break

                    case " ":
                        self._clear_screen()
                        print("Generating maze...\n")
                        self._generate_maze_and_path()

                        if self.show_path and self.path:
                            self._animate_path()
                            self._render_current_maze(force_show_path=True)
                        else:
                            self._render_current_maze(force_show_path=False)

                    case "p":
                        if self.maze is None:
                            print("Generate a maze first! (Press SPACE)")
                            continue
                        self.show_path = not self.show_path
                        self._render_current_maze()

                    case "c":
                        self._color_menu()
                        if self.maze:
                            self._render_current_maze()
                        else:
                            self._clear_screen()
                            print(
                                "Colors updated! Press SPACE to " + "generate a maze.\n"
                            )
                    case "t":
                        self.use_tj_pattern = not self.use_tj_pattern
                        self._clear_screen()
                        label = "TJ" if self.use_tj_pattern else "Standard"
                        print(f"Motif 42 : {label} — génération...\n")
                        self._generate_maze_and_path()

                        if self.show_path and self.path:
                            self._animate_path()
                            self._render_current_maze(force_show_path=True)
                        else:
                            self._render_current_maze(force_show_path=False)
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as exc:
                print(f"Error: {exc}")
                break
            finally:
                print("\033[?25h", end="")
