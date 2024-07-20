import click

from komo import printing
from komo.cli.utils import handle_errors
from komo.core import terminate_service


@click.command("terminate")
@click.argument(
    "service_name",
    type=str,
)
@handle_errors
def cmd_terminate(service_name: str):
    terminate_service(service_name)
    printing.success(f"Service {service_name} is being terminated")
