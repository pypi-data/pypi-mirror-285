import click

from komo import printing
from komo.cli.utils import handle_errors
from komo.core import get_machine, ssh_machine
from komo.types import MachineStatus


@click.command("ssh")
@click.argument(
    "machine_name",
    type=str,
)
@handle_errors
def cmd_ssh(machine_name: str):
    ssh_machine(machine_name)
