import click

from komo import printing
from komo.cli.utils import handle_errors, prompt_update
from komo.core import login


@click.command("update")
def cmd_update():
    prompt_update(noconfirm=True)
