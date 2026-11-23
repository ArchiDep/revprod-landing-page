"""Start the landing page: python3 -m revprod_landing"""

import errno
import logging
import os
import sys

from .config import ConfigError, load_config
from .server import LandingPageServer

logger = logging.getLogger("revprod_landing")


def main() -> int:
    try:
        config = load_config(os.environ)
    except ConfigError as error:
        print(error, file=sys.stderr)
        return 1

    logging.basicConfig(
        level=config.log_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    logger.info("Log level: %s", config.log_level)
    logger.info("Backend base URL: %s", config.backend_base_url or "none")

    try:
        server = LandingPageServer(config)
    except OSError as error:
        logger.error(_describe_listen_error(error, config.port))
        return 1

    with server:
        logger.info("Listening on %s:%d", config.host, config.port)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Stopped")

    return 0


def _describe_listen_error(error: OSError, port: int) -> str:
    if error.errno == errno.EACCES:
        return f"Port {port} requires elevated privileges"
    if error.errno == errno.EADDRINUSE:
        return f"Port {port} is already in use"
    return f"Could not listen on port {port}: {error}"


if __name__ == "__main__":
    sys.exit(main())
