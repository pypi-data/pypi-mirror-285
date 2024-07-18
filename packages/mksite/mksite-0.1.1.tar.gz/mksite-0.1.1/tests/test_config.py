import pathlib

import pytest

from mksite import config, exceptions


def test_read_config():
    fpath = pathlib.Path(__file__).parent / "example/config.toml"

    got = config.read_config(fpath)
    want = config.Config(
        base="https://mksite.com",
        lang="en-us",
        directories=config.Directories(
            content="content",
            static="static",
        ),
        nav=[config.NavItem("home", "/"), config.NavItem("contact", "/contact")],
    )

    assert got == want


def test_read_config_with_defaults():
    fpath = pathlib.Path(__file__).parent / "example/defaults.toml"

    got = config.read_config(fpath)
    want = config.Config(
        base="https://mksite.com",
        lang="en-us",
        directories=config.Directories(
            content="content",
            static="static",
        ),
        nav=[config.NavItem("home", "/"), config.NavItem("contact", "/contact")],
    )

    assert got == want


def test_read_config_broken():
    fpath = pathlib.Path(__file__).parent / "example/broken.toml"

    with pytest.raises(
        exceptions.MissingConfigurationKeyError,
        match="Missing 'lang' key in configuration.",
    ):
        config.read_config(fpath)


def test_read_config_missing():
    fpath = pathlib.Path(__file__).parent / "example/missing.toml"

    with pytest.raises(
        exceptions.MissingConfigurationError,
        match="Missing configuration: 'missing.toml'",
    ):
        config.read_config(fpath)
