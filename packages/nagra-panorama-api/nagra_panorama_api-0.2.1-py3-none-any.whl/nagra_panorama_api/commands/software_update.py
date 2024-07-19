"""
This example will download and install the latest version of the software.

Python requirements:
- ping3
"""

import logging
from multiprocessing.pool import ThreadPool
from pathlib import Path
from typing import List, Optional

import click
import requests
import urllib3
import yaml

# from nagra_network_misc_utils.logger import set_default_logger
# from ping3 import ping  # Ping
import nagra_panorama_api
from nagra_panorama_api.utils import first
from nagra_panorama_api.xmlapi.utils import wait

from .common import DEFAULT_OUTPUT_DIRECTOR, ensure_group_load, ensure_output_directory
from .utils import get_logger, getenv

# set_default_logger()
logging.getLogger().setLevel(logging.INFO)
# logging.getLogger().setLevel(logging.DEBUG)


def wait_availability(client, fw_host, logger=None):
    if logger is None:
        logger = logging
    logger.info(f"Checking firewall '{fw_host}' availability. Waiting for response...")
    for _ in wait():
        try:
            versions = client.get_versions()
            current = next(v for v in versions if v.current)
            if current is None:
                logger.warning("Device is not not answering")
            else:
                return current
        except (urllib3.exceptions.MaxRetryError, requests.exceptions.ConnectionError):
            logger.warning(f"Firewall {fw_host} is still not responding")
        except Exception as e:
            logger.debug(
                f"Unexpected error of type {type(e)} occured on firewall {fw_host}"
            )
            logger.error(f"Firewall {fw_host} is still not responding: {e}")
    raise Exception(f"Timeout while waiting for availability of firewall {fw_host}")


def check_availability(client, fw_host, logger=None):
    if logger is None:
        logger = logging
    ## Wait for the FW to respond
    version = wait_availability(client, fw_host, logger=logger)
    if not version:
        logger.error(f"Device {fw_host} never responded")
        return False
    logger.info(f"Firewall {fw_host} is available")
    return True


def check_panorama_connection(panorama_client, fw_host, logger=None):
    if logger is None:
        logger = logging
    ## Check that the device is connected to Panorama
    devices = panorama_client.get_devices()
    candidates = [d for d in devices if d.ip_address == fw_host]
    if len(candidates) > 1:
        serials = ", ".join(c.serial for c in candidates)
        logger.warning(
            f"Device {fw_host} has {len(candidates)} serial number: {serials}"
        )
    if not candidates:
        logger.error(f"Device with IP {fw_host} is not detected AT ALL to panorama")
        return False
    if not any(c.connected for c in candidates):
        logger.error(
            f"Device with IP {fw_host} is not detected as connected to panorama"
        )
        return False
    logger.info(f"Firewall {fw_host} is detected has connected to panorama")
    return True


def run_checks(
    client,
    fw_host,
    panorama_client: Optional[nagra_panorama_api.XMLApi] = None,
    logger=None,
):
    if logger is None:
        logger = logging
    if not check_availability(client, fw_host, logger=logger):
        return False
    if panorama_client and not check_panorama_connection(
        panorama_client, fw_host, logger=logger
    ):
        return False
    return True


################################################################################
def get_ha_info_worker(args):
    (
        device,
        apikey,
    ) = args
    fw_name, fw_host = device["hostname"], device["ip_address"]
    try:
        client = nagra_panorama_api.XMLApi(fw_host, apikey)
        return device, client.get_ha_info()
    except Exception as e:
        logging.error(
            f"""\
An unexpected error occured on device {fw_name}:
{e}
"""
        )
        return None


def check_and_complete_data(panorama: nagra_panorama_api.XMLApi, devices: List[dict]):
    """
    This function check that all devices are connected to panorama.
    It also add the device information from panorama into the devices object.
    The devices dicts are updated in place and returned at the end of the function
    """
    errors = []
    panorama_devices = panorama.get_devices(connected=True)
    device_map = {d.ip_address: d for d in panorama_devices}
    errors = []
    for d in devices:
        panorama_data = device_map.get(d["fw_host"])
        if panorama_data is None:
            errors.append(d)
            continue
        d["panorama_data"] = panorama_data
    if errors:
        for d in errors:
            logging.error(
                f"Device {d['fw_name']} ({d['fw_host']}) is not connected to panorama"
            )
        exit(1)
    return devices


