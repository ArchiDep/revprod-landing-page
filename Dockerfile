# syntax=docker/dockerfile:1

# Test
# ====
# The application needs nothing but Python, but its tests need pytest, installed
# with uv. The code is the same on every architecture, so it is tested once, on
# the builder's own, even for an image of another architecture.
FROM --platform=$BUILDPLATFORM python:3.14.7-slim-trixie AS test

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /usr/local/bin/

# Use the image's Python rather than download one, and copy the packages into
# the virtual environment, since the cache is not part of the image.
ENV UV_PYTHON=python3 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy

WORKDIR /build

# Installs the test dependencies before copying the code, so that a change to
# the code alone reuses this layer. The cache keeps uv's downloads between local
# builds.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY revprod_landing ./revprod_landing/
COPY tests ./tests/

# A failing test stops the build. The bytecode is then compiled, since the user
# the application runs as cannot write it next to the code at run time. It is
# the same on every architecture, and checked against a hash of the code rather
# than its modification time, which copying it may change.
RUN uv run --locked --no-sync pytest && \
    python3 -m compileall -q -f --invalidation-mode checked-hash revprod_landing

# Runtime
# =======
FROM python:3.14.7-slim-trixie

RUN useradd --system --no-create-home --shell /usr/sbin/nologin revprod

# The code that was tested. Owned by root, so the user the application runs as
# cannot replace it.
COPY --from=test /build/revprod_landing /revprod-landing-page/revprod_landing/

WORKDIR /revprod-landing-page

# Writes the logs as they come rather than in blocks.
ENV PYTHONUNBUFFERED=1

USER revprod

EXPOSE 3000

# The image has neither wget nor curl.
HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python3", "-c", "import os, urllib.request; urllib.request.urlopen(f\"http://127.0.0.1:{os.environ.get('REVPROD_LISTEN_PORT', '3000')}/health\", timeout=4)"]

# Python does not stop on SIGTERM when it is the container's first process,
# whose signals have no default action: Docker would wait, then kill it. SIGINT
# raises KeyboardInterrupt instead, which the application handles by stopping.
STOPSIGNAL SIGINT

CMD ["python3", "-m", "revprod_landing"]
