from http import HTTPStatus

import pytest

from revprod_landing.config import Config
from revprod_landing.pages import render, render_error, render_index


def make_config(**overrides):
    values = {
        "host": "127.0.0.1",
        "port": 4201,
        "log_level": "INFO",
        "title": "The Revolutionary Product",
        "backend_base_url": "http://revprod-backend.example.com",
    }
    values.update(overrides)
    return Config(**values)


def test_index_links_to_the_backend():
    page = render_index(make_config())

    assert '<body data-backend-base-url="http://revprod-backend.example.com">' in page
    assert page.count('href="http://revprod-backend.example.com/share"') == 2


def test_index_links_to_the_same_origin_without_a_backend_base_url():
    page = render_index(make_config(backend_base_url=""))

    assert '<body data-backend-base-url="">' in page
    assert page.count('href="/share"') == 2


def test_index_shows_the_title():
    page = render_index(make_config(title="The Evolutionary Product"))

    assert "<title>The Evolutionary Product</title>" in page
    assert page.count("The Evolutionary Product") == 4


def test_index_has_no_placeholder_left():
    assert "{{" not in render_index(make_config())


def test_values_are_escaped():
    page = render_index(make_config(title='<Fish & "Chips">'))

    assert "<title>&lt;Fish &amp; &quot;Chips&quot;&gt;</title>" in page
    assert "<Fish" not in page


def test_error_page():
    page = render_error(make_config(), HTTPStatus.NOT_FOUND)

    assert "<title>The Revolutionary Product</title>" in page
    assert '<h1 class="mt-5 text-danger">Not Found</h1>' in page
    assert '<h2 class="mt-3">Code 404</h2>' in page
    assert "{{" not in page


def test_a_placeholder_without_a_value_is_an_error():
    with pytest.raises(KeyError) as error:
        render("error.html", title="The Revolutionary Product")

    assert error.value.args == ("No value for placeholder 'message' in error.html",)
