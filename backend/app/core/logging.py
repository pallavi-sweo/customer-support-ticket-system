import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    # Clean, readable structured-ish logs without external deps
    logger = logging.getLogger()
    logger.setLevel(level.upper())

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # Avoid duplicate handlers in reload
    if not logger.handlers:
        logger.addHandler(handler)
    else:
        logger.handlers[:] = [handler]
