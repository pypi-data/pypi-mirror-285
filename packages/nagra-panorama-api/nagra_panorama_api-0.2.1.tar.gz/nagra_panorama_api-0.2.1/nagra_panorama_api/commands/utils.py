"""
This example will download and install the latest version of the software.

Python requirements:
- ping3
"""

import logging
import os
import re
from pathlib import Path

# from nagra_network_misc_utils.logger import set_default_logger
from rich.logging import RichHandler

# set_default_logger()
logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().setLevel(logging.DEBUG)

SLUGIFY_REG = re.compile("\w+")


def slugify(name, join="_"):
    return join.join(SLUGIFY_REG.findall(name.strip().lower()))


def getenv(*varnames, exit_on_failure=True, default=None):
    for var in varnames:
        val = os.environ.get(var)
        if val is not None:
            return val.strip()
    logging.error(
        f"None of the following environment variables are defined: {', '.join(varnames)}"
    )
    if exit_on_failure:
        exit(1)
    return default


# %(asctime)s - %(name)s - %(levelname)s - %(message)s
DEFAULT_LOGGER_FORMAT = "[%(levelname)s] %(message)s"

LOGGER_REGISTRY = {}


def get_logger(name, file=None, level=logging.INFO):
    global LOGGER_REGISTRY
    logger = LOGGER_REGISTRY.get(name)
    if logger is not None:
        return logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent calling the root logger
    logger.handlers.clear()
    formatter = logging.Formatter(DEFAULT_LOGGER_FORMAT)
    if file is not None:
        file = Path(file).resolve()
        file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file, mode="w")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    stream_handler = RichHandler()
    logger.addHandler(stream_handler)
    LOGGER_REGISTRY[name] = logger
    return logger
