"""Write a generated maze, its solution path and its endpoints to disk."""

from mazegen import MazeCell


def generate_output_file(
    maze: list[list[MazeCell]],
    path: list[str],
    start: tuple[int, int],
    end: tuple[int, int],
    filename: str,
) -> None:
    """Write the maze, its solution path and its endpoints to a file.

    Each cell is encoded as a single hexadecimal digit: a 4-bit mask
    (north=1, east=2, south=4, west=8) is subtracted from 15, so a
    digit of ``F`` means every wall is closed and ``0`` means every
    wall is open. Rows are newline-separated. After a blank line, the
    ``start`` and ``end`` coordinates are written as ``row,col``
    pairs, followed by the solution `path` directions.

    Parameters
    ----------
    maze : list[list[MazeCell]]
        The maze to write, as a grid of `MazeCell`.
    path : list[str]
        Solution path, as a list of direction characters
        (``"N"``/``"S"``/``"E"``/``"W"``), e.g. as returned by
        `mazegen.BFS.path_to_directions`.
    start : tuple[int, int]
        ``(row, col)`` coordinate of the maze entry.
    end : tuple[int, int]
        ``(row, col)`` coordinate of the maze exit.
    filename : str
        Path of the file to write.

    Returns
    -------
    None
    """
    with open(filename, "w") as file:
        for row in maze:
            for cell in row:
                open_walls = 0
                cell_num = 15
                if cell.north:
                    cell_num -= 1
                    open_walls += 1
                if cell.east:
                    cell_num -= 2
                    open_walls += 1
                if cell.south:
                    cell_num -= 4
                    open_walls += 1
                if cell.west:
                    cell_num -= 8
                    open_walls += 1
                file.write(hex(cell_num)[2:].capitalize())
            file.write("\n")
        file.write("\n")
        file.write(str(start[0]))
        file.write(",")
        file.write(str(start[1]))
        file.write("\n")
        file.write(str(end[0]))
        file.write(",")
        file.write(str(end[1]))
        file.write("\n")
        file.writelines(path)
