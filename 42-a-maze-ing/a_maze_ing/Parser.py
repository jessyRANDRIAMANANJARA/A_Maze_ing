from typing import List, Dict, Union
from configparser import ConfigParser
from os import remove


class Parsing:
    """Parsing class"""
    def __init__(self, config_file: str) -> None:
        """initialize the object"""
        self.WIDTH: int = 0
        self.HEIGHT: int = 0
        self.ENTRY: Dict[str, int] = {}
        self.EXIT: Dict[str, int] = {}
        self.OUTPUT_FILE: str = ""
        self.PERFECT: Union[None, bool] = None
        self.SEED: Union[None, int] = None
        self.CONFIG_FILE: str = config_file

    def set_config(self) -> None:
        """set the config values in the object"""
        try:
            config: ConfigParser = ConfigParser()
            keys: List[str] = [
                "width",
                "height",
                "entry",
                "exit",
                "output_file",
                "perfect",
                "seed"
            ]

            try:
                with open(self.CONFIG_FILE, 'r') as file:
                    for line in file:
                        if line.startswith('#') or line == "\n":
                            continue
                        arr: List = line.split("=")
                        if arr[0].strip().lower() not in keys:
                            raise ValueError(arr[0].strip())
                        if len(arr) != 2:
                            raise IndexError(line.strip())
            except ValueError as e:
                print(f"Invalid key: {e}")
                exit(0)
            except IndexError as e:
                print(f"Invalid line: {e}")
                exit(0)

            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    config_string: str = '[root]\n' + f.read()
                    config.read_string(config_string)
            except Exception as e:
                print(f"Error exporting the data: {e}")
                exit(0)

            try:
                self.SEED = int(config['root']["seed"])
            except KeyError:
                self.SEED = None
            except ValueError as e:
                print(f"Invalid value: {e}")
                exit(0)

            try:
                self.WIDTH = int(config['root']["width"])
                if self.WIDTH < 9 or self.WIDTH > 45:
                    raise ValueError("Invalid width size")
            except KeyError:
                print("There no is no value in width")
                exit(0)
            except ValueError as e:
                print(f"Invalid value: {e}")
                exit(0)

            try:
                self.HEIGHT = int(config['root']["height"])
                if self.HEIGHT < 7 or self.HEIGHT > 45:
                    raise ValueError("Invalid height size")
            except KeyError as e:
                print(f"There no is no key for: {e}")
                exit(0)
            except ValueError as e:
                print(f"Invalid value: {e}")
                exit(0)

            try:
                entery: List = config['root']["entry"].strip().split(",")
                if len(entery) != 2:
                    raise ValueError()
                if entery[0] == "" or entery[1] == "":
                    raise IndexError()
                if (
                    self.WIDTH <= int(entery[0]) or
                    int(entery[0]) < 0 or
                    self.HEIGHT <= int(entery[1]) or
                    int(entery[1]) < 0
                ):
                    raise ValueError("Entry coordinates out of range")
                self.ENTRY = {"x": int(entery[0]), "y": int(entery[1])}
            except IndexError:
                print("Missing coordinates in entry")
                exit(0)
            except ValueError as e:
                print(f"Invalid coordinates: {e}")
                exit(0)
            except KeyError as e:
                print(f"Missing: {e}")
                exit(0)

            try:
                exit_: List = config['root']["exit"].strip().split(",")
                if len(exit_) != 2:
                    raise ValueError()
                if exit_[0] == "" or exit_[1] == "":
                    raise IndexError()
                if (
                    self.WIDTH <= int(exit_[0]) or
                    int(exit_[0]) < 0 or
                    self.HEIGHT <= int(exit_[1]) or
                    int(exit_[1]) < 0
                ):
                    raise ValueError("Exit coordinates out of range")
                self.EXIT = {"x": int(exit_[0]), "y": int(exit_[1])}
            except IndexError:
                print("Missing coordinates in entry")
                exit(0)
            except ValueError as e:
                print(f"Invalid coordinates: {e}")
                exit(0)
            except KeyError as e:
                print(f"Missing: {e}")
                exit(0)

            try:
                if self.ENTRY == self.EXIT:
                    raise ValueError("Entry & exit must not be the same point")
            except ValueError as e:
                print(e)
                exit(0)

            try:
                self.OUTPUT_FILE = str(config['root']["output_file"])
                with open(self.OUTPUT_FILE, "w") as _:
                    remove(self.OUTPUT_FILE)
            except PermissionError:
                print("You have no permission to write in this file")
                exit(0)
            except KeyError as e:
                print(f"Missing: {e}")
                exit(0)

            try:
                is_perfect = config['root']["perfect"]
                if is_perfect == "True" or is_perfect == "TRUE":
                    self.PERFECT = True
                elif is_perfect == "False" or is_perfect == "FALSE":
                    self.PERFECT = False
                else:
                    raise ValueError(
                        f"{config['root']['perfect']} is not True or False"
                    )
            except ValueError as e:
                print(f"Invalid value: {e}")
                exit(0)
            except KeyError as e:
                print(f"Missing: {e}")
                exit(0)

        except FileNotFoundError:
            print(f"There no {self.CONFIG_FILE} file")
            exit(0)
        except PermissionError:
            print("You have no permission to read in this file")
            exit(0)
        except IndexError as e:
            print(f"Invalid line: {e}")
            exit(0)
        except ValueError as e:
            print(f"Invalid key: {e}")
            exit(0)
        except Exception as e:
            print(f"Error in parasing: {e}")
            exit(0)
