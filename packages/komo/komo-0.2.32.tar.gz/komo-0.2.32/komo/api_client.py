import json
import os
import shutil
import tempfile
import time
from typing import Dict, List, Optional, Union

import jwt
import requests
from requests.exceptions import RequestException, ConnectionError, ConnectTimeout
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_result,
    RetryError,
)


from komo import printing
from komo.types import (
    ClientException,
    Cloud,
    Job,
    JobConfig,
    JobStatus,
    Machine,
    MachineConfig,
    MachineStatus,
    Service,
    ServiceConfig,
    ServiceReplica,
)

KOMODO_API_URL = os.environ.get("KOMODO_API_URL", "https://api.komodoai.dev")
KOMODO_JWT_TOKEN_FILE_PATH = os.path.expanduser("~/.komo/jwt-token")


def _is_retryable_exception(exception):
    return (
        isinstance(exception, ConnectionError)
        or isinstance(exception, ConnectTimeout)
        or isinstance(exception, RequestException)
    )


def _is_retryable_response(response):
    return response.status_code > 500


@retry(
    retry=(
        retry_if_exception_type((ConnectionError, ConnectTimeout, RequestException))
        | retry_if_result(_is_retryable_response)
    ),
    stop=stop_after_attempt(6),
    # Wait exponentially between retries, starting at 1 second and capping at 20 seconds (1,2,4,8,16,20)
    wait=wait_exponential(multiplier=1, min=1, max=20),
)
def _make_request_and_raise_for_status(method, url, headers, files, data):
    try:
        response = requests.request(
            method,
            url,
            headers=headers,
            files=files,
            data=data,
        )
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code <= 500:
            text = e.response.text
            try:
                response_json = e.response.json()
            except requests.exceptions.JSONDecodeError:
                response_json = None

            if response_json:
                if "detail" in response_json:
                    text = response_json["detail"]

            raise ClientException(
                f"Got HTTP Error Code {e.response.status_code}: {text}"
            )

    return response


