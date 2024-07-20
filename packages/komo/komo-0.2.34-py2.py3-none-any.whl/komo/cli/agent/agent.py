import click

from komo.cli.agent.cmd_download_workdir import cmd_download_workdir
from komo.cli.agent.cmd_run import cmd_run
from komo.cli.agent.cmd_run_service_replica import cmd_run_service_replica
from komo.cli.agent.cmd_setup import cmd_setup
from komo.cli.agent.cmd_setup_machine import cmd_setup_machine
from komo.cli.agent.cmd_setup_service_replica import cmd_setup_service_replica


@click.group()
@click.pass_context
def agent(ctx: click.Context):
    pass


agent.add_command(cmd_run)
agent.add_command(cmd_setup)
agent.add_command(cmd_setup_machine)
agent.add_command(cmd_setup_service_replica)
agent.add_command(cmd_run_service_replica)
agent.add_command(cmd_download_workdir)
