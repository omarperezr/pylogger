import os


class EnvVar:
    """A class for managing environment variables.

    This class provides methods for getting and setting environment variables.

    Attributes:
        name (str): The name of the environment variable.
        default_value (str): The value of the environment variable.

    Methods:
        __init__(self, name: str, new_value: Any = None) -> None: Initializes the EnvVar object.
        __str__(self) -> str: Returns the value of the environment variable.
        set(self) -> str: Sets the value of the environment variable.
    """

    __UNSET__ = "UNSET"

    def __init__(self, name: str, default_value: str = __UNSET__) -> None:
        self.name: str = name
        self.value: str = os.environ.get(name, default_value)

    def __str__(self) -> str:
        return os.environ.get(self.name, self.value)

    def set(self) -> str:
        os.environ[self.name] = self.value
        return self.value
