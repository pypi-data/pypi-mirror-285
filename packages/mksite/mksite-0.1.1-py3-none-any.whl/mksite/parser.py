import pathlib


def get_content_paths(dir: pathlib.Path) -> list[pathlib.Path]:
    """Get a dictionary of paths from content directory."""
    return [p for p in dir.rglob("*") if p.is_file()]


def get_static_paths(dir: pathlib.Path) -> list[str]:
    """Get a list of paths from static directory."""
    return [d.name for d in dir.glob("*")]
