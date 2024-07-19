import click

from .dump_configs import dump_states_cmd
from .dump_dir import dump_dir
from .software_update import (
    generate_apikey_cmd,
    generate_configuration_file_cmd,
    upgrade_cmd,
)


# Keep it as the main entry point
@click.group()
def cli():
    pass


# Add here your subcommands if needed
cli.add_command(dump_states_cmd)
cli.add_command(upgrade_cmd)
cli.add_command(generate_configuration_file_cmd)
cli.add_command(generate_apikey_cmd)
cli.add_command(dump_dir)
