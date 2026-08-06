from sys import argv

from config_reader import read_config
from mazegen import BFS, DFSearch, WilsonsAlgorithm
from render import Terminal


def get_int_int_tuple(val_1: int, val_2: int) -> tuple[int, int]:
    """Convert two integers to a tuple."""
    return (val_1, val_2)


def check_42_pattern_avilability(height: int, width: int) -> str:
    if int(width) >= 14 and int(height) >= 10:
        return ""
    return "Maze is too small to fit the 42 pattern, omitting it!"


def main() -> None:
    """Parse config and run maze generation with rendering."""
    if len(argv) != 2:
        print("Invalid number of arguments. Please provide a config file.")
        return
    config = argv[1]
    try:
        file = open(config)
        if not file.readable():
            file.close()
            raise PermissionError("")
        file.close()
    except FileNotFoundError:
        print("Config file does not exist. Aborting...")
        return
    except PermissionError:
        print("Config file cannot be read. Aborting...")
        return
    try:
        configs = read_config(config)
    except Exception as e:
        print("Error: ", e)
        return
    if configs["algorithm"] == "dfs":
        gen: type[DFSearch | WilsonsAlgorithm] = DFSearch
    else:
        gen = WilsonsAlgorithm
    Terminal(
        width=int(configs["height"]),
        height=int(configs["width"]),
        entry=(
            int(configs["entry.x"]),
            int(configs["entry.y"]),
        ),
        end=(int(configs["exit.x"]), int(configs["exit.y"])),
        maze_generator_cls=gen,
        pathfinder_cls=BFS,
        seed=int(configs["seed"]),
        perfect=bool(configs["perfect"]),
        output=str(configs["output_file"]),
        delay=0.065,
    ).run()
    
    print(check_42_pattern_avilability(int(configs["height"]), int(configs["width"])))


if __name__ == "__main__":
    main()
