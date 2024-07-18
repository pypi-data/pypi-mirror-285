import pathlib

from mksite import parser


def test_get_content_paths():
    dir = pathlib.Path(__file__).parent / "example/content"

    got = parser.get_content_paths(dir)
    want = [
        pathlib.Path(__file__).parent / "example/content/contact.md",
        pathlib.Path(__file__).parent / "example/content/index.md",
        pathlib.Path(__file__).parent / "example/content/blog/index.md",
        pathlib.Path(__file__).parent / "example/content/blog/post.md",
    ]

    assert got == want


def test_get_static_paths():
    dir = pathlib.Path(__file__).parent / "example/static"

    got = parser.get_static_paths(dir)
    want = ["style.css"]

    assert got == want
