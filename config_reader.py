def read_config(config_file: "str") -> dict[str, str | int | bool]:
    """Parse configuration file and validate required fields."""
    required = set(
        ["width", "height", "entry.x", "entry.y", "exit.x", "exit.y"]
    )
    configs: dict[str, str | int | bool] = {}
    with open(config_file) as config:
        for line in config:
            line = line.strip().lower()
            if line.startswith("#") or line.strip() == "":
                continue
            if "=" not in line:
                raise ValueError("Non-Comments must be declarations with =")
            key, val = map(str.strip, line.split("=", 1))
            if key == "width":
                if configs.get("width") is None:
                    configs["width"] = val
                    if int(configs["width"]) <= 0:
                        raise ValueError("width cannot be less than 1")
                else:
                    raise ValueError("Width is defined multiple times!")
            elif key == "height":
                if configs.get("height") is None:
                    configs["height"] = val
                    if int(configs["height"]) <= 0:
                        raise ValueError("height cannot be less than 1")
                else:
                    raise ValueError("Height is defined multiple times!")
            elif key == "entry":
                if (
                    configs.get("entry.x") is None
                    and configs.get("entry.y") is None
                ):
                    if "," not in val:
                        raise ValueError("Expected entry in this format: x,y")
                    x, y = map(str.strip, val.split(",", 1))
                    if int(x) < 0 or int(y) < 0:
                        raise ValueError("Coordinates cannot be negative!")
                    if int(x) >= int(configs.get("width", -1)) or int(
                        y
                    ) >= int(configs.get("height", -1)):
                        raise ValueError(
                            "Coordinates cannot be outside of "
                            + "the maze borders!"
                        )
                    configs["entry.x"] = int(x)
                    configs["entry.y"] = int(y)
                else:
                    raise ValueError("Entry is defined multiple times!")
            elif key == "exit":
                if (
                    configs.get("exit.x") is None
                    and configs.get("exit.y") is None
                ):
                    if "," not in val:
                        raise ValueError("Expected entry in this format: x,y")
                    x, y = map(str.strip, val.split(",", 1))
                    if int(x) < 0 or int(y) < 0:
                        raise ValueError("Coordinates cannot be negative!")
                    if int(x) >= int(configs.get("width", -1)) or int(
                        y
                    ) >= int(configs.get("height", -1)):
                        raise ValueError(
                            "Coordinates cannot be outside of "
                            + "the maze borders!"
                        )
                    configs["exit.x"] = int(x)
                    configs["exit.y"] = int(y)
                else:
                    raise ValueError("Exit is defined multiple times!")
            elif key == "perfect":
                if configs.get("perfect") is None:
                    if val not in ["true", "false"]:
                        raise ValueError(
                            'Perfect needs to be either "True" or "False"'
                        )
                    configs["perfect"] = val == "true"
                else:
                    raise ValueError("Perfect is defined multiple times!")
            elif key == "output_file":
                configs["output_file"] = str(val)
            elif key == "seed":
                if val == "":
                    val = "-1"
                try:
                    seed_val = int(val)
                    if seed_val < 0 or seed_val > 2147483647:
                        seed_val = -1
                    configs["seed"] = seed_val
                except Exception:
                    raise ValueError(
                        "I'm too lazy to support multiple seed "
                        + "datatypes, so please stick with "
                        + "signed 32-bit integers"
                    )
            elif key == "algorithm":
                if val not in ["wilson", "dfs"]:
                    raise ValueError(
                        f"{val.capitalize()} is not a valid "
                        + "algorithm, please use a valid algorithm"
                    )
                configs["algorithm"] = val
            else:
                raise KeyError(
                    f"{key.capitalize()} is not a valid key, "
                    + "please remove it from the config file"
                )
    if set(configs.keys()).intersection(required) != required:
        raise ValueError(
            "width, height, entry and exit must be defined in the config file"
        )
    if configs.get("output_file") is None or configs.get("output_file") == "":
        configs["output_file"] = "output.txt"
    if configs.get("algorithm") is None or configs.get("algorithm") == "":
        configs["algorithm"] = "dfs"
    if configs.get("seed") is None or configs.get("seed") == "":
        configs["seed"] = -1
    if configs.get("perfect") is None or configs.get("perfect") == "":
        configs["perfect"] = False
    return configs
