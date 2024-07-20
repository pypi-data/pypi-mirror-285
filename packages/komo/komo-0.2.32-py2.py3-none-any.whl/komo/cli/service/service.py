import click

from komo.cli.service.cmd_launch import cmd_launch
from komo.cli.service.cmd_list import cmd_list
from komo.cli.service.cmd_terminate import cmd_terminate


@click.group()
def service():
    pass


service.add_command(cmd_list)
service.add_command(cmd_launch)
service.add_command(cmd_terminate)
