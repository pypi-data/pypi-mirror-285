import json
import logging
from collections import defaultdict
from pathlib import Path

import click

# https://stackoverflow.com/questions/27981545/suppress-insecurerequestwarning-unverified-https-request-is-being-made-in-pytho
import urllib3

from nagra_panorama_api.restapi import PanoramaClient
from nagra_panorama_api.xmlapi import XMLApi
from nagra_panorama_api.xmlapi.utils import el2dict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def xpath(el, expr):
    res = el.xpath(expr)
    if not res:
        return None
    return res[0]


def missing_attributes(element):
    location = element.xpath("../../..")[0].tag or ""
    # Find the first ancestor below the device-group tag
    device_group = (element.xpath("ancestor::*[parent::device-group]/@name") or [""])[0]
    loc = device_group
    return {
        "@location": location,
        "@device-group": device_group,
        "@loc": loc,
    }


def transform_value(d, path, transform):
    if not path or not d:
        return d
    c = d
    for p in path[:-1]:
        c = c.get(p)
        if c is None:
            return d
    key = path[-1]
    value = c.get(key)
    res = transform(key, value)
    c[key] = res
    return d


def _wrap_list(value):
    if value is not None and not isinstance(value, list):
        value = [value]
    return value


def ensure_list(d, path):
    return transform_value(d, path, lambda _, v: _wrap_list(v))


# def convert_member(d, path):
#     """
#         Convert {member: ["...", "..."]} to [{"#text": "..."}]
#         at the position given by keys
#     """

#     def transform(_, value):
#         print('func', value)
#         return [{'#text': text} for text in _wrap_list(value['member'])]

#     return transform_value(d, path, transform)

# ============================================================
# Grouping utilities


def group_into(target, element, keys):
    if not keys:
        raise Exception("missing keys")
    for k in keys[:-1]:
        target = target.setdefault(k, {})
    target = target.setdefault(keys[-1], [])
    target.append(element)


def group_rules(rules):
    groups = {}
    for e in rules:
        dg = e["@device-group"]
        pre_post = e["@location"].split("-")[0]
        group_into(groups, e, (dg, pre_post))
    return groups


def _flatten_dict(d):
    if not isinstance(d, dict):
        yield (d,)  # Use a tuple because it will be unpacked
        return
    for k, v in d.items():
        tmp = list(_flatten_dict(v))
        for *keys, data in tmp:
            yield (k, *keys, data)


def flatten_grouped_rules(rules):
    "device-group -> pre/post -> rule"
    groups = group_rules(rules)
    return list(_flatten_dict(groups))


# ============================================================


def _convert_element_to_dict(element, func=None):
    d = el2dict(element)["entry"]
    d.update(missing_attributes(element))
    if func is not None:
        d = func(d)
    return d


def convert_elements_to_dict(elements, func=None):
    return [_convert_element_to_dict(e, func=func) for e in elements]


# ============================================================


def prepare_rules(tree, rule_definitions):
    for rule_def in rule_definitions:
        elements = tree.xpath(rule_def["xpath"])
        data = convert_elements_to_dict(elements)
        rule_def["data"] = data
    return rule_definitions


def _dump_rules(directory, rule_type, rules):
    if isinstance(directory, str):
        directory = Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    # device-group -> pre/post -> rule
    grouped = flatten_grouped_rules(rules)
    for args in grouped:
        try:
            device_group, pre_post, rules = args
            # TODO: FIX => rules can be a mere dictionnary sometimes
        except Exception:
            print(args)
            raise
        filename = f"{pre_post}{rule_type}RulesFW{device_group}.json"
        with open(directory / filename, "w") as f:
            json.dump(rules, f)


def dump_rules(output_dir, rules):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for rule_def in rules:
        _dump_rules(
            output_dir / rule_def["folder"],
            rule_def["rule_type"],
            rule_def["data"],
        )


# ============================================================

RULES = [
    {
        "rule_type": "security",
        "folder": "securityRules",
        "xpath": (
            "devices/entry/device-group/*"
            "/*[self::post-rulebase or self::pre-rulebase]/security/rules/entry"
        ),
    },
    {
        "rule_type": "nat",
        "folder": "nat",
        "xpath": (
            "devices/entry/device-group/*"
            "/*[self::post-rulebase or self::pre-rulebase]/nat/rules/entry"
        ),
    },
    {
        "rule_type": "pbf",
        "folder": "pb",
        "xpath": (
            "devices/entry/device-group/*"
            "/*[self::post-rulebase or self::pre-rulebase]/pbf/rules/entry"
        ),
    },
    {
        "rule_type": "appover",
        "folder": "appover",
        "xpath": (
            "devices/entry/device-group/*"
            "/*[self::post-rulebase or self::pre-rulebase]"
            "/application-override/rules/entry"
        ),
    },
]


