import os
import subprocess
import tempfile
import time
import traceback
import zipfile

import requests
from retry.api import retry_call

from komo.api_client import APIClient


class Logger:
    _TIME_BETWEEN_LOGS = 1

    def __init__(
        self,
        api_client: APIClient,
        task_id: str,
        task_type: str,
    ):
        self.api_client = api_client
        self.task_id = task_id
        self.task_type = task_type
        self.buffer = []
        self.last_log_time = None

    def flush(self):
        if len(self.buffer) == 0:
            return

        try:
            self.api_client.post_logs(
                self.task_id,
                self.task_type,
                self.buffer,
            )
        except Exception as e:
            print(e)
            traceback.print_exc()

        self.buffer = []
        self.last_log_time = time.time()

    def flush_if_necessary(self):
        curr_time = time.time()

        if (
            not self.last_log_time
            or (curr_time - self.last_log_time) > self._TIME_BETWEEN_LOGS
        ):
            self.flush()

    def log(self, message: str):
        self.flush_if_necessary()

        self.buffer.append(
            {
                "timestamp": int(time.time() * 1000),
                "message": message,
            }
        )

    def __del__(self):
        self.flush()


def _get_setup_node_index() -> int:
    node_index = os.environ.get("SKYPILOT_SETUP_NODE_RANK", 0)
    node_index = int(node_index)
    return node_index


def _get_node_index() -> int:
    node_index = os.environ.get("SKYPILOT_NODE_RANK", 0)
    node_index = int(node_index)
    return node_index


def _execute(
    api_client: APIClient,
    task_id: str,
    task_type: str,
    script: str,
    raise_on_error: bool = True,
):
    logger = Logger(api_client, task_id, task_type)

    with tempfile.TemporaryDirectory() as td:
        script_file = os.path.join(td, "script.sh")

        with open(script_file, "w") as f:
            f.write(script)

        proc = subprocess.Popen(
            ["bash", script_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        for line in proc.stdout:
            try:
                logger.log(line.decode("utf-8"))
            except:
                pass

        proc.communicate()
        if raise_on_error and proc.returncode != 0:
            raise Exception(f"Process exited with return code {proc.returncode}")


def setup(job_id: str, setup_script: str):
    api_client = APIClient()
    node_index = _get_setup_node_index()
    try:
        api_client.mark_job_as_running_setup(job_id)
        task_id = f"{job_id}/{node_index}"
        _execute(api_client, task_id, "jobs", setup_script)
    except Exception as e:
        if node_index == 0:
            retry_call(api_client.finish_job, fargs=[job_id], tries=-1, delay=30)
        raise e


def run(job_id: str, run_script: str):
    api_client = APIClient()
    node_index = _get_node_index()
    try:
        api_client.mark_job_as_running(job_id)
        task_id = f"{job_id}/{node_index}"
        _execute(api_client, task_id, "jobs", run_script)
    finally:
        if node_index == 0:
            retry_call(api_client.finish_job, fargs=[job_id], tries=-1, delay=30)


def setup_machine(machine_id: str, setup_script: str):
    api_client = APIClient()
    # We don't raise on error because we still want the machine to stay running even if the
    # setup script fails (so the user can debug)
    # TODO: instead of using raise_on_error=False, catch an exception, and mark the machine
    # as "setup failed" (will have to create this endpoint on the server)
    try:
        api_client.mark_machine_as_running_setup(machine_id)
        _execute(api_client, machine_id, "machines", setup_script, raise_on_error=False)
    finally:
        retry_call(
            api_client.mark_machine_as_running, fargs=[machine_id], tries=-1, delay=30
        )


def setup_service_replica(service_id: str, replica_id: int, setup_script: str):
    api_client = APIClient()
    task_id = f"{service_id}/{replica_id}"
    _execute(api_client, task_id, "services", setup_script)


def run_service_replica(service_id: str, replica_id: int, run_script: str):
    api_client = APIClient()
    task_id = f"{service_id}/{replica_id}"
    _execute(api_client, task_id, "services", run_script)


def download_workdir(workdir_upload_id: str, destination: str):
    api_client = APIClient()
    os.makedirs(destination, exist_ok=True)

    download_url = api_client.get_workdir_download_url(workdir_upload_id)
    response = requests.get(download_url)
    response.raise_for_status()
    tf = tempfile.mktemp()
    with open(tf, "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile(tf, "r") as zf:
        zf.extractall(destination)

    os.remove(tf)
