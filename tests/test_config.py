import pytest

from revprod_landing.config import Config, ConfigError, load_config


def test_defaults():
    assert load_config({}) == Config(
        host="0.0.0.0",
        port=3000,
        log_level="INFO",
        title="The Revolutionary Product",
        backend_base_url="",
    )


def test_every_variable_set():
    environ = {
        "REVPROD_LISTEN_HOST": "127.0.0.1",
        "REVPROD_LISTEN_PORT": "4201",
        "REVPROD_LOG_LEVEL": "DEBUG",
        "REVPROD_TITLE": "The Evolutionary Product",
        "REVPROD_BACKEND_BASE_URL": "http://revprod-backend.example.com",
    }

    assert load_config(environ) == Config(
        host="127.0.0.1",
        port=4201,
        log_level="DEBUG",
        title="The Evolutionary Product",
        backend_base_url="http://revprod-backend.example.com",
    )


def test_log_level_is_case_insensitive():
    assert load_config({"REVPROD_LOG_LEVEL": "warning"}).log_level == "WARNING"


def test_trailing_slashes_are_removed_from_the_backend_base_url():
    environ = {"REVPROD_BACKEND_BASE_URL": "http://revprod-backend.example.com/"}

    assert load_config(environ).backend_base_url == "http://revprod-backend.example.com"


@pytest.mark.parametrize("value", ["", "abc", "42.5", "0", "65536", "-1"])
def test_invalid_port(value):
    with pytest.raises(ConfigError) as error:
        load_config({"REVPROD_LISTEN_PORT": value})

    assert str(error.value) == (
        "$REVPROD_LISTEN_PORT must be an integer between 1 and 65535, "
        f"but its value is {value!r}"
    )


@pytest.mark.parametrize("value", ["1", "65535"])
def test_port_limits(value):
    assert load_config({"REVPROD_LISTEN_PORT": value}).port == int(value)


def test_invalid_log_level():
    with pytest.raises(ConfigError) as error:
        load_config({"REVPROD_LOG_LEVEL": "TRACE"})

    assert str(error.value) == (
        "$REVPROD_LOG_LEVEL must be one of CRITICAL, ERROR, WARNING, INFO, DEBUG, "
        "but its value is 'TRACE'"
    )
