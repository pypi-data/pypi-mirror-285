from outerbounds._vendor import click
from . import local_setup_cli
from . import workstations_cli
from . import perimeters_cli


@click.command(
    cls=click.CommandCollection,
    sources=[local_setup_cli.cli, workstations_cli.cli, perimeters_cli.cli],
)
def cli(**kwargs):
    pass
