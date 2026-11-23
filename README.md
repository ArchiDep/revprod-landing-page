# The Revolutionary Product - Landing Page

Landing page for The Revolutionary Product, a multi-component web application to
illustrate [CORS](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing)
and [reverse proxying](https://en.wikipedia.org/wiki/Reverse_proxy).

[![build](https://github.com/ArchiDep/revprod-landing-page/actions/workflows/build.yml/badge.svg)](https://github.com/ArchiDep/revprod-landing-page/actions/workflows/build.yml)
[![license](https://img.shields.io/github/license/ArchiDep/revprod-landing-page)](https://opensource.org/licenses/MIT)

The landing page displays the testimonials it fetches from the [revprod
backend][backend].

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Requirements](#requirements)
- [Run the application](#run-the-application)
- [Configuration](#configuration)
- [Development](#development)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Requirements

- [Python][python] 3.12 or later

The application uses only Python's standard library: there is nothing to
install besides Python itself.

## Run the application

```bash
# Clone and move into the repository
git clone https://github.com/ArchiDep/revprod-landing-page.git
cd revprod-landing-page

# Run the application
REVPROD_BACKEND_BASE_URL=https://revprod-backend.example.com python3 -m revprod_landing
```

## Configuration

The application can be configured using the following environment variables:

| Variable                   | Default value               | Description                                                                                    |
| :------------------------- | :-------------------------- | :--------------------------------------------------------------------------------------------- |
| `REVPROD_BACKEND_BASE_URL` | -                           | The public URL at which the revprod backend can be accessed.                                   |
| `REVPROD_LISTEN_HOST`      | `0.0.0.0`                   | The IP address to listen to (use `0.0.0.0` for any IP address).                                |
| `REVPROD_LISTEN_PORT`      | `3000`                      | The port to listen on.                                                                         |
| `REVPROD_TITLE`            | `The Revolutionary Product` | The title displayed in the navbar.                                                             |
| `REVPROD_LOG_LEVEL`        | `INFO`                      | The lowest level of log messages to output: `DEBUG`, `INFO`, `WARNING`, `ERROR` or `CRITICAL`. |

Without `REVPROD_BACKEND_BASE_URL`, the landing page fetches the testimonials
from its own origin, which works when a reverse proxy serves both components
under the same domain.

## Development

Development requires these tools, in the versions listed in
[`.tool-versions`](.tool-versions), which [asdf][asdf] can install with
`asdf install`:

- [Python][python], to run the application.
- [uv][uv], to install pytest and Ruff, the development dependencies declared in
  [`pyproject.toml`](pyproject.toml) and locked in [`uv.lock`](uv.lock).
- [Node.js][node], to run [Prettier][prettier] and [doctoc][doctoc].

The [`Makefile`](Makefile) installs the dependencies each target needs:

```bash
# Run every check: table of contents, formatting, linting, tests
make

# Run the application, with the settings in .env if there is one (see
# .env.sample)
make run

# Run the automated tests
make test

# Format the code: Python with Ruff, the rest with Prettier
make format

# Update the table of contents of this README
make doctoc
```

[asdf]: https://asdf-vm.com
[backend]: https://github.com/ArchiDep/revprod-backend
[doctoc]: https://github.com/thlorenz/doctoc
[node]: https://nodejs.org
[prettier]: https://prettier.io
[python]: https://www.python.org
[uv]: https://docs.astral.sh/uv/
