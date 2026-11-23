"""Rendering of the HTML pages from the templates."""

import html
import re
from http import HTTPStatus
from pathlib import Path

from .config import Config

TEMPLATES_DIR = Path(__file__).parent / "templates"

# A placeholder such as "{{ title }}". Templates cannot use Python's
# string.Template, whose "$" placeholders clash with the page's jQuery code.
_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render_index(config: Config) -> str:
    """Render the landing page."""
    return render(
        "index.html",
        title=config.title,
        backend_base_url=config.backend_base_url,
    )


def render_error(config: Config, status: HTTPStatus) -> str:
    """Render the error page for an HTTP status."""
    return render(
        "error.html",
        title=config.title,
        message=status.phrase,
        status=str(status.value),
    )


def render(template_name: str, **values: str) -> str:
    """
    Render a template, replacing each placeholder with its HTML-escaped value.
    Every placeholder in the template must have a value.
    """
    template = (TEMPLATES_DIR / template_name).read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in values:
            raise KeyError(f"No value for placeholder {name!r} in {template_name}")

        return html.escape(values[name])

    return _PLACEHOLDER.sub(replace, template)