def check_ha_pairs(panorama, devices):
    """
    NB: This function need to be called after check_and_complete_data

    This function check if we are trying to update a device in an HA pair.
    If yes, it ensures that all devices in the HA pair are set for upgrade.

    """
    errors = []
    ha_pairs, without_ha = panorama.get_ha_pairs(connected=True)
    devices_map = {d["panorama_data"].serial: d for d in devices}
    for pair in ha_pairs:
        # Ensure that each pair contains exactly 2 devices
        if len(pair) != 2:
            members = (
                ", ".join(d.ip_address for d in pair)
                if pair
                else "(NO MEMBER -> Script bug)"
            )
            errors.append(
                f"""\
An HA pair doesn't have 2 active devices. Found members:
{members}
"""
            )
            continue
        # Ensure that we upgrade all devices in an HA pair
        member1, member2 = pair
        member1_found = member1.serial in devices_map
        member2_found = member2.serial in devices_map
        # If any member is found, ensure that member1 is the one found
        # Nb: This implies that
        # - if member1 is not found, none are found
        # - if member2 is found, both are found
        # - if they are not both found, member1 is the one found and member2 is not found
        if member2_found is True:
            member1_found, member2_found = member2_found, member1_found
            member1, member2 = member2, member1
        # If they are not both found/not found, there is an issue
        # Nb: member1 would necessarily be the one found in this situation
        if member1_found != member2_found:
            errors.append(
                f"Device {member1.ip_address} is part of an HA pair "
                f"but its peer {member2.ip_address} is not set for upgrade"
            )
    if errors:
        for e in errors:
            logging.error(e)
        exit(1)

    # Split the devices depending on their HA membership
    # and group the device from the same HA pair

    ha_pairs, without_ha = [], []
    devices_map = {d["panorama_data"].serial: d for d in devices}
    done = set()
    for d in devices:
        data = d["panorama_data"]
        serial = data.serial
        if serial in done:
            continue
        ha_peer_serial = data.ha_peer_serial
        if not ha_peer_serial:
            without_ha.append(d)
            done.add(serial)
            continue
        peer = devices_map.get(ha_peer_serial)
        ha_pairs.append((d, peer))
    return ha_pairs, without_ha


def upgrade_worker(device: dict):
    try:
        logger = device["logger"]
        panorama_host = device["panorama_host"]
        fw_name = device["fw_name"]
        fw_host = device["fw_host"]
        apikey = device["apikey"]
        version = device["version"]
        download_only = device["download_only"]
        test_only = device["test_only"]

        panorama_client = None
        if panorama_host:
            panorama_client = nagra_panorama_api.XMLApi(
                panorama_host, apikey, logger=logger
            )
        client = nagra_panorama_api.XMLApi(fw_host, apikey, logger=logger)

        fw_sys_info = client.system_info()
        serial_number = fw_sys_info.xpath(".//serial/text()")[0]
        current_version = fw_sys_info.xpath(".//sw-version/text()")[0]
        logger.info(
            f"Device with IP {fw_host} (S/N: {serial_number}) is currently on version '{current_version}'"
        )
        if not test_only:
            version = client.automatic_software_upgrade(
                version, install=(not download_only)
            )

        # Tests
        res = run_checks(
            client, fw_host, panorama_client=panorama_client, logger=logger
        )
        if download_only:
            logger.info(
                f"Done dowloading version { version.version } on device {fw_name} ({fw_host}) "
            )
        elif not test_only:
            logger.info(
                f"Done upgrading device {fw_name} ({fw_host}) to version { version.version }"
            )
        return res
    except Exception as e:
        logger.error(
            f"""\
An unexpected error occured
Worker args: {device}
{e}
"""
        )
        return False


