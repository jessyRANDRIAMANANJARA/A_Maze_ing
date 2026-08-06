"""Parse and validate the maze configuration file (``config.txt``).

Reading happens in two passes: `_parse_raw` first collects every
``key = value`` line into a raw string dict (handling only line-level
syntax such as comments, duplicate keys and unknown keys), and
`read_config` then validates each mandatory/optional key in a fixed,
canonical order -- regardless of the order the keys actually appear in
the file -- so that error messages are always predictable.
"""

import sys


MANDATORY_KEYS: list[str] = [
    "width", "height", "entry", "exit", "perfect", "output_file",
]
OPTIONAL_KEYS: list[str] = ["seed", "algorithm"]
KNOWN_KEYS: set[str] = set(MANDATORY_KEYS) | set(OPTIONAL_KEYS)


def _parse_raw(config_file: str) -> dict[str, str]:
    """Read a config file into a raw ``{key: value}`` dict.

    Only handles line-level syntax (comments, blank lines, missing
    ``=``, unknown keys, duplicate keys). No value validation happens
    here so that later validation can be done in a fixed, predictable
    order instead of the order the lines happen to appear in the file.

    Inline comments are supported (e.g. ``entry = 8, 8  # top right``),
    but only when the ``#`` is separated from the value by whitespace.
    A ``#`` stuck directly onto a value (e.g. ``8#comment``) is treated
    as part of the value, not a comment.

    Parameters
    ----------
    config_file : str
        Path to the configuration file to read.

    Returns
    -------
    dict[str, str]
        Mapping of every recognized key found in the file to its raw,
        unvalidated string value.

    Raises
    ------
    ValueError
        If a non-comment line has no ``=``, or if a key is defined
        more than once.
    KeyError
        If a line declares a key that is not in `KNOWN_KEYS`.
    """
    raw: dict[str, str] = {}
    with open(config_file) as config:
        for line in config:
            line = line.strip().lower()
            if line.startswith("#") or line == "":
                continue
            hash_idx = line.find("#")
            if hash_idx > 0 and line[hash_idx - 1].isspace():
                line = line[:hash_idx].rstrip()
            if "=" not in line:
                raise ValueError("Non-Comments must be declarations with =")
            key, val = map(str.strip, line.split("=", 1))
            if key not in KNOWN_KEYS:
                raise KeyError(
                    f"{key.capitalize()} is not a valid key, "
                    + "please remove it from the config file"
                )
            if key in raw:
                raise ValueError(f"{key.capitalize()} is defined multiple times!")
            raw[key] = val
    return raw


def _validate_width(raw: dict[str, str], configs: dict[str, str | int | bool]) -> None:
    """Validate the ``width`` key and store it in `configs`.

    Parameters
    ----------
    raw : dict[str, str]
        Raw config values collected by `_parse_raw`.
    configs : dict[str, str | int | bool]
        Dict of parsed/validated config values, mutated in place.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If ``width`` is not strictly between 5 and 60.
    """
    val = raw["width"]
    if int(val) <= 5 or int(val) >= 60:
        raise ValueError(f"width must be at least 5 and less than 60 (got {val})")
    configs["width"] = val


def _validate_height(raw: dict[str, str], configs: dict[str, str | int | bool]) -> None:
    """Validate the ``height`` key and store it in `configs`.

    Parameters
    ----------
    raw : dict[str, str]
        Raw config values collected by `_parse_raw`.
    configs : dict[str, str | int | bool]
        Dict of parsed/validated config values, mutated in place.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If ``height`` is not strictly between 5 and 60.
    """
    val = raw["height"]
    if int(val) <= 5 or int(val) >= 60:
        raise ValueError(f"height must be at least 5 and less than 60 (got {val})")
    configs["height"] = val


def _validate_coordinates(
    label: str, val: str, configs: dict[str, str | int | bool]
) -> tuple[int, int]:
    """Parse and validate an ``x,y`` coordinate string.

    Parameters
    ----------
    label : str
        Human-readable name of the field being validated (``"entry"``
        or ``"exit"``), used in error messages.
    val : str
        Raw value to parse, expected in the form ``"x,y"``.
    configs : dict[str, str | int | bool]
        Dict of already-validated config values; must already contain
        valid ``"width"`` and ``"height"`` entries, used as the bounds
        the coordinate must fall within.

    Returns
    -------
    tuple[int, int]
        The parsed ``(x, y)`` coordinate.

    Raises
    ------
    ValueError
        If `val` is not comma-separated, contains negative
        coordinates, or falls outside the maze borders.
    """
    if "," not in val:
        raise ValueError(f"Expected {label} in this format: x,y")
    x, y = map(str.strip, val.split(",", 1))
    if int(x) < 0 or int(y) < 0:
        raise ValueError("Coordinates cannot be negative!")
    if int(x) >= int(configs["width"]) or int(y) >= int(configs["height"]):
        raise ValueError("Coordinates cannot be outside of the maze borders!")
    return int(x), int(y)


def _validate_entry(raw: dict[str, str], configs: dict[str, str | int | bool]) -> None:
    """Validate the ``entry`` key and store its coordinates in `configs`.

    Parameters
    ----------
    raw : dict[str, str]
        Raw config values collected by `_parse_raw`.
    configs : dict[str, str | int | bool]
        Dict of parsed/validated config values, mutated in place with
        ``"entry.x"`` and ``"entry.y"``.

    Returns
    -------
    None
    """
    x, y = _validate_coordinates("entry", raw["entry"], configs)
    configs["entry.x"] = x
    configs["entry.y"] = y


