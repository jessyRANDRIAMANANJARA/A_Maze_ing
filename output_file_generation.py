from mazegen import MazeCell


def generate_output_file(
    maze: list[list[MazeCell]],
    path: list[str],
    start: tuple[int, int],
    end: tuple[int, int],
    filename: str,
) -> None:
    """Write maze, path, and endpoints to output file."""
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
        file.write(str(end[0]))
        file.write(",")
        file.write(str(end[1]))
        file.write("\n")
        file.write(str(start[0]))
        file.write(",")
        file.write(str(start[1]))
        file.write("\n")
        for direction in path:
            file.write(direction)
