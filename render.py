#!/usr/bin/env python3
from typing import Callable, Literal, Type, Optional, Any
from mazegen import (
    MazeCell,
    MazeGenerator,
)
from termcolor import colored
from enum import Enum
from output_file_generation import generate_output_file
import os


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

    Args:
        wall_color: Color for walls.
        fourty_two: Color for the 42 pattern cells.
        path_color: Color for path markers (• and connectors).
        If None, uses fourty_two color.
        background: Background color.
        start_color: Color for the start marker.
        end_color: Color for the end marker.
        start_marker: Character used for the start marker (before padding).
        end_marker: Character used for the end marker (before padding).
    """

    def _colorize(text: str, is_wall: bool) -> str:

        if path_color and text == "▒▒":
            return colored(text, path_color, background)

        if text == start_marker:
            return colored(text, start_color, background)

        if text == end_marker:
            return colored(text, end_color, background)

        color: str = wall_color if is_wall else fourty_two
        return colored(text, color, background)

    return _colorize


class Characters(Enum):
    """Readable enum for wall-connection cases."""

    NONE = ((False, False, False, False), " ")
    NORTH = ((True, False, False, False), "╵")
    SOUTH = ((False, True, False, False), "╷")
    EAST = ((False, False, True, False), "╶")
    WEST = ((False, False, False, True), "╴")

    NORTH_SOUTH = ((True, True, False, False), "│")
    EAST_WEST = ((False, False, True, True), "─")

    NORTH_EAST = ((True, False, True, False), "╰")
    NORTH_WEST = ((True, False, False, True), "╯")
    SOUTH_EAST = ((False, True, True, False), "╭")
    SOUTH_WEST = ((False, True, False, True), "╮")

    NORTH_SOUTH_EAST = ((True, True, True, False), "├")
    NORTH_SOUTH_WEST = ((True, True, False, True), "┤")
    SOUTH_EAST_WEST = ((False, True, True, True), "┬")
    NORTH_EAST_WEST = ((True, False, True, True), "┴")

    NORTH_SOUTH_EAST_WEST = ((True, True, True, True), "┼")

    def __init__(self, tpl: tuple[bool, bool, bool, bool], char: str) -> None:
        self.tuple: tuple[bool, bool, bool, bool] = tpl
        self.char: str = char


class MazeRenderer:
    """Renders maze data with wall characters and paths."""

    def __init__(self) -> None:
        """Initialize character map for maze rendering."""
        self.char_map: dict[tuple[bool, bool, bool, bool], str] = {
            member.tuple: member.char for member in Characters
        }

    def get_wall_char(self, n: bool, s: bool, e: bool, w: bool) -> str:
        """Get wall character for directional connections."""
        return self.char_map.get((n, s, e, w), Characters.NONE.char)

    def render_maze_walls(
        self,
        maze: list[list[MazeCell]],
        colorizer: Callable[[str, bool], str] | None,
        path: list[tuple[int, int]] | None,
        start: tuple[int, int],
        end: tuple[int, int],
    ) -> str:
        """Render maze with walls, paths, and endpoints."""
        rows: int = len(maze)
        cols: int = len(maze[0])

        is_wall, content_grid, grid_h, grid_w = self._init_grids(rows, cols)
        self._carve_passages(maze, is_wall, rows, cols)
        self._apply_forty_two_pattern(maze, content_grid, rows, cols)
        self._apply_solved_path(content_grid, path)
        self._mark_endpoints(content_grid, start=start, end=end)

        return self._render_lines(
            is_wall, content_grid, grid_h, grid_w, colorizer
        )

    def _init_grids(
        self, rows: int, cols: int
    ) -> tuple[list[list[bool]], list[list[str]], int, int]:
        """Initialize wall and content grids for rendering."""
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
        """Mark wall grid based on maze cell connections."""
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
        """Mark special cells with 42 pattern indicator."""
        for r in range(rows):
            for c in range(cols):
                cell: MazeCell = maze[r][c]
                if not cell.fourty_two_pattern:
                    continue
                content_grid[r * 2 + 1][c * 2 + 1] = "░░"

    def _apply_solved_path(
        self,
        content_grid: list[list[str]],
        path: list[tuple[int, int]] | None,
        marker: str = "▒▒",
    ) -> None:
        """Apply solved path markers and connectors to grid."""
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
        """Mark path nodes on the content grid."""
        for r, c in path:
            cr, cc = r * 2 + 1, c * 2 + 1
            content_grid[cr][cc] = marker

    def _add_path_connectors(
        self, content_grid: list[list[str]], path: list[tuple[int, int]]
    ) -> None:
        """Connect consecutive nodes with segments along corridors."""
        for (r1, c1), (r2, c2) in zip(path, path[1:]):
            cr1, cc1 = r1 * 2 + 1, c1 * 2 + 1
            # Horizontal step
            if r1 == r2 and c2 == c1 + 1:
                # east corridor between centers
                content_grid[cr1][cc1 + 1] = "▒▒"
            elif r1 == r2 and c2 == c1 - 1:
                # west corridor between centers
                content_grid[cr1][cc1 - 1] = "▒▒"
            # Vertical step
            elif c1 == c2 and r2 == r1 + 1:
                # south corridor between centers
                content_grid[cr1 + 1][cc1] = "▒▒"
            elif c1 == c2 and r2 == r1 - 1:
                # north corridor between centers
                content_grid[cr1 - 1][cc1] = "▒▒"

    def _mark_endpoints(
        self,
        content_grid: list[list[str]],
        *,
        start: tuple[int, int],
        end: tuple[int, int],
        start_marker: str = "E ",
        end_marker: str = "S ",
    ) -> None:
        """Mark start and end positions on content grid."""
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
        """Build colored output strings from wall and content grids."""
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
    """Interactive terminal driver with configurable algorithms and sizing."""

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
        maze_generator_cls: Type[MazeGenerator],
        pathfinder_cls: Type[Any],
        width: int,
        height: int,
        seed: int,
        entry: tuple[int, int],
        end: tuple[int, int],
        delay: float,
        perfect: bool,
        output: str,
    ) -> None:
        """Initialize Terminal with maze and rendering config."""
        self.maze_generator_cls: Type[MazeGenerator] = maze_generator_cls
        self.pathfinder_cls: Type[Any] = pathfinder_cls
        self.width: int = width
        self.height: int = height
        self.seed: int = seed
        self.entry: tuple[int, int] = end
        self.exit: tuple[int, int] = entry
        self.delay: float = delay
        self.perfect: bool = perfect
        self.output: str = output

        self.renderer: MazeRenderer = MazeRenderer()
        self.wall_color: str = "magenta"
        self.fourty_two: str = "red"
        self.path_color: str = "magenta"
        self.background: str | None = "on_black"
        self.colorizer = self._build_colorizer()

        self.maze: list[list[MazeCell]] | None = None
        self.path: list[tuple[int, int]] | None = None
        self.show_path: bool = True

    @staticmethod
    def _clear_screen() -> None:
        """Clear terminal screen."""
        os.system("clear")

    def _select_color_from_list(
        self, colors: tuple[str, ...] | list[str], prompt: str
    ) -> str | None:
        """Select a color from a list/tuple of color names.

        Args:
            colors: Sequence of color names
            prompt: Display prompt for the selection menu

        Returns:
            Selected color name or None if selection is invalid
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
        """Build colorizer from current color settings."""
        base = colorize(
            wall_color=self.wall_color,
            fourty_two=self.fourty_two,
            path_color=self.path_color,
            background=self.background,
        )

        return base

    @staticmethod
    def _print_colored_color(color_name: str) -> str:
        """Return colored color name for display."""
        return colored(text=color_name, color=color_name)

    def _color_menu(self) -> None:
        """Display interactive color configuration menu."""
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
            print(
                f"1 - Wall Color: {self._print_colored_color(self.wall_color)}"
            )
            print(
                f"2 - 42 Color: {self._print_colored_color(self.fourty_two)}"
            )
            print(
                f"3 - Path Color: {self._print_colored_color(self.path_color)}"
            )
            bg_display = (
                self.background.replace("on_", "")
                if self.background
                else "None"
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
                                print(
                                    f"  {key}. {colored(bg_name, 'white', bg)}"
                                )
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

    def _render_current_maze(
        self, force_show_path: bool | None = None
    ) -> None:
        """Render and display current maze with optional path."""
        if self.maze is None:
            print("No maze generated yet. Press SPACE to generate one.")
            return

        show_path = (
            self.show_path if force_show_path is None else force_show_path
        )
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
            + "[P] to show the path\n[C] to change the colors\n[SPACE] to "
            + "regenerate the maze"
            + "\n[Q] to quit.\n"
        )

    def _animate_path(self) -> None:
        """Animate path solution step-by-step on maze."""
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
        """Generate maze and solve with pathfinder algorithm."""
        generator: MazeGenerator = self.maze_generator_cls(
            width=self.width, height=self.height, seed=self.seed
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
        """Start interactive maze generation and visualization loop."""
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
                                "Colors updated! Press SPACE to "
                                + "generate a maze.\n"
                            )

            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as exc:
                print(f"Error: {exc}")
                break
            finally:
                print("\033[?25h")
