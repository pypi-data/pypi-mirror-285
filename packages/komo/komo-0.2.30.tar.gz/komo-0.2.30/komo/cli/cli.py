import os

import click

from komo.cli.agent.agent import agent
from komo.cli.aws.aws import aws
from komo.cli.cmd_login import cmd_login
from komo.cli.job.job import job
from komo.cli.lambda_labs.lambda_labs import lambda_labs
from komo.cli.machine.machine import machine
from komo.cli.service.service import service


@click.group()
@click.pass_context
def cli(ctx: click.Context):
    ctx.ensure_object(dict)


cli.add_command(cmd_login)
cli.add_command(aws)
cli.add_command(lambda_labs)
cli.add_command(machine)
cli.add_command(job)
cli.add_command(service)

# agent is not to be used by the user, but only but running komodo workflows
if os.environ.get("__KOMODO_INTERNAL_AGENT__", None):
    cli.add_command(agent)
