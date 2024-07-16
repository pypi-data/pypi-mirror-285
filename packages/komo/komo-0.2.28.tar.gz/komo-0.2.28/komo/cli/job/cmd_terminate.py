import click

from komo import printing
from komo.cli.utils import handle_errors
from komo.core import terminate_job


@click.command("terminate")
@click.argument(
    "job_id",
    type=str,
)
@handle_errors
def cmd_terminate(job_id: str):
    terminate_job(job_id)
    printing.success(f"Job {job_id} is being terminated")
