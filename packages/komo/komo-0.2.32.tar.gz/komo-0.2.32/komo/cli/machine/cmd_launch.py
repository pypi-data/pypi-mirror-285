import time
from typing import Optional

import click

from komo import printing
from komo.cli.utils import handle_errors
from komo.core import get_machine, launch_machine, print_machine_setup_logs
from komo.types import Cloud, MachineConfig, MachineStatus


@click.command("launch")
@click.option("--name", type=str, required=True)
@click.option("--gpus", type=str, default=None)
@click.option("--cloud", "-c", type=str, default=None)
@click.option("--detach", "-d", is_flag=True, default=False)
@click.option("--notebook", is_flag=True, default=False)
@click.argument("config_file", nargs=1)
@handle_errors
def cmd_launch(
    name: str,
    gpus: Optional[str],
    cloud: Optional[str],
    detach: bool,
    notebook: bool,
    config_file: str,
):
    overrides = {}
    if gpus:
        overrides["resources/accelerators"] = gpus
    if cloud:
        overrides["resources/cloud"] = cloud
    if notebook:
        overrides["notebook"] = True
    machine_config = MachineConfig.from_yaml(config_file, **overrides)

    machine = launch_machine(machine_config, name)
    printing.success(f"Machine {machine.name} successfully created")

    if detach:
        return

    printing.info("Waiting for machine to start...")

    last_messsage = None
    while True:
        machine = get_machine(name)

        should_break = False
        error = False
        if machine.status in [MachineStatus.PENDING, MachineStatus.INITIALIZING]:
            pass
        elif machine.status in [MachineStatus.RUNNING_SETUP, MachineStatus.RUNNING]:
            should_break = True
        else:
            should_break = True
            error = True

        if machine.status_message and machine.status_message != last_messsage:
            if error:
                printing.error(machine.status_message)
            else:
                printing.info(machine.status_message)

            last_messsage = machine.status_message

        if should_break:
            break

        time.sleep(5)

    print_machine_setup_logs(machine.name, True)

    machine = get_machine(name)
    while machine.status == MachineStatus.INITIALIZING:
        time.sleep(5)
        machine = get_machine(name)

    if machine.status == MachineStatus.RUNNING:
        printing.success(f"Machine {name} successfully created")

        if machine.notebook_url:
            printing.info(
                f"Open this link to access the notebook: {machine.notebook_url}"
            )
    else:
        printing.error(
            f"Machine {name} has status {machine.status.value} with the following message:\n{machine.status_message}"
        )
