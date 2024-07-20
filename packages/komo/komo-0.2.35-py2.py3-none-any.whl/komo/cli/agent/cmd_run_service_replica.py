import click

from komo.agent.core import run_service_replica


@click.command("run-service-replica")
@click.option("--service-id", type=str, required=True)
@click.option("--replica-id", type=int, required=True)
@click.option("--script", type=str, required=True)
def cmd_run_service_replica(
    service_id: str,
    replica_id: int,
    script: str,
):
    run_service_replica(service_id, replica_id, script)
