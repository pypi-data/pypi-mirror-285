import pathlib
import shutil

import pytest

from mksite import config, persistence, parser, renderer


@pytest.fixture
def cwd():
    cwd = pathlib.Path(__file__).parent / "example"
    yield cwd

    # clean up generated files
    shutil.rmtree(cwd / "public")


def test_write_to_filesystem(cwd):
    cfg = config.read_config(cwd / "config.toml")
    static_files = parser.get_static_paths(cwd / "static")
    content_files = parser.get_content_paths(cwd / "content")
    rendered_pages = renderer.render_content(cfg, content_files, static_files)
    persistence.write_to_filesystem(cfg, cwd, rendered_pages, static_files)

    checks = [
        (cwd / "public/index.html").exists(),
        (cwd / "public/contact/index.html").exists(),
        (cwd / "public/blog/post/index.html").exists(),
        (cwd / "public/blog/index.html").exists(),
        (cwd / "public/static/style.css").exists(),
    ]

    assert all(checks)
