import os
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

import yaml
from pydantic import (BaseModel, ConfigDict, Field, NonNegativeInt,
                      PositiveInt, ValidationError, field_validator,
                      model_validator)
from pydantic_core import PydanticCustomError


class ClientException(Exception):
    def __init__(self, msg):
        self.msg = msg


class Cloud(str, Enum):
    AWS: str = "aws"
    LAMBDA_LABS: str = "lambda"
    GCP: str = "gcp"
    RUNPOD: str = "runpod"
    KUBERNETES: str = "kubernetes"


class AcceleratorArgsConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    runtime_version: Optional[str] = Field(default=None)
    tpu_name: Optional[str] = Field(default=None)
    tpu_vm: Optional[bool] = Field(default=None)


class SingleResourcesConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    cloud: Optional[Cloud] = Field(default=None)
    region: Optional[str] = Field(default=None)
    zone: Optional[str] = Field(default=None)
    cpus: Optional[Union[str, PositiveInt]] = Field(default=None)
    memory: Optional[Union[str, PositiveInt]] = Field(default=None)
    accelerators: Optional[Union[str, Dict[str, Optional[PositiveInt]], List[str]]] = (
        Field(default=None)
    )
    instance_type: Optional[str] = Field(default=None)
    use_spot: Optional[bool] = Field(default=None)
    disk_size: Optional[PositiveInt] = Field(default=None)
    disk_tier: Optional[str] = Field(default=None)
    ports: Optional[List[str]] = Field(default=None)
    accelerator_args: Optional[AcceleratorArgsConfig] = Field(default=None)
    image_id: Optional[str] = Field(default=None)

    @field_validator("ports", mode="before")
    @classmethod
    def validate_ports(cls, ports: Any) -> Any:
        if isinstance(ports, str):
            return [ports]

        if isinstance(ports, int):
            return [str(ports)]

        if isinstance(ports, list) and all(
            [isinstance(p, int) or isinstance(p, str) for p in ports]
        ):
            return list(map(str, ports))

        return ports


class ResourcesConfig(SingleResourcesConfig):
    any_of: Optional[List[SingleResourcesConfig]] = Field(default=None)
    ordered: Optional[List[SingleResourcesConfig]] = Field(default=None)


class FileMountConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: str
    mode: Literal["MOUNT", "COPY"]


class _TaskConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # common to all machines/jobs/services
    workdir: Optional[str] = Field(default=None)
    resources: Optional[ResourcesConfig] = Field(default=None)
    envs: Optional[Dict[str, Union[str, int, float]]] = Field(default=None)
    file_mounts: Optional[Dict[str, FileMountConfig]] = Field(default=None)
    setup: Optional[str] = Field(default=None)

    @field_validator("envs", mode="before")
    @classmethod
    def validate_env_var_names(
        cls, envs: Optional[Dict[str, Union[str, int, float]]]
    ) -> Optional[Dict[str, Union[str, int, float]]]:
        if not envs:
            return envs

        for var_name in envs.keys():
            match = re.search("^[a-zA-Z_][a-zA-Z0-9_]*$", var_name)
            if match is None:
                raise PydanticCustomError(
                    "env_regex_mismatch",
                    f"{var_name} is not a valid environment variable name",
                )

        return envs

    @staticmethod
    def _update_config(config: dict, **overrides) -> dict:
        updated_config = config.copy()
        for k, v in overrides.items():
            keys = k.split("/")
            curr_obj = updated_config
            for key in keys[:-1]:
                if key not in curr_obj:
                    curr_obj[key] = {}
                elif not isinstance(curr_obj[key], dict):
                    raise ClientException(
                        f"Cannot set property {k} in config because it already has a non-dict value"
                    )

                curr_obj = curr_obj[key]

            curr_obj[keys[-1]] = v

        return updated_config

    @classmethod
    def _from_dict(cls, config: dict, **overrides):
        updated_config = cls._update_config(config, **overrides)
        try:
            config = cls(**updated_config)
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                loc = error["loc"]
                loc = "/".join(map(str, loc))
                msg = error["msg"]

                error_message = f"'{loc}': {msg}"
                error_messages.append(error_message)

            raise ClientException(
                "\033[1mConfig Error\033[22m\n" + "\n".join(error_messages)
            )

        return config