class APIClient:
    def __init__(self):
        os.makedirs(os.path.expanduser("~/.komo"), exist_ok=True)
        api_key = os.environ.get("KOMODO_API_KEY", None)
        if not api_key:
            api_key_file = os.path.expanduser("~/.komo/api-key")
            if not os.path.isfile(api_key_file):
                raise ClientException(f"{api_key_file} does not exist")

            with open(api_key_file, "r") as f:
                api_key = f.read().strip()

        self.api_key = api_key

    @classmethod
    def register(cls, email: str, password: str):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        payload = json.dumps(
            {
                "email": email,
                "password": password,
            },
        )

        _make_request_and_raise_for_status(
            "POST",
            f"{KOMODO_API_URL}/api/v1/auth/register",
            headers,
            None,
            payload,
        )

    def refresh_token(self):
        response = _make_request_and_raise_for_status(
            "POST",
            f"{KOMODO_API_URL}/api/v1/auth/jwt/api_key/login?api_key={self.api_key}",
            None,
            None,
            None,
        )
        auth = response.json()

        self._token = auth["token"]
        with open(KOMODO_JWT_TOKEN_FILE_PATH, "w") as f:
            f.write(self._token)

    @property
    def token(self):
        if os.path.exists(KOMODO_JWT_TOKEN_FILE_PATH):
            with open(KOMODO_JWT_TOKEN_FILE_PATH, "r") as f:
                token_contents = f.read()
                decoded_token = jwt.decode(
                    # when verify_signature is false, none of the other verification options are checked
                    # https://github.com/jpadilla/pyjwt/blob/master/jwt/api_jwt.py#L140
                    token_contents,
                    options={"verify_signature": False},
                )
                if decoded_token["exp"] < time.time():
                    self.refresh_token()
                else:
                    self._token = token_contents
        else:
            self.refresh_token()

        return self._token

    @classmethod
    def get_api_key(cls, email: str, password: str):
        files = {
            "username": (None, email),
            "password": (None, password),
        }

        response = _make_request_and_raise_for_status(
            "POST",
            f"{KOMODO_API_URL}/api/v1/auth/jwt/login",
            None,
            files,
            None,
        )
        auth = response.json()

        token, token_type = auth["access_token"], auth["token_type"]

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{token_type} {token}",
        }

        response = _make_request_and_raise_for_status(
            "GET",
            f"{KOMODO_API_URL}/api/v1/auth/jwt/api_key",
            headers,
            None,
            None,
        )
        auth = response.json()

        api_key = auth["api_key"]
        return api_key

    def api_request(
        self,
        method: str,
        url: str,
        files: Dict = None,
        data: Dict = None,
    ) -> Union[Dict, List]:  # Not using | for > 1 return type for < Py 3.10 compat
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        try:
            response = _make_request_and_raise_for_status(
                method,
                url,
                headers,
                files,
                data,
            )
        except RetryError as e:
            raise ClientException(f"Failed to make request to {url}")

        try:
            retval = response.json()
        except json.JSONDecodeError:
            retval = response.text

        return retval

    def get_user_id(self):
        result = self.api_request(
            "GET",
            f"{KOMODO_API_URL}/api/v1/user-id",
        )

        return result["user-id"]

    def connect_aws(self, iam_role_arn):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/aws/connect?iam_role_arn={iam_role_arn}",
        )

    def connect_lambda(self, lambda_api_key):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/lambda_labs/connect?api_key={lambda_api_key}",
        )

    def get_workdir_download_url(self, workdir_upload_id):
        response = self.api_request(
            "GET",
            f"{KOMODO_API_URL}/api/v1/workdirs/download_url?upload_id={workdir_upload_id}",
        )
        url = response["url"]
        return url

    def launch_job(
        self,
        job_config: JobConfig,
        name: Optional[str] = None,
    ) -> Job:
        payload = job_config.model_dump(exclude_none=True, mode="json")
        if "workdir" in payload:
            payload.pop("workdir")

        if name:
            payload["name"] = name

        if job_config.workdir:
            with tempfile.TemporaryDirectory() as td:
                workdir_zipfile = os.path.join(td, "workdir")
                workdir_zipfile = shutil.make_archive(
                    workdir_zipfile, "zip", job_config.workdir,
                )

                upload_info = self.api_request(
                    "GET", f"{KOMODO_API_URL}/api/v1/workdirs/upload_info"
                )
                workdir_upload_id = upload_info["upload_id"]
                upload_url = upload_info["url"]
                fields = upload_info["fields"]

                with open(workdir_zipfile, "rb") as f:
                    files = {"file": f}

                    if job_config.workdir == ".":
                        workdir_str = "current working directory"
                    else:
                        workdir_str = f"directory {job_config.workdir}"
                    printing.info(f"Uploading {workdir_str}")
                    _make_request_and_raise_for_status(
                        "POST",
                        upload_url,
                        None,
                        files,
                        fields,
                    )
                    printing.success(f"Uploaded {workdir_str}")

                payload["workdir_upload_id"] = workdir_upload_id

        payload = json.dumps(payload)
        job_dict = self.api_request(
            "POST", f"{KOMODO_API_URL}/api/v1/jobs", data=payload
        )
        job = Job.from_dict(job_dict)

        return job

    def get_job(self, job_id: str):
        job_dict = self.api_request("GET", f"{KOMODO_API_URL}/api/v1/jobs/{job_id}")
        job = Job.from_dict(job_dict)
        return job

    def get_jobs(self):
        job_dicts = self.api_request("GET", f"{KOMODO_API_URL}/api/v1/jobs")
        jobs = [Job.from_dict(d) for d in job_dicts]
        return jobs

    def _get_log_chunk(
        self,
        job_or_machine_id: str,
        node_index: str,
        next_token: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        is_machine: bool = False,
    ):
        if is_machine:
            url = f"{KOMODO_API_URL}/api/v1/machines/{job_or_machine_id}/setup_logs"
        else:
            url = f"{KOMODO_API_URL}/api/v1/jobs/{job_or_machine_id}/{node_index}/logs"
        if next_token or start_time or end_time:
            url += "?"

        args = []
        if next_token:
            args.append(f"next_token={next_token}")
        if start_time:
            args.append(f"start_time={start_time * 1000}")
        if end_time:
            args.append(f"end_time={end_time * 1000}")

        url += "&".join(args)

        logs = self.api_request("GET", url)

        return logs

    def print_job_logs(self, job_id: str, node_index: int, follow: bool):
        job = self.get_job(job_id)
        if job.status in [JobStatus.PENDING, JobStatus.INITIALIZING]:
            raise ClientException(f"Job {job_id} has not started")

        live = (
            job.status in JobStatus.executing_statuses()
            or job.status
            in [
                JobStatus.CANCELLED,
                JobStatus.CANCELLING,
                JobStatus.FINISHED,
                JobStatus.SHUTTING_DOWN,
            ]
            and (time.time() - job.updated_timestamp) < 30
        )

        # time between server queries, in seconds (so we don't overload the server)
        TIME_BETWEEN_QUERIES = 1
        # the number of seconds after a job finishes to wait before assuming no more logs are coming
        JOB_FINISH_WAIT_TIME = 30
        next_token = None
        job_finished_time = None
        last_query_time = time.time() - TIME_BETWEEN_QUERIES
        end_time = None
        if not follow:
            end_time = int(time.time())
        while True:
            time.sleep(max(TIME_BETWEEN_QUERIES - (time.time() - last_query_time), 0))
            response = self._get_log_chunk(
                job_id, node_index, next_token, end_time=end_time
            )
            last_query_time = time.time()

            for event in response["logs"]:
                message: str = event["message"]
                if message.endswith("\n"):
                    message = message[:-1]
                printing.info(message)

            if response["next_token"] == next_token:
                # we've reached the end of the currently available logs
                if not follow or not live:
                    break

                job = self.get_job(job_id)
                if job.status not in JobStatus.executing_statuses():
                    if live:
                        if job_finished_time is None:
                            job_finished_time = time.time()
                        elif (time.time() - job_finished_time) >= JOB_FINISH_WAIT_TIME:
                            break

            next_token = response["next_token"]

    def terminate_job(self, job_id: str):
        self.api_request("POST", f"{KOMODO_API_URL}/api/v1/jobs/{job_id}/cancel")

    def finish_job(self, job_id: str):
        self.api_request("POST", f"{KOMODO_API_URL}/api/v1/jobs/{job_id}/finish")

    def get_private_ssh_key(self) -> str:
        response = self.api_request("GET", f"{KOMODO_API_URL}/api/v1/ssh-key")
        ssh_key = response["ssh-key"]
        return ssh_key

    def launch_machine(
        self,
        machine_config: MachineConfig,
        name: str,
    ) -> Machine:
        payload = machine_config.model_dump(exclude_none=True)
        if "workdir" in payload:
            payload.pop("workdir")
        payload["name"] = name

        if machine_config.workdir:
            with tempfile.TemporaryDirectory() as td:
                workdir_zipfile = os.path.join(td, "workdir")
                workdir_zipfile = shutil.make_archive(
                    workdir_zipfile,
                    "zip",
                    machine_config.workdir,
                )

                upload_info = self.api_request(
                    "GET", f"{KOMODO_API_URL}/api/v1/workdirs/upload_info"
                )
                workdir_upload_id = upload_info["upload_id"]
                upload_url = upload_info["url"]
                fields = upload_info["fields"]

                with open(workdir_zipfile, "rb") as f:
                    files = {"file": f}

                    if machine_config.workdir == ".":
                        workdir_str = "current working directory"
                    else:
                        workdir_str = f"directory {machine_config.workdir}"
                    printing.info(f"Uploading {workdir_str}")
                    _make_request_and_raise_for_status(
                        "POST",
                        upload_url,
                        None,
                        files,
                        fields,
                    )
                    printing.success(f"Uploaded {workdir_str}")

                payload["workdir_upload_id"] = workdir_upload_id

        payload = json.dumps(payload)
        machine_dict = self.api_request(
            "POST", f"{KOMODO_API_URL}/api/v1/machines", data=payload
        )
        machine = Machine.from_dict(machine_dict)

        return machine

    def get_machines(self) -> List[Machine]:
        machine_dicts = self.api_request("GET", f"{KOMODO_API_URL}/api/v1/machines")
        machines = [Machine.from_dict(d) for d in machine_dicts]
        return machines

    def get_machine(self, machine_id_or_name: str, is_name: bool = False) -> Machine:
        machine_dict = self.api_request(
            "GET",
            f"{KOMODO_API_URL}/api/v1/machines/{machine_id_or_name}?is_name={str(is_name).lower()}",
        )
        machine = Machine.from_dict(machine_dict)
        return machine

    def terminate_machine(self, machine_id: str):
        self.api_request("DELETE", f"{KOMODO_API_URL}/api/v1/machines/{machine_id}")

    def mark_job_as_running_setup(self, job_id: str):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/jobs/{job_id}/running_setup",
        )

    def mark_job_as_running(self, job_id: str):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/jobs/{job_id}/running",
        )

    def post_logs(self, task_id: str, task_type: str, logs: List[Dict[str, str]]):
        assert task_type in {"jobs", "machines", "services"}
        if task_type in {"jobs", "services"}:
            assert task_id.count("/") == 1

        if task_type == "machines":
            endpoint_suffix = "setup_logs"
        else:
            endpoint_suffix = "logs"

        payload = json.dumps(
            {
                "logs": logs,
            }
        )
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/{task_type}/{task_id}/{endpoint_suffix}",
            data=payload,
        )

    def print_machine_setup_logs(self, machine_id: str, follow: bool):
        machine = self.get_machine(machine_id, is_name=False)
        if machine.status in [MachineStatus.PENDING, MachineStatus.INITIALIZING]:
            raise Exception(f"Machine {machine_id} has not started")

        live = machine.status == MachineStatus.RUNNING_SETUP

        # time between server queries, in seconds (so we don't overload the server)
        TIME_BETWEEN_QUERIES = 1
        # the number of seconds after a machine finishes setup to wait before assuming no more logs are coming
        MACHINE_FINISH_WAIT_TIME = 30
        next_token = None
        machine_finished_time = None
        last_query_time = time.time() - TIME_BETWEEN_QUERIES
        end_time = None
        if not follow:
            end_time = int(time.time())
        while True:
            time.sleep(max(TIME_BETWEEN_QUERIES - (time.time() - last_query_time), 0))
            response = self._get_log_chunk(
                machine_id,
                0,
                next_token,
                end_time=end_time,
                is_machine=True,
            )
            last_query_time = time.time()

            for event in response["logs"]:
                message: str = event["message"]
                if message.endswith("\n"):
                    message = message[:-1]
                printing.info(message)

            if response["next_token"] == next_token or not response["next_token"]:
                # we've reached the end of the currently available logs
                if not follow or not live:
                    break

                machine = self.get_machine(machine_id, is_name=False)
                if machine.status != MachineStatus.RUNNING_SETUP:
                    if live:
                        if machine_finished_time is None:
                            machine_finished_time = time.time()
                        elif (
                            time.time() - machine_finished_time
                        ) >= MACHINE_FINISH_WAIT_TIME:
                            break

            next_token = response["next_token"]

    def mark_machine_as_running_setup(self, machine_id: str):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/machines/{machine_id}/running_setup",
        )

    def mark_machine_as_running(self, machine_id: str):
        self.api_request(
            "POST",
            f"{KOMODO_API_URL}/api/v1/machines/{machine_id}/running",
        )

    def get_services(self) -> List[Service]:
        service_dicts = self.api_request("GET", f"{KOMODO_API_URL}/api/v1/services")
        services = [Service.from_dict(d) for d in service_dicts]
        return services

    def get_service(self, service_id_or_name: str, is_name: bool = False) -> Machine:
        service_dict = self.api_request(
            "GET",
            f"{KOMODO_API_URL}/api/v1/services/{service_id_or_name}?is_name={str(is_name).lower()}",
        )
        service = Service.from_dict(service_dict)
        return service

    def launch_service(
        self,
        service_config: ServiceConfig,
        name: str,
    ) -> Service:
        payload = service_config.model_dump(exclude_none=True, mode="json")
        if "workdir" in payload:
            payload.pop("workdir")
        payload["name"] = name

        if service_config.workdir:
            with tempfile.TemporaryDirectory() as td:
                workdir_zipfile = os.path.join(td, "workdir")
                workdir_zipfile = shutil.make_archive(
                    workdir_zipfile,
                    "zip",
                    service_config.workdir,
                )

                upload_info = self.api_request(
                    "GET", f"{KOMODO_API_URL}/api/v1/workdirs/upload_info"
                )
                workdir_upload_id = upload_info["upload_id"]
                upload_url = upload_info["url"]
                fields = upload_info["fields"]

                with open(workdir_zipfile, "rb") as f:
                    files = {"file": f}

                    if service_config.workdir == ".":
                        workdir_str = "current working directory"
                    else:
                        workdir_str = f"directory {service_config.workdir}"
                    printing.info(f"Uploading {workdir_str}")
                    _make_request_and_raise_for_status(
                        "POST",
                        upload_url,
                        None,
                        files,
                        fields,
                    )
                    printing.success(f"Uploaded {workdir_str}")

                payload["workdir_upload_id"] = workdir_upload_id

        payload = json.dumps(payload)
        service_dict = self.api_request(
            "POST", f"{KOMODO_API_URL}/api/v1/services", data=payload
        )
        service = Service.from_dict(service_dict)

        return service

    def terminate_service(
        self,
        service_id: str,
    ):
        self.api_request("DELETE", f"{KOMODO_API_URL}/api/v1/services/{service_id}")

    def get_service_replicas(self, service_id: str) -> List[ServiceReplica]:
        replica_dicts = self.api_request(
            "GET",
            f"{KOMODO_API_URL}/api/v1/services/{service_id}/replicas",
        )

        replicas = [ServiceReplica.from_dict(d) for d in replica_dicts]
        return replicas
