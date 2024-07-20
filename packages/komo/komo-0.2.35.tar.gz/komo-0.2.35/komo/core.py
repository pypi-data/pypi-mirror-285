import os
import shutil
import subprocess
from typing import Dict, List, Optional

import yaml

from komo.api_client import KOMODO_JWT_TOKEN_FILE_PATH, APIClient
from komo.types import (ClientException, Cloud, Job, JobConfig, JobStatus,
                        Machine, MachineConfig, MachineStatus, ReplicaStatus,
                        Service, ServiceConfig, ServiceReplica, ServiceStatus)


def login(api_key: str):
    if os.path.isfile(KOMODO_JWT_TOKEN_FILE_PATH):
        os.remove(KOMODO_JWT_TOKEN_FILE_PATH)
    komo_dir = os.path.expanduser("~/.komo")
    os.makedirs(komo_dir, exist_ok=True)
    api_key_file = os.path.join(komo_dir, "api-key")
    with open(api_key_file, "w") as f:
        f.write(api_key)


def launch_job(
    job_config: JobConfig,
    name: Optional[str] = None,
):
    api_client = APIClient()
    job = api_client.launch_job(
        job_config,
        name,
    )
    return job


def list_jobs() -> List[Job]:
    api_client = APIClient()
    jobs = api_client.get_jobs()
    return jobs


def get_job(job_id) -> Job:
    api_client = APIClient()
    job = api_client.get_job(job_id)
    return job


def print_job_logs(job_id, node_index: int = 0, follow: bool = False):
    api_client = APIClient()
    api_client.print_job_logs(job_id, node_index, follow)


def terminate_job(job_id):
    api_client = APIClient()
    api_client.terminate_job(job_id)


def _get_private_ssh_key() -> str:
    api_client = APIClient()
    ssh_key = api_client.get_private_ssh_key()
    return ssh_key


def ssh_job(job_id, node_index: int = 0):
    api_client = APIClient()

    job = api_client.get_job(job_id)
    if job.status not in [JobStatus.RUNNING, JobStatus.RUNNING_SETUP]:
        raise ClientException(f"Job {job_id} is not running")

    if node_index >= job.num_nodes:
        raise ClientException(
            f"Node index {node_index} is out of range for job {job_id} with {job.num_nodes} node{'s' if job.num_nodes > 1 else ''}"
        )
    ip_address = job.ssh_info[node_index].get("ip_address", None)
    user = job.ssh_info[node_index].get("ssh_user", None)
    port = job.ssh_info[node_index].get("ssh_port", None)

    if not ip_address or not user or not port:
        raise ClientException("SSH info not found")

    key_file = _get_private_key_file()

    subprocess.call(
        [
            "ssh",
            "-t",
            "-i",
            key_file,
            "-o",
            "IdentitiesOnly=yes",
            "-p",
            str(port),
            f"{user}@{ip_address}",
            f"cd ~/sky_workdir; bash --login",
        ]
    )


def launch_machine(
    machine_config: MachineConfig,
    name: str,
) -> Machine:
    api_client = APIClient()
    machine = api_client.launch_machine(
        machine_config,
        name,
    )

    return machine


def list_machines() -> List[Machine]:
    api_client = APIClient()
    machines: List[Machine] = api_client.get_machines()

    running_machine_names = set(
        [m.name for m in machines if m.status == MachineStatus.RUNNING]
    )
    ssh_dir = os.path.expanduser("~/.komo/ssh")
    os.makedirs(ssh_dir, exist_ok=True)
    for machine_name in os.listdir(ssh_dir):
        if machine_name not in running_machine_names:
            os.remove(os.path.join(ssh_dir, machine_name))

    return machines


def terminate_machine(machine_name: str):
    api_client = APIClient()
    machine = api_client.get_machine(machine_name, is_name=True)
    api_client.terminate_machine(machine.id)


def get_machine(machine_name: str) -> Machine:
    api_client = APIClient()
    machine = api_client.get_machine(machine_name, is_name=True)
    return machine


