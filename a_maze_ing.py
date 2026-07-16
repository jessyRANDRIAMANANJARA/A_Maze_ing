from sys import argv
from config_reader import read_config
from render import Terminal
from mazegen import DFSearch, WilsonsAlgorithm, BFS


def get_int_int_tuple(val_1: int, val_2: int) -> tuple[int, int]:
    """Convert two integers to a tuple."""
    return (val_1, val_2)


def main() -> None:
    """Parse config and run maze generation with rendering."""
    if len(argv) < 2:
        print("No config file given. Aborting...")
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
        height=int(configs["height"]),
        width=int(configs["width"]),
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
        delay=0.075,
    ).run()


if __name__ == "__main__":
    main()
