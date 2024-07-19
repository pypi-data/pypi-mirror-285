import webbrowser

import click

from komo import printing
from komo.cli.utils import handle_errors
from komo.core import get_machine


@click.command("notebook")
@click.argument(
    "machine_name",
    type=str,
)
@handle_errors
def cmd_notebook(machine_name: str):
    machine = get_machine(machine_name)
    url = machine.notebook_url
    if not url:
        printing.error("There is no notebook running on this machine")
        exit(1)
    printing.success(f"Opening notebook at {url}")
    webbrowser.open(url)
