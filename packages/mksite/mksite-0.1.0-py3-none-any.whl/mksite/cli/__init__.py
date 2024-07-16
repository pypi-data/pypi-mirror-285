import pathlib

import click

from mksite import config, parser, persistence, renderer
from mksite.__about__ import __version__

CONFIG_FILENAME = "config.toml"


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="mksite")
def mksite() -> None:
    """Control panel for building static sites."""


@mksite.command()
@click.option("--dir", type=str, default=".", help="Site directory.", show_default=True)
def build(dir: str) -> None:
    """Build the static website with 'config.toml'."""
    click.echo("Start building site…")

    cwd = pathlib.Path(dir)
    cfg = config.read_config(cwd / CONFIG_FILENAME)

    content_file_paths = parser.get_content_paths(cwd / cfg.directories.content)
    static_file_paths = parser.get_static_paths(cwd / cfg.directories.static)
    rendered_pages = renderer.render_content(cfg, content_file_paths, static_file_paths)

    persistence.write_to_filesystem(cfg, cwd, rendered_pages, static_file_paths)

    click.echo(f"Files written to {cfg.directories.public!r} directory.")
