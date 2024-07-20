import os
from typing import List, Optional

import click

from komo import printing
from komo.cli.utils import handle_errors
from komo.core import login


@click.command("login")
@handle_errors
def cmd_login():
    api_key = click.prompt("API Key")

    login(api_key)
    printing.success("You are now logged in!")