def _validate_exit(raw: dict[str, str], configs: dict[str, str | int | bool]) -> None:
    """Validate the ``exit`` key and store its coordinates in `configs`.

    Parameters
    ----------
    raw : dict[str, str]
        Raw config values collected by `_parse_raw`.
    configs : dict[str, str | int | bool]
        Dict of parsed/validated config values, mutated in place with
        ``"exit.x"`` and ``"exit.y"``.

    Returns
    -------
    None
    """
    x, y = _validate_coordinates("exit", raw["exit"], configs)
    configs["exit.x"] = x
    configs["exit.y"] = y


def _validate_perfect(raw: dict[str, str], configs: dict[str, str | int | bool]) -> None:
    """Validate the ``perfect`` key and store it as a bool in `configs`.

    Parameters
    ----------
    raw : dict[str, str]
        Raw config values collected by `_parse_raw`.
    configs : dict[str, str | int | bool]
        Dict of parsed/validated config values, mutated in place.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If ``perfect`` is not ``"true"`` or ``"false"``.
    """
    val = raw["perfect"]
    if val not in ["true", "false"]:
        raise ValueError('Perfect needs to be either "True" or "False"')
    configs["perfect"] = val == "true"


def _validate_output_file(
    raw: dict[str, str], configs: dict[str, str | int | bool]
) -> None:
    """Store the ``output_file`` key in `configs`.

    Parameters
    ----------
    raw : dict[str, str]
        Raw config values collected by `_parse_raw`.
    configs : dict[str, str | int | bool]
        Dict of parsed/validated config values, mutated in place.

    Returns
    -------
    None
    """
    configs["output_file"] = str(raw["output_file"])


def _validate_seed(raw: dict[str, str], configs: dict[str, str | int | bool]) -> None:
    """Validate the optional ``seed`` key and store it in `configs`.

    An empty or missing seed defaults to ``-1`` (random seed). A seed
    outside the signed 32-bit range is silently reset to ``-1`` instead
    of raising, since it simply means "use a random seed".

    Parameters
    ----------
    raw : dict[str, str]
        Raw config values collected by `_parse_raw`.
    configs : dict[str, str | int | bool]
        Dict of parsed/validated config values, mutated in place.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If ``seed`` is present but not a valid integer.
    """
    val = raw.get("seed", "")
    if val == "":
        val = "-1"
    try:
        seed_val = int(val)
        if seed_val < 0 or seed_val > 2147483647:
            seed_val = -1
        configs["seed"] = seed_val
    except ValueError:
        raise ValueError(
            "I'm too lazy to support multiple seed "
            + "datatypes, so please stick with "
            + "signed integers between 0 and 2147483647"
        )


def _validate_algorithm(
    raw: dict[str, str], configs: dict[str, str | int | bool]
) -> None:
    """Validate the optional ``algorithm`` key and store it in `configs`.

    Parameters
    ----------
    raw : dict[str, str]
        Raw config values collected by `_parse_raw`.
    configs : dict[str, str | int | bool]
        Dict of parsed/validated config values, mutated in place.
        Defaults to ``"dfs"`` when the key is absent or empty.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If ``algorithm`` is present but not ``"dfs"`` or ``"wilson"``.
    """
    val = raw.get("algorithm", "")
    if val == "":
        configs["algorithm"] = "dfs"
        return
    if val not in ["wilson", "dfs"]:
        raise ValueError(
            f"{val.capitalize()} is not a valid "
            + "algorithm, please use a valid algorithm"
        )
    configs["algorithm"] = val


_mandatory_validators = {
    "width": _validate_width,
    "height": _validate_height,
    "entry": _validate_entry,
    "exit": _validate_exit,
    "perfect": _validate_perfect,
    "output_file": _validate_output_file,
}


def read_config(config_file: "str") -> dict[str, str | int | bool]:
    """Parse a configuration file and validate all required fields.

    Missing mandatory keys are reported together in a single message
    (instead of failing on the first one found), and value validation
    always proceeds in the fixed order defined by `MANDATORY_KEYS`,
    regardless of how the keys are ordered in the file itself.

    Parameters
    ----------
    config_file : str
        Path to the configuration file to read.

    Returns
    -------
    dict[str, str | int | bool]
        Fully parsed and validated configuration, keyed by
        ``"width"``, ``"height"``, ``"entry.x"``, ``"entry.y"``,
        ``"exit.x"``, ``"exit.y"``, ``"perfect"``, ``"output_file"``,
        ``"seed"`` and ``"algorithm"``.

    Raises
    ------
    ValueError, KeyError
        Propagated from `_parse_raw` or from any of the per-key
        validators if a value is malformed.

    SystemExit
        If one or more mandatory keys are missing from the file
        (exits with status 1 after printing a unified error message).
    """
    raw = _parse_raw(config_file)

    missing = [key for key in MANDATORY_KEYS if raw.get(key, "") == ""]
    if missing:
        print(
            "Error: missing mandatory key(s) in config file: "
            + ", ".join(missing)
        )
        sys.exit(1)

    configs: dict[str, str | int | bool] = {}
    for key in MANDATORY_KEYS:
        _mandatory_validators[key](raw, configs)

    _validate_seed(raw, configs)
    _validate_algorithm(raw, configs)

    return configs
