"""
This example will download and install the latest version of the software.

Python requirements:
- ping3
"""

import logging
from datetime import datetime
from multiprocessing.pool import ThreadPool

import click

# from ping3 import ping  # Ping
import nagra_panorama_api
from nagra_panorama_api.xmlapi.utils import etree_tostring

from .common import ensure_group_load, ensure_output_directory
from .utils import get_logger, getenv, slugify

# set_default_logger()
logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().setLevel(logging.DEBUG)


################################################################################


DEFAULT_PREFIX = "scripted"


def dump_states_worker(args):
    try:
        (
            fw_name,
            fw_host,
            apikey,
            save,
            prefix,
            output,
        ) = args

        logger = get_logger(f"Device {fw_name}")

        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        snapshot_name = f"{prefix}_{now}"

        client = nagra_panorama_api.XMLApi(fw_host, apikey, logger=logger)
        if save:
            save_response = client.save_config(snapshot_name)
            logger.info(f"Saved result: {save_response}")
        if not output:
            return True

        fw_output_dir = output / fw_name
        fw_output_dir.mkdir(parents=True, exist_ok=True)

        config_file = fw_output_dir / f"{prefix}_config_{now}.xml"
        if save:
            configuration = etree_tostring(
                client.get_named_configuration(snapshot_name)
            ).decode()
        else:
            configuration = client.export_configuration().decode()
        with config_file.open("w") as f:
            f.write(configuration)
        logger.info(f"Configuration saved here: {config_file}")

        state_file = fw_output_dir / f"{prefix}_state_{now}.tgz"
        state = client.export_device_state()
        with state_file.open("wb") as f:
            f.write(state)
        logger.info(f"State saved here: {config_file}")
        return True

    except Exception as e:
        logger.error(f"""An unexpected error occured\n{e}""")
        # raise e
        logger.debug(f"Worker args: {args}")
        return False


@click.command(
    "dump-states",
    help="Dump the configuration and device-state of a group of devices",
)
@click.argument(
    "file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    # help="Configuration file containing the upgrade groups"
)
@click.argument("group")  # help="Upgrade group from the configuration to run"
@click.option(
    "--apikey",
    help="Panorama & Firewall api key (must be the same for both). Use one of the following environment variables: PANORAMA_APIKEY, PANO_APIKEY",
)
@click.option("--save/--no-save", default=True)
@click.option("--prefix", help="Prefix for the configuration/state snapshots")
@click.option(
    "--output",
    default="./confdumps",
    help="Destination folder where to put the downloaded files",
)
def dump_states_cmd(file, group, apikey, save, prefix, output):
    if prefix:
        prefix = slugify(prefix)
    if not prefix:
        prefix = DEFAULT_PREFIX
    if len(prefix) > 12:
        logging.error(
            f"Prefix cannot be longer than 12 caracters. Current prefix: '{prefix}'"
        )
    if not apikey:
        apikey = getenv("PANORAMA_APIKEY", "PANO_APIKEY")
    output = ensure_output_directory(output, group)
    if not output and not save:
        logging.warning("No output nor configuration save requested. Nothing to do")
        exit()
    group_data = ensure_group_load(file, group)

    devices = group_data["devices"]

    pool_data = [
        (
            d["hostname"],
            d["ip_address"],
            apikey,
            save,
            prefix,
            output,
        )
        for d in devices
    ]
    failed = 0
    with ThreadPool(len(pool_data)) as pool:
        for i, upgrade_res in enumerate(
            pool.imap_unordered(dump_states_worker, pool_data), 1
        ):
            logging.info(f"Dumped {i}/{len(pool_data)} configurations")
            if not upgrade_res:
                failed += 1
    if failed > 0:
        logging.error(f"There was {failed} failed upgrades")
    else:
        logging.info("All configuration/states were downloaded successfuly")
