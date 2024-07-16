import pathlib

from mksite import config, renderer


def test_render_content():
    cfg = config.Config(
        base="https://mksite.com",
        lang="en-us",
        directories=config.Directories(content="content", static="static"),
        nav=[config.NavItem("home", "/")],
    )
    homepage = pathlib.Path(__file__).parent / "example/content/index.md"

    got = renderer.render_content(cfg=cfg, content=[homepage], static=["style.css"])
    want = [
        renderer.RenderedPage(
            target="index",
            html='<!doctype html><html lang="en-us"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><meta http-equiv="x-ua-compatible" content="ie=edge"/><link rel="stylesheet" href="/static/style.css"/></head><body><nav><a href="/">home</a></nav><h1>Hello, world</h1><p>This is a web page.</p></body></html>',  # noqa: E501
        ),
    ]

    assert got == want


def test_store_rendered_page(tmp_path):
    rp = renderer.RenderedPage(target="blog/post", html="<html>Hi!</html>")
    public = tmp_path / "public"
    rp.store(public)

    got = (public / "blog/post/index.html").read_text()
    want = "<html>Hi!</html>"

    assert got == want
