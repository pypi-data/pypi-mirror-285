import dataclasses
import pathlib

import haitch as H
import mistletoe as md

from .config import Config


@dataclasses.dataclass(slots=True)
class RenderedPage:
    """Data container for html rendered content."""

    target: str
    """Target path for rendered html."""
    html: str
    """Fully rendered html page."""

    def store(self, public: pathlib.Path) -> None:
        """Persist html to public target directory."""
        if "index" in self.target:
            target_path = public / f"{self.target}.html"
        else:
            target_path = public / self.target / "index.html"

        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(self.html)


def render_content(
    cfg: Config, content: list[pathlib.Path], static: list[str]
) -> list[RenderedPage]:
    """Renders list of page paths to a list of rendered html containers."""
    rendered_pages = []

    with md.HtmlRenderer() as renderer:
        for path in content:
            rendered_markdown = render_markdown(renderer, path)
            built_page = build_page(cfg, rendered_markdown, static)
            _, raw_target = str(path).split(cfg.directories.content)
            target = raw_target.lstrip("/").rstrip(".md")
            rendered_pages.append(RenderedPage(target, built_page))

    return rendered_pages


def render_markdown(renderer: md.HtmlRenderer, path: pathlib.Path) -> str:
    """Renders the markdown file's content to html replacing newlines."""
    raw_content: str = renderer.render(md.Document(path.read_text()))
    return raw_content.replace("\n", "")


def build_page(cfg: Config, content: str, static: list[str]) -> str:
    """Build full web page based on configuration and passed content."""
    links = [
        H.link(rel="stylesheet", href=f"/static/{item}")
        for item in static
        if ".css" in item
    ]
    scripts = [H.script(src=item) for item in static if ".js" in item]

    built_page = H.html5(
        content=H.fragment(
            H.nav(H.a(href=item.uri)(item.name) for item in cfg.nav),
            H.unsafe(content),
        ),
        language_code=cfg.lang,
        links=links,
        scripts=scripts,
    )

    return str(built_page)
