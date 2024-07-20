import click

from komo.cli.lambda_labs.cmd_connect import cmd_connect


@click.group("lambda")
@click.pass_context
def lambda_labs(ctx: click.Context):
    pass


lambda_labs.add_command(cmd_connect)