def dump_dir_xml(output, host, api_key):
    client = XMLApi(host, api_key)
    logging.info("Starting to retrieve the data (extended informations)")
    tree = client.get_tree(extended=True)

    logging.info("Data retrieved, starting the export")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)

    address_elements = tree.xpath("devices/entry/device-group/*/address/entry")
    address_group_elements = tree.xpath(
        "devices/entry/device-group/*/address-group/entry",
    )

    addresses = convert_elements_to_dict(
        address_elements,
        lambda d: ensure_list(d, ("tag", "member")),
    )
    addresses_groups = convert_elements_to_dict(
        address_group_elements,
        lambda d: ensure_list(d, ("static", "member")),
    )

    with open(output / "addresses.json", "w") as f:
        json.dump(addresses, f)
    with open(output / "addressGroups.json", "w") as f:
        json.dump(addresses_groups, f)

    prepare_rules(tree, RULES)
    dump_rules(output, RULES)
    logging.info("Export done")


def get_rest_rules(client, device_group):
    return [
        {
            "rule_type": "security",
            "folder": "securityRules",
            "pre-data": client.policies.SecurityPreRules.get(
                device_group=device_group,
                inherited=False,
            ),
            "post-data": client.policies.SecurityPostRules.get(
                device_group=device_group,
                inherited=False,
            ),
        },
        {
            "rule_type": "nat",
            "folder": "nat",
            "pre-data": client.policies.NATPreRules.get(
                device_group=device_group,
                inherited=False,
            ),
            "post-data": client.policies.NATPostRules.get(
                device_group=device_group,
                inherited=False,
            ),
        },
        {
            "rule_type": "pbf",
            "folder": "pb",
            "pre-data": client.policies.PolicyBasedForwardingPreRules.get(
                device_group=device_group,
                inherited=False,
            ),
            "post-data": client.policies.PolicyBasedForwardingPostRules.get(
                device_group=device_group,
                inherited=False,
            ),
        },
        {
            "rule_type": "appover",
            "folder": "appover",
            "pre-data": client.policies.ApplicationOverridePreRules.get(
                device_group=device_group,
                inherited=False,
            ),
            "post-data": client.policies.ApplicationOverridePostRules.get(
                device_group=device_group,
                inherited=False,
            ),
        },
        {
            "rule_type": "decryption",
            "folder": "decryption",
            "pre-data": client.policies.DecryptionPreRules.get(
                device_group=device_group,
                inherited=False,
            ),
            "post-data": client.policies.DecryptionPostRules.get(
                device_group=device_group,
                inherited=False,
            ),
        },
    ]


def grouped_rest_rules(rules):
    # device-group -> pre/post -> rule
    grouped = {}
    for r in rules:
        folder = r["folder"]
        rule_type = r["rule_type"]
        for pre_post in ("pre", "post"):
            for e in r[pre_post + "-data"]:
                dg = e["@device-group"]
                group_into(grouped, e, (folder, rule_type, dg, pre_post))
    grouped = _flatten_dict(grouped)
    data = defaultdict(list)
    for args in grouped:
        try:
            folder, rule_type, device_group, pre_post, rules = args
            # TODO: FIX => rules can be a mere dictionnary sometimes
        except Exception:
            print(args)
            raise
        filename = f"{pre_post}{rule_type}RulesFW{device_group}.json"
        data[folder].append((filename, rules))
    return dict(data)


def dump_rest_rules(output_dir, rules):
    output_dir = Path(output_dir)
    for folder, data in grouped_rest_rules(rules).items():
        directory = output_dir / folder
        directory.mkdir(parents=True, exist_ok=True)
        for filename, rules in data:
            with open(directory / filename, "w") as f:
                json.dump(rules, f)


def dump_dir_rest(output, host, api_key):
    client = PanoramaClient(host, api_key)
    logging.info("Starting to retrieve the data (extended informations)")
    groups = [d["@name"] for d in client.panorama.DeviceGroups.get()]
    addresses = client.objects.Addresses.get(device_group=groups, inherited=False)
    addresses_groups = client.objects.AddressGroups.get(
        device_group=groups,
        inherited=False,
    )

    rules = get_rest_rules(client, groups)
    logging.info("Data retrieved, starting the export")
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)

    with open(output / "addresses.json", "w") as f:
        json.dump(addresses, f)
    with open(output / "addressGroups.json", "w") as f:
        json.dump(addresses_groups, f)
    dump_rest_rules(output, rules)
    logging.info("Export done")


@click.command(
    "dump-dir",
    help="Dump data from palo alto",
)
@click.option("-o", "--output", help="Output directory", default="output")
@click.option(
    "-h",
    "--host",
    envvar="PANO_HOST",
    help="Palo Alto host (default to PANO_HOST env var)",
    required=True,
)
@click.option(
    "-k",
    "--key",
    "api_key",
    envvar="PANO_API_KEY",
    help="Palo Alto API Key (default to PANO_API_KEY env var)",
    required=True,
)
@click.option("--api", type=click.Choice(["xml", "rest"]), default="rest")
def dump_dir(output, host, api_key, api):
    host = host.strip()  # remove trailing \r
    api_key = api_key.strip()  # remove trailing \r
    if api == "xml":
        dump_dir_xml(output, host, api_key)
    else:
        dump_dir_rest(output, host, api_key)
