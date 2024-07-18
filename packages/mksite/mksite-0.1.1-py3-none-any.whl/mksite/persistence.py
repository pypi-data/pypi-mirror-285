import pathlib
import shutil

from mksite import config, renderer


def write_to_filesystem(
    cfg: config.Config,
    cwd: pathlib.Path,
    rendered_pages: list[renderer.RenderedPage],
    static_files: list[str],
) -> None:
    """Store rendered pages into public directory."""
    public_dir = cwd / cfg.directories.public
    static_dir = public_dir / "static"

    static_dir.mkdir(parents=True, exist_ok=True)

    for rp in rendered_pages:
        rp.store(public_dir)

    for sf in static_files:
        src_static_fpath = cwd / cfg.directories.static / sf
        target_static_fpath = static_dir / sf
        shutil.copy(src_static_fpath, target_static_fpath)