def _get_private_key_file():
    ssh_dir = os.path.expanduser("~/.ssh")
    os.makedirs(ssh_dir, exist_ok=True)
    key_file = os.path.join(ssh_dir, "komodo-key")
    if not os.path.isfile(key_file):
        ssh_key = _get_private_ssh_key()
        with open(key_file, "w") as f:
            f.write(ssh_key)
        os.chmod(key_file, 0o600)

    return key_file


def ssh_machine(machine_name):
    api_client = APIClient()

    machine = api_client.get_machine(machine_name, True)
    if machine.status not in [MachineStatus.RUNNING, MachineStatus.RUNNING_SETUP]:
        raise ClientException(f"Machine {machine_name} is not running")

    ip_address = machine.ssh_info.get("ip_address", None)
    user = machine.ssh_info.get("ssh_user", None)
    port = machine.ssh_info.get("ssh_port", None)

    if not ip_address or not user or not port:
        raise ClientException("SSH info not found")

    key_file = _get_private_key_file()

    subprocess.call(
        [
            "ssh",
            "-t",
            "-i",
            key_file,
            "-o",
            "IdentitiesOnly=yes",
            "-p",
            str(port),
            f"{user}@{ip_address}",
            f"cd ~/sky_workdir; bash --login",
        ]
    )


def _setup_ssh_config():
    ssh_config_file = os.path.expanduser("~/.ssh/config")
    include_entry = "Include ~/.komo/ssh/*\n"

    config = ""
    if not os.path.isfile(ssh_config_file):
        os.makedirs(os.path.expanduser("~/.ssh"), exist_ok=True)
    else:
        with open(ssh_config_file, "r") as f:
            config = f.read()

    if include_entry in config:
        return
    config = include_entry + config

    with open(ssh_config_file, "w") as f:
        f.write(config)


def open_machine_in_vscode(machine_name):
    _setup_ssh_config()
    api_client = APIClient()

    code = shutil.which("code")
    if code is None:
        raise ClientException(
            "Please install the VSCode CLI (https://code.visualstudio.com/docs/editor/command-line)"
        )
    machine = api_client.get_machine(machine_name, is_name=True)
    if machine.status not in [MachineStatus.RUNNING, MachineStatus.RUNNING_SETUP]:
        raise ClientException(f"Machine {machine_name} is not running")

    ip_address = machine.ssh_info.get("ip_address", None)
    user = machine.ssh_info.get("ssh_user", None)
    port = machine.ssh_info.get("ssh_port", None)

    if not ip_address or not user or not port:
        raise ClientException("SSH info not found")

    key_file = _get_private_key_file()

    ssh_file = os.path.expanduser(f"~/.komo/ssh/{machine_name}")
    os.makedirs(os.path.expanduser("~/.komo/ssh"), exist_ok=True)

    with open(ssh_file, "w") as f:
        f.write(
            f"Host {machine_name}\n"
            f"\tHostname {ip_address}\n"
            f"\tIdentityFile {key_file}\n"
            "\tIdentitiesOnly=yes\n"
            f"\tUser {user}\n"
            f"\tPort {port}\n"
        )

    subprocess.call(
        [
            "code",
            "--remote",
            f"ssh-remote+{machine_name}",
            f"/home/{user}/sky_workdir",
        ]
    )


def print_machine_setup_logs(machine_name: str, follow: bool):
    api_client = APIClient()
    machine = api_client.get_machine(machine_name, is_name=True)
    api_client.print_machine_setup_logs(machine.id, follow)


def list_services() -> List[Service]:
    api_client = APIClient()
    services = api_client.get_services()
    return services


def get_service(service_name: str) -> Service:
    api_client = APIClient()
    service = api_client.get_service(service_name, is_name=True)
    return service


def launch_service(
    service_config: ServiceConfig,
    name: str,
) -> Service:
    api_client = APIClient()
    service = api_client.launch_service(
        service_config,
        name,
    )

    return service


def terminate_service(
    service_name: str,
):
    api_client = APIClient()
    service = api_client.get_service(service_name, is_name=True)
    api_client.terminate_service(service.id)
