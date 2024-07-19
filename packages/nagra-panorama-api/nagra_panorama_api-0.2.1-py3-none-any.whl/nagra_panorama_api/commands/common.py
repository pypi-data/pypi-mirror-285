import logging
from datetime import datetime
from pathlib import Path

import yaml

DEFAULT_OUTPUT_DIRECTOR = "upgrade_logs"


def ensure_output_directory(output, group):
    if output == "":
        return output
    if output is None:
        output = DEFAULT_OUTPUT_DIRECTOR

    # Check that the destination directory is not a file
    logs_output = Path(output).resolve()
    if logs_output.is_file():
        logging.error(f"{logs_output} is a file, it must be a folder or not exists")
        exit(1)

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    group_folder = f"{group}_{now}"
    # Check that the group directory is not a file
    group_logs_output = logs_output / Path(group_folder)
    if group_logs_output.is_file():
        logging.error(
            f"""\
Destination '{logs_output}' already contains a file named '{group_folder}'.
Please rename/delete/move file '{group_logs_output}' or change the destination folder
"""
        )
        exit(1)
    group_logs_output.mkdir(parents=True)
    return group_logs_output


def ensure_group_load(file, group):
    file = Path(file).resolve()
    if not file.exists():
        logging.error(f"File {file} does not exist")
        exit(1)
    if file.suffix not in (".yml", ".yaml"):
        logging.error("File must be in yaml format")
        exit(1)
    try:
        data = yaml.safe_load(file.read_text())
        groups = data["groups"]
        group_data = groups.get(group)
        if group_data:
            return group_data
        logging.error(f"Group '{group}' does not exist ini file {file}")
        defined_groups = groups.keys()
        if defined_groups:
            defined_groups = ", ".join(sorted(defined_groups))
            logging.info(f"Possible groups are: {defined_groups}")
        exit(1)
    except Exception as e:
        logging.error(
            f"""\
An error occured when parsing the file '{file}' and/or retrieving the data of group '{group}'
Make sure that the file is formatted correctly and that the group exists
{e}
"""
        )
        exit(1)
