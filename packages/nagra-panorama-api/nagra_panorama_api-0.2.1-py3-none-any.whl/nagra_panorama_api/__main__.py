import logging

from nagra_network_misc_utils.logger import set_default_logger

from .commands import cli

set_default_logger()
logging.getLogger().setLevel(logging.INFO)

if __name__ == "__main__":
    cli()
