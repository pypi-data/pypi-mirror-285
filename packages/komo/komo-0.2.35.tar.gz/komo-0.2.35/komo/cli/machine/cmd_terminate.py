import click

from komo import printing
from komo.cli.utils import handle_errors
from komo.core import terminate_machine


@click.command("terminate")
@click.argument(
    "machine_name",
    type=str,
)
@handle_errors
def cmd_terminate(machine_name: str):
    terminate_machine(machine_name)
    printing.success(f"Machine {machine_name} is being terminated")
