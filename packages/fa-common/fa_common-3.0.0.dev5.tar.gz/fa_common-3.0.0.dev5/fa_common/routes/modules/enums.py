from enum import Enum


class ParamType(str, Enum):
    STRING = "str"
    LIST = "list"
    INT = "int"
    FLOAT = "float"
    ARRAY = "array"  # numpy array
    DATAFRAME = "dataframe"


class ModuleRunModes(str, Enum):
    """
    Module local run modes.
    """

    FUNC = "func"
    SUBPROCESS = "subprocess"
    VENV = "venv"
    CONTAINER = "container"


class ModuleVisibility(str, Enum):
    """Module visibility."""

    PRIVATE = "private"
    PUBLIC = "public"
    HIDDEN = "hidden"


class ModuleUsability(str, Enum):
    """Module visibility."""

    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"
    TEST = "test"


class ModuleType(str, Enum):
    """Module visibility."""

    IMAGE = "image"
    ZIP = "zip"
