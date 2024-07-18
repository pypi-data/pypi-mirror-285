import dataclasses
import pathlib
import tomllib
from typing import Any

from . import exceptions


@dataclasses.dataclass(slots=True)
class Directories:
    """The directory names to crawl."""

    content: str
    """Name of the directory that holds template files."""
    static: str
    """Name of the directory that holds static files."""
    public: str = "public"
    """Name of target directory where rendered content will be persisted."""

    @classmethod
    def from_raw(cls, data: dict[str, Any]) -> "Directories":
        """Parse the raw dictionary provided by the TOML file."""
        return cls(
            content=str(data.get("content", "content")),
            static=str(data.get("static", "static")),
        )


@dataclasses.dataclass(slots=True)
class NavItem:
    """The nav items for the website."""

    name: str
    uri: str

    @classmethod
    def from_raw(cls, data: dict[str, Any]) -> "NavItem":
        return cls(name=data["name"], uri=data["uri"])


@dataclasses.dataclass(slots=True)
class Config:
    """The static site generator configuration."""

    base: str
    """The base url like 'https://mksite.com'"""
    lang: str
    """The language code of the website."""
    directories: Directories
    """The directories to crawl for files."""
    nav: list[NavItem]

    @classmethod
    def from_raw(cls, data: dict[str, Any]) -> "Config":
        """Parse the raw dictionary provided by the TOML file."""
        try:
            return cls(
                base=str(data["base"]),
                lang=str(data["lang"]),
                directories=Directories.from_raw(data.get("directories", {})),
                nav=[NavItem.from_raw(item) for item in data["nav"].get("items", [])],
            )
        except KeyError as err:
            raise exceptions.MissingConfigurationKeyError(str(err)) from err


def read_config(path: pathlib.Path) -> Config:
    """Read the configuration from the provided file path."""
    try:
        with path.open("rb") as f:
            return Config.from_raw(tomllib.load(f))
    except FileNotFoundError as err:
        raise exceptions.MissingConfigurationError(path) from err