class MachineConfig(_TaskConfig):
    notebook: Optional[bool] = Field(default=None)

    @classmethod
    def from_yaml(cls, config_file: str, **overrides) -> "MachineConfig":
        if not os.path.isfile(config_file):
            raise ClientException(f"{config_file} does not exist")

        with open(config_file, "r") as f:
            config = yaml.load(f, yaml.FullLoader)

        # ignore job/service config fields
        if "run" in config:
            config.pop("run")
        if "service" in config:
            config.pop("service")

        machine_config = super()._from_dict(config, **overrides)
        return machine_config


class JobConfig(_TaskConfig):
    workdir: Optional[str] = Field(default=None)
    num_nodes: Optional[PositiveInt] = Field(default=None)
    run: str

    @classmethod
    def from_yaml(cls, config_file: str, **overrides) -> "JobConfig":
        if not os.path.isfile(config_file):
            raise ClientException(f"{config_file} does not exist")

        with open(config_file, "r") as f:
            config = yaml.load(f, yaml.FullLoader)

        # ignore machine/service config fields
        if "notebook" in config:
            config.pop("notebook")
        if "service" in config:
            config.pop("service")

        job_config = super()._from_dict(config, **overrides)
        return job_config


class ServiceConfigReadinessProbeSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    post_data: Optional[dict] = Field(default=None)
    initial_delay_seconds: Optional[PositiveInt] = Field(default=None)

    @model_validator(mode="after")
    def validate_readiness_probe(self):
        if not self.path.startswith("/"):
            raise PydanticCustomError(
                "readiness_probe_path_error", "readiness probe path must start with /"
            )
        return self


class ServiceConfigReplicaPolicySection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    min_replicas: NonNegativeInt
    max_replicas: Optional[PositiveInt] = Field(default=None)
    target_qps_per_replica: Optional[PositiveInt] = Field(default=None)
    upscale_delay_seconds: Optional[PositiveInt] = Field(default=None)
    downscale_delay_seconds: Optional[PositiveInt] = Field(default=None)

    @model_validator(mode="after")
    def validate_policy(self):
        if self.max_replicas is not None and self.max_replicas < self.min_replicas:
            raise PydanticCustomError(
                "min_max_replica_error",
                "max_replicas must be greater than min_replicas",
            )

        if (
            self.max_replicas is not None
            and self.max_replicas > self.min_replicas
            and self.target_qps_per_replica is None
        ):
            raise PydanticCustomError(
                "target_qps_per_replica_error",
                "target_qps_per_replica must be provided when max_replicas > min_replicas",
            )

        return self


class ServiceConfigServiceSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    readiness_probe: ServiceConfigReadinessProbeSection
    replica_policy: ServiceConfigReplicaPolicySection


class ServiceConfig(JobConfig):
    service: ServiceConfigServiceSection

    @classmethod
    def from_yaml(cls, config_file: str, **overrides) -> "ServiceConfig":
        if not os.path.isfile(config_file):
            raise ClientException(f"{config_file} does not exist")

        with open(config_file, "r") as f:
            config = yaml.load(f, yaml.FullLoader)

        # ignore machine config fields
        if "notebook" in config:
            config.pop("notebook")

        service_config = super()._from_dict(config, **overrides)

        return service_config


class JobStatus(Enum):
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING_SETUP = "running_setup"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    FINISHED = "finished"
    CANCELLING = "cancelling"
    CANCELLED = "cancelled"
    ERROR = "error"
    UNKNOWN = "unknown"
    NOT_FOUND = "not found"
    UNAUTHORIZED = "unauthorized"
    UNREACHABLE = "unreachable"

    @classmethod
    def executing_statuses(cls):
        return [cls.RUNNING_SETUP, cls.RUNNING]


class MachineStatus(Enum):
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING_SETUP = "running_setup"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    TERMINATING = "terminating"
    TERINATED = "terminated"
    ERROR = "error"
    UNKNOWN = "unknown"
    NOT_FOUND = "not found"
    UNAUTHORIZED = "unauthorized"
    UNREACHABLE = "unreachable"

    @classmethod
    def executing_statuses(cls):
        return [cls.RUNNING_SETUP, cls.RUNNING]


class ServiceStatus(Enum):
    CONTROLLER_INIT = "CONTROLLER_INIT"
    REPLICA_INIT = "REPLICA_INIT"
    CONTROLLER_FAILED = "CONTROLLER_FAILED"
    READY = "READY"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    FAILED = "FAILED"
    FAILED_CLEANUP = "FAILED_CLEANUP"
    NO_REPLICA = "NO_REPLICA"
    DELETED = "DELETED"
    UNAUTHORIZED = "unauthorized"
    NOT_FOUND = "not found"
    UNKNOWN = "unknown"