def group_by_panorama(devices: List[dict]):
    def worker(device):
        fw_name = device["fw_name"]
        fw_host = device["fw_host"]
        apikey = device["apikey"]
        try:
            client = nagra_panorama_api.XMLApi(fw_host, apikey)
            panorama_ip = client.get_local_panorama_ip()
            return True, panorama_ip, device
        except Exception as e:
            logging.error(f"Couldn't find panorama server for device '{fw_name}':\n{e}")
        return True, None, device

    grouped = {}
    failed = []
    with ThreadPool(len(devices)) as pool:
        for success, panorama_ip, device in pool.imap_unordered(worker, devices):
            if not success:
                failed.append(device)
                continue
            device.setdefault("panorama_host", panorama_ip)
            g = grouped.setdefault(panorama_ip, [])
            g.append(device)
    if failed:
        failed_devices = ", ".join(
            sorted(f"{d['fw_name']} ({d['fw_host']})" for d in failed)
        )
        logging.error(
            f"Couldn't assess the Panorama server of the following devices: {failed_devices}"
        )
        # exit(1)  # Stop the upgrade ? Ask for continuation ?
    return grouped


def trim_text(text, max_len=100):
    line_end = "..."
    trim_len = max(max_len - len(line_end), 0)
    if len(text) > max_len:
        text = text[:trim_len] + line_end
    return text


