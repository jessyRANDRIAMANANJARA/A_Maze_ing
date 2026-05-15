#!/usr/bin/env python3

from typing import List
from sys import argv
from os import remove

from a_maze_ing import MazeGenerator
from a_maze_ing import WHITE
from a_maze_ing import RED
from a_maze_ing import GREEN
from a_maze_ing import YELLOW
from a_maze_ing import BLUE
from a_maze_ing import MAGENTA
from a_maze_ing import CYAN
from a_maze_ing import BROWN
from a_maze_ing import BLACK
from a_maze_ing import RESET


def main() -> None:
    """the main function that start the program"""
    config_file: str = 'config.txt'

    if (len(argv) != 1):
        config_file = argv[1]

    try:
        with open(config_file, "r") as _:
            pass

    except FileNotFoundError:
        print(f"[!] No such file {config_file}")
        exit(0)

    except PermissionError:
        print(f"[!] You don't have read access on {config_file}")
        exit(0)

    try:
        COLORS: List[str] = [
            WHITE, RED, GREEN,
            YELLOW, BLUE, MAGENTA,
            CYAN, BROWN, BLACK
        ]
        color_index: int = 0
        maze_color: str = WHITE
        solution: bool = False
        animation: bool = False
        custom_solution: str = " ● "

        gen: MazeGenerator = MazeGenerator(config_file, animation)
        gen.dfs_generate()
        choice: int = 0

        while True:
            print(f"{WHITE}\n=====  A-MAZE-ING  =====")
            print("1) Regenerate a New Maze")
            print(f"2) {'Hide' if solution else 'Show'} Solution")
            print("3) Rotate Maze Colors")
            print("4) Save Hex Maze to a File")
            print("5) Save Rendered Maze to a File")
            print(f"6) {'Disable' if animation else 'Enable'} Animation")
            print("7) Remove saved mazes")
            print("8) Change walls style")
            print("9) Change solution style")
            print("----------")
            print("0) Quit\n")

            try:
                pt: str = f"{MAGENTA}╭───[ Choice from 0-9 ]\n╰─A-Maze-Ing:~$ "
                raw: str = input(pt).strip()
                choice: int = int(raw)

            except ValueError:
                gen.render_frame(maze_color=maze_color)
                print("\n[!] Invalid choice, please choose from 0-9")
                continue

            if not 0 <= choice <= 9:
                gen.render_frame(maze_color=maze_color)
                print("\n[!] Invalid choice, please choose from 0-9")
                continue

            if choice == 1:
                try:
                    gen = MazeGenerator(config_file, animation)
                    print(
                        f"{RESET}    ╭───[ Which algo would you like to run? ]"
                    )
                    print("    | 1- DFS Maze")
                    print("    | 2- BFS Maze")
                    algo: int = int(input("    ╰───: ").strip())

                    if algo not in [1, 2]:
                        raise ValueError()

                    if algo == 1:
                        gen.dfs_generate()

                    elif algo == 2:
                        gen.bfs_generate()

                    gen.reset_maze_visited()
                    gen.start_solving()
                    gen.render_frame(maze_color=maze_color)
                    print("\n[+] Maze Regenerated!")

                except ValueError:
                    gen.render_frame(maze_color=maze_color)
                    print("\n[!] Invalid choice, please choose from 1-2")
                    continue

            elif choice == 2:
                solution = not solution
                if solution:
                    gen.display_solution(
                        maze_color=maze_color,
                        custom_solution=custom_solution
                    )

                else:
                    gen.render_frame(maze_color=maze_color)
                print(
                    f"\n[+] Solution {'Shown' if solution else 'Hidden'}!"
                )

            elif choice == 3:
                color_index: int = (color_index + 1) % len(COLORS)
                maze_color: str = COLORS[color_index]
                gen.render_frame(maze_color=maze_color)
                print("\n[+] Color Rotated!")

            elif choice == 4:
                gen.save_maze()
                gen.render_frame(maze_color=maze_color)
                print(f"\n[+] Maze Saved to {gen.OUTPUT_FILE}!")

            elif choice == 5:
                gen.save_rendered()
                gen.render_frame(maze_color=maze_color)
                print(
                    f"\n[+] Rendered Maze Saved: rendered_{gen.OUTPUT_FILE}!"
                )

            elif choice == 6:
                animation = not animation
                gen.render_frame(maze_color=maze_color)
                print(
                    "\n[+] Animation "
                    f"{'Enabled' if animation else 'Disabled'}!"
                )

            elif choice == 7:
                gen.render_frame(maze_color=maze_color)
                f1: str = gen.OUTPUT_FILE
                f2: str = f"rendered_{f1}"
                try:
                    remove(f1)
                    print(f"\n[+] {f1} has been removed!")

                except Exception as e:
                    print(f"\n[!] Unable to remove {f1}, {e}!")

                try:
                    remove(f2)
                    print(f"\n[+] {f2} has been removed!")

                except Exception as e:
                    print(f"\n[!] Unable to remove {f2}, {e}!")

            elif choice == 8:
                print(
                    f"{RESET}    ╭───[ Enter one character for walls style ]"
                )
                print("    | [ENTER]: Use the default character")
                print("    | [Any Character]: For customization")
                wall_style: str = input("    ╰───: ").strip()

                try:
                    if len(wall_style) == 0:
                        gen.render_frame(maze_color=maze_color)
                        print("\n[*] Rendered with the default settings")

                    else:
                        if len(wall_style) != 1:
                            raise ValueError

                        gen.render_frame(
                            maze_color=maze_color,
                            wall_style=wall_style
                        )
                        print(f"\n[*] Rendered with: {wall_style}")

                except ValueError:
                    gen.render_frame(maze_color=maze_color)
                    print(
                        "\n[!] Invalid input, try again with one character!"
                    )

            elif choice == 9:
                print(f"{RESET}    ╭───[ Change solution style ]")
                print("    | 1) 🟠")
                print("    | 2) 🎱")
                print("    | 3) ⚽️")
                print("    | 4) 🥎")
                print("    | 5) 🏐")
                print("    | 0) Default")

                try:
                    solution_style: str = int(input("    ╰───: ").strip())

                    if solution_style == 0:
                        custom_solution = " ● "
                        gen.display_solution(maze_color=maze_color)
                        print("\n[*] Rendered with the default settings")

                    else:
                        if solution_style == 1:
                            custom_solution = "🟠 "
                        elif solution_style == 2:
                            custom_solution = "🎱 "
                        elif solution_style == 3:
                            custom_solution = "⚽️ "
                        elif solution_style == 4:
                            custom_solution = "🥎 "
                        elif solution_style == 5:
                            custom_solution = "🏐 "
                        else:
                            raise ValueError()
                        gen.display_solution(
                            maze_color=maze_color,
                            custom_solution=custom_solution
                        )
                        print(f"\n[+] Changed to: {custom_solution}")
                except ValueError:
                    gen.render_frame(maze_color=maze_color)
                    print("\n[!] Invalid choice!")

            elif choice == 0:
                print(f"{RESET}Quitting...")
                break

    except KeyboardInterrupt:
        print(f"{RESET}\nCtrl+C Detected, Exiting...")


if __name__ == "__main__":
    main()
