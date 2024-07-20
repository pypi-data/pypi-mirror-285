import click

from komo.cli.utils import handle_errors
from komo.lambda_labs.connect import connect


@click.command("connect")
@handle_errors
def cmd_connect():
    api_key = click.prompt("Please enter your Lambda Labs API Key")
    connect(api_key)