@click.command(
    "upgrade",
    help="Upgrade a group of devices to a different softare version",
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
@click.option(
    "--download-only",
    is_flag=True,
    default=False,
    help="Only download the software version without installing it",
)
@click.option("--test-only", is_flag=True, default=False, help="Only runs the checks")
@click.option(
    "--logs-output",
    help=f"Destination folder where to put the logs (Default to {DEFAULT_OUTPUT_DIRECTOR})",
)
def upgrade_cmd(file, group, apikey, download_only, test_only, logs_output):
    if download_only and test_only:
        logging.error(
            "You cannot not use --download-only and --test-only flags at the same time"
        )
        exit(1)
    if not apikey:
        apikey = getenv("PANORAMA_APIKEY", "PANO_APIKEY")

    logs_output = ensure_output_directory(logs_output, group)
    group_data = ensure_group_load(file, group)

    if logs_output:
        generic_logs_file = logs_output / "main.log"
        generic_logs_file_handler = logging.FileHandler(generic_logs_file)
        # generic_logs_file_handler.setLevel(logging.DEBUG)  # Set the logging level for the file handler
        # Create a formatter and set it for the handler
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        generic_logs_file_handler.setFormatter(formatter)
        # Add the handler to the logger
        logging.getLogger().addHandler(generic_logs_file_handler)

    # panorama_ip = group_data["panorama_ip"]
    if "panorama_ip" in group_data:
        logging.warning("Entry 'panorama_ip' is deprecated and will be ignored")

    version = group_data.get("version")
    devices = group_data["devices"]

    # Transform the device lists:
    # - Simplify maintenance (e.g. renaming) and debuging
    # - make each device data self-contained
    devices = [
        {
            "group": group,
            "panorama_host": None,
            "panorama_data": None,  # See check_and_complete_data
            "fw_name": d["hostname"],
            "fw_host": d["ip_address"],
            "apikey": apikey,
            "version": version,
            "download_only": download_only,
            "test_only": test_only,
            "logs_output": logs_output,
        }
        for d in devices
    ]

    # Find panorama server associated to the devices (if there is one)
    panorama_ip = None
    grouped = group_by_panorama(devices)
    if len(grouped) > 1:
        statistics = "\n".join(
            f"""{panorama_server or '<no-server>'} => {len(devices)} ({trim_text(', '.join(d['fw_name'] for d in devices))})"""
            for panorama_server, devices in grouped.items()
        )
        logging.error(
            f"Devices in group {group} are associated to different panorama server:\n{statistics}"
        )

        exit(1)
    elif len(grouped) == 1:
        panorama_ip, devices = first(grouped.items())

    panorama = None
    if panorama_ip:
        panorama = nagra_panorama_api.XMLApi(panorama_ip, apikey)
    else:
        # TODO: Check the HA pair directly from the devices, not from panorama
        logging.warning(
            "No panorama host defined in configuration. Some features won't apply, like checking HA pairs"
        )
    if panorama:
        devices = check_and_complete_data(panorama, devices)

    for d in devices:
        fw_name = d["fw_name"]
        logfile = logs_output / fw_name if logs_output else None
        logger = get_logger(f"Device {fw_name}", logfile)
        d["logger"] = logger

    if panorama:
        ha_pairs, without_ha = check_ha_pairs(panorama, devices)

        devices = without_ha
        if ha_pairs and not (download_only or test_only):
            ha_pairs_textual_list = "\n".join(
                " - ".join(f"{d['fw_name']} ({d['fw_host']})" for d in pair)
                for pair in ha_pairs
            )
            logging.warning(
                f"Group {group} contains devices that are part of HA pairs."
                "The script cannot upgrade them at the moment and will ignore them.\n"
                "You can retry with flags --download-only or --test-only.\n"
                f"List of HA pairs found:\n{ha_pairs_textual_list}"
            )

    if not test_only:
        if not version:
            logging.warning(
                "version not defined, the script will default to the latest version for each devices"
            )
        else:
            logging.info(f"Starting upgrade to version {version}")

    if not devices:
        logging.info("No device to manage.")
        exit()

    operation, op_adj = "upgrades", "Upgraded"
    if test_only:
        operation, op_adj = "tests", "Tested"
    elif download_only:
        operation, op_adj = "downloads", "Downloaded"

    failed_upgrades = 0
    with ThreadPool(len(devices)) as pool:
        for i, upgrade_res in enumerate(
            pool.imap_unordered(upgrade_worker, devices), 1
        ):
            logging.info(f"{op_adj} {i}/{len(devices)}")
            if not upgrade_res:
                failed_upgrades += 1

    if failed_upgrades > 0:
        logging.error(f"There was {failed_upgrades} failed {operation}")
    else:
        logging.info(f"All {operation} went successfuly")


@click.command(
    "generate-apikey",
    help="This command generate the configuration file boilerplate using all devices connected to panorama",
)
@click.option(
    "--panorama-host",
    "host",
    envvar="PANORAMA_HOST",
    required=True,
    help="Panorama host/ip. Use PANORAMA_HOST environment variable",
)
@click.option(
    "--username",
    envvar="PANORAMA_USERNAME",
    required=True,
    help="Username password to access Panorama (envvar: PANORAMA_USERNAME)",
)
@click.option(
    "--password",
    envvar="PANORAMA_PASSWORD",
    prompt=True,
    hide_input=True,
    required=True,
    help="User password to access Panorama (envvar: PANORAMA_PASSWORD)",
)
def generate_apikey_cmd(host, username, password):
    client = nagra_panorama_api.XMLApi(host, "dummykey")
    try:
        key = client.generate_apikey(username, password)
        print(key)
    except Exception as e:
        print(e)
        exit(1)


@click.command(
    "generate-config",
    help="This command generate the configuration file boilerplate using all devices connected to panorama",
)
@click.option(
    "--panorama-host",
    "host",
    help="Panorama host/ip. Use PANORAMA_HOST environment variable",
)
@click.option(
    "--apikey",
    help="Panorama api key. Use one of the following environment variables: PANORAMA_APIKEY, PANO_APIKEY",
)
@click.option(
    "--sw-version",
    "version",
)
@click.option(
    "-o",
    "--out",
    help="Output file for the configuration containing the upgrade groups (default to stdin)",
)
def generate_configuration_file_cmd(host, apikey, version, out):
    if not host:
        host = getenv("PANORAMA_HOST")
    if not apikey:
        apikey = getenv("PANORAMA_APIKEY", "PANO_APIKEY")
    if not apikey:
        logging.error("Missing Panorama API Key")
        exit(1)
    panorama_client = nagra_panorama_api.XMLApi(host, apikey)
    connected_devices = panorama_client.get_devices(connected=True)
    data = {
        "groups": {
            "all": {
                # "panorama_ip": host,
                "version": version,
                "devices": [
                    {
                        "hostname": d.hostname,
                        "ip_address": d.ip_address,
                    }
                    for d in connected_devices
                ],
            }
        },
    }

    content = yaml.dump(data, sort_keys=False, explicit_start=True, indent=2)
    if not out:
        print(content)
    else:
        output = Path(out)
        output.write_text(content)


# client = nagra_panorama_api.XMLApi(os.environ["PANO_HOST"], os.environ["PANO_APIKEY"])
# fw_sys_info = client.system_info()

# vpn_flows = client.get_vpn_flows()
# template_status = list(panorama_client.get_templates_sync_status())
