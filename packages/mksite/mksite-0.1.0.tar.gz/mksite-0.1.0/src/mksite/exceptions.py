import pathlib


class MissingConfigurationError(Exception):
    """Raised when TOML configuration is missing."""

    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(f"Missing configuration: {path.name!r}.")


class MissingConfigurationKeyError(Exception):
    """Raised when a key is missing in the TOML configuration."""

    def __init__(self, key: str) -> None:
        super().__init__(f"Missing {key} key in configuration.")
