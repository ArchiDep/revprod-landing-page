"""Configuration of the landing page, read from environment variables."""

from collections.abc import Mapping
from dataclasses import dataclass

LOG_LEVELS = ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG")


class ConfigError(Exception):
    """An environment variable has an invalid value."""


@dataclass(frozen=True)
class Config:
    host: str
    port: int
    log_level: str
    title: str
    backend_base_url: str


def load_config(environ: Mapping[str, str]) -> Config:
    """
    Read the configuration from environment variables, using a default value for
    each variable that is not set.
    """
    return Config(
        host=environ.get("REVPROD_LISTEN_HOST", "0.0.0.0"),
        port=_parse_port(environ, "REVPROD_LISTEN_PORT", 3000),
        log_level=_parse_log_level(environ, "REVPROD_LOG_LEVEL", "INFO"),
        title=environ.get("REVPROD_TITLE", "The Revolutionary Product"),
        # The pages append paths such as "/share", which must not start with
        # two slashes.
        backend_base_url=environ.get("REVPROD_BACKEND_BASE_URL", "").rstrip("/"),
    )


def _parse_port(environ: Mapping[str, str], name: str, default: int) -> int:
    value = environ.get(name)
    if value is None:
        return default

    try:
        port = int(value)
    except ValueError:
        port = None

    if port is None or not 1 <= port <= 65_535:
        raise ConfigError(
            f"${name} must be an integer between 1 and 65535, "
            f"but its value is {value!r}"
        )

    return port


def _parse_log_level(environ: Mapping[str, str], name: str, default: str) -> str:
    value = environ.get(name)
    if value is None:
        return default

    level = value.upper()
    if level not in LOG_LEVELS:
        allowed = ", ".join(LOG_LEVELS)
        raise ConfigError(
            f"${name} must be one of {allowed}, but its value is {value!r}"
        )

    return level
