import click

from komo.aws.connect import connect
from komo.cli.utils import handle_errors


@click.command("connect")
@handle_errors
def cmd_connect():
    connect()
