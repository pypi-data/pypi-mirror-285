# mksite

---

[![builds.sr.ht status](https://builds.sr.ht/~loges/mksite.svg)](https://builds.sr.ht/~loges/mksite?)
[![PyPI - Version](https://img.shields.io/pypi/v/mksite.svg)](https://pypi.org/project/mksite)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

> like mkdir but for websites

`mksite` helps you to quickly generate static websites with markdown.

## Installation

```console
pip install mksite
```

## Quickstart

Create site directory structure and change into `site` directory:

```console
mkdir -p site/content site/static
cd site
```

Add some site files:

```console
echo "<h1>Hello, world!</h1>" > content/index.md
echo "h1 {color: darkblue;}" > static/style.css
```

Add `config.toml` inside `site` directory:

```toml
base = "https://mksite.com"
lang = "en-us"

[directories]
content = "content"
static = "static"

[nav]
[[nav.items]]
name = "home"
uri = "/"
```

Build static site using `mksite` CLI:

```console
mksite build
```

Serve website using Python's http server:

```console
python -m http.server -d public 8000
```

Navigate to port [8000](http://localhost:8000).

## License

`mksite` is distributed under the terms of the [AGPLv3](https://spdx.org/licenses/AGPL-3.0-or-later.html) license.