class ReplicaStatus(Enum):
    PENDING = "PENDING"
    PROVISIONING = "PROVISIONING"
    STARTING = "STARTING"
    READY = "READY"
    NOT_READY = "NOT_READY"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    FAILED = "FAILED"
    FAILED_INITIAL_DELAY = "FAILED_INITIAL_DELAY"
    FAILED_PROBING = "FAILED_PROBING"
    FAILED_PROVISION = "FAILED_PROVISION"
    FAILED_CLEANUP = "FAILED_CLEANUP"
    PREEMPTED = "PREEMPTED"
    UNKNOWN = "UNKNOWN"


@dataclass(kw_only=True)
class Job:
    id: str
    status: JobStatus
    status_message: str
    cloud: Optional[Cloud]
    region: Optional[str]
    zone: Optional[str]
    instance_type: Optional[str]
    accelerators: Optional[str]
    ports: Optional[List[dict]]
    disk_size: Optional[int]
    spot: Optional[bool]
    ssh_info: Optional[List[dict]]

    name: str
    num_nodes: int
    requested_resources: dict
    envs: dict
    file_mounts: dict
    setup: str
    run: str

    created_timestamp: int
    started_timestamp: Optional[int]
    updated_timestamp: int
    finished_timestamp: Optional[int]

    @classmethod
    def from_dict(cls, d):
        d["status"] = JobStatus(d["status"])
        if d.get("cloud", None):
            d["cloud"] = Cloud(d["cloud"])

        job = Job(**d)
        return job


@dataclass(kw_only=True)
class Machine:
    id: str
    status: MachineStatus
    status_message: str
    cloud: Optional[Cloud]
    region: Optional[str]
    zone: Optional[str]
    instance_type: Optional[str]
    accelerators: Optional[str]
    ports: Optional[List[dict]]
    disk_size: Optional[int]
    spot: Optional[bool]
    ssh_info: Optional[dict]

    name: str
    requested_resources: dict
    envs: dict
    file_mounts: dict
    setup: str
    notebook_token: Optional[str]
    notebook_url: Optional[str]

    created_timestamp: int
    started_timestamp: Optional[int]
    updated_timestamp: int
    terminated_timestamp: Optional[int]

    @classmethod
    def from_dict(cls, d):
        d["status"] = MachineStatus(d["status"])
        if d.get("cloud", None):
            d["cloud"] = Cloud(d["cloud"])

        machine = Machine(**d)
        return machine


@dataclass(kw_only=True)
class ReadinessProbeSection:
    path: str
    post_data: Optional[dict] = None
    initial_delay_seconds: int


@dataclass(kw_only=True)
class ReplicaPolicySection:
    min_replicas: int
    max_replicas: int
    target_qps_per_replica: Optional[int] = None
    upscale_delay_seconds: int
    downscale_delay_seconds: int


@dataclass(kw_only=True)
class ServiceSection:
    readiness_probe: ReadinessProbeSection
    replica_policy: ReplicaPolicySection

    @classmethod
    def from_dict(cls, d):
        d["readiness_probe"] = ReadinessProbeSection(**d["readiness_probe"])
        d["replica_policy"] = ReplicaPolicySection(**d["replica_policy"])

        service_section = ServiceSection(**d)
        return service_section


@dataclass(kw_only=True)
class Service:
    id: str
    status: ServiceStatus
    status_message: str

    name: str
    num_nodes: int
    requested_resources: dict
    envs: dict
    file_mounts: dict
    setup: str
    run: str
    service: ServiceSection

    uptime: int
    active_versions: List[int]

    created_timestamp: int
    updated_timestamp: int

    url: Optional[str] = None

    @classmethod
    def from_dict(cls, d):
        d["status"] = ServiceStatus(d["status"])
        d["service"] = ServiceSection.from_dict(d["service"])

        service = Service(**d)
        return service


@dataclass(kw_only=True)
class ServiceReplica:
    service_id: str
    replica_id: int
    version: int
    status: Optional[ReplicaStatus]

    cloud: Optional[Cloud]
    region: Optional[str]
    zone: Optional[str]
    instance_type: Optional[str]
    accelerators: Optional[str]
    ports: Optional[List[dict]]
    disk_size: Optional[int]
    spot: Optional[bool]
    ssh_info: Optional[List[dict]]

    created_timestamp: int
    updated_timestamp: int

    @classmethod
    def from_dict(cls, d):
        if d.get("status", None):
            d["status"] = ReplicaStatus(d["status"])
        else:
            d["status"] = None

        if d.get("cloud", None):
            d["cloud"] = Cloud(d["cloud"])

        replica = ServiceReplica(**d)
        return replica
