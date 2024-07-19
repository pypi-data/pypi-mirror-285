import click

from komo import printing
from komo.cli.utils import handle_errors
from komo.core import get_job, ssh_job
from komo.types import JobStatus


@click.command("ssh")
@click.argument(
    "job_id",
    type=str,
)
@click.option("--node-index", "-i", type=int, default=0)
@handle_errors
def cmd_ssh(job_id: str, node_index: int):
    ssh_job(job_id, node_index)
