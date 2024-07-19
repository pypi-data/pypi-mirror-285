import click

from komo.cli.job.cmd_launch import cmd_launch
from komo.cli.job.cmd_list import cmd_list
from komo.cli.job.cmd_logs import cmd_logs
from komo.cli.job.cmd_ssh import cmd_ssh
from komo.cli.job.cmd_terminate import cmd_terminate


@click.group
def job():
    pass


job.add_command(cmd_launch)
job.add_command(cmd_terminate)
job.add_command(cmd_list)
job.add_command(cmd_logs)
job.add_command(cmd_ssh)
