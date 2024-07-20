#!/usr/bin/env python3
# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

""" Client implementation for interacting with Cluster Management."""

import copy
import datetime
import getpass
import json
import logging
import os
import shlex
import socket
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import timezone
from os import path
from pathlib import Path
from typing import Any, Dict, List, NamedTuple, Optional, Sequence, Tuple, Union

import grpc
import jwt
from google.protobuf.json_format import MessageToJson

from cerebras.appliance.cluster import cluster_logger
from cerebras.appliance.cluster.config import get_cs_cluster_config
from cerebras.appliance.cluster.job_timer import JobTimer
from cerebras.appliance.cluster.surrogate_job import get_surrogate_job
from cerebras.appliance.pb.workflow.appliance.cluster_mgmt import cluster_pb2
from cerebras.appliance.pb.workflow.appliance.cluster_mgmt.cluster_pb2_grpc import (
    ClusterManagementStub,
)
from cerebras.appliance.pb.workflow.appliance.cluster_mgmt.csctl import api_pb2
from cerebras.appliance.pb.workflow.appliance.cluster_mgmt.csctl.api_pb2_grpc import (
    CsCtlV1Stub,
)
from cerebras.appliance.pb.workflow.appliance.cluster_mgmt.csctl.v1.resources_pb2 import (
    VolumeList,
)
from cerebras.appliance.pb.workflow.appliance.common.common_config_pb2 import (
    ClusterDetails,
    DebugArgs,
    JobMode,
)
from cerebras.appliance.utils import Tracker

logger = cluster_logger.getChild("client")


@dataclass
class HeartBeatOptions:
    """Options to control appliance heartbeat signals."""

    cycle_seconds: int = 10
    cycle_threshold: int = 12
    lease_duration_seconds_override: int = 0

    def __post_init__(self) -> None:
        if self.cycle_seconds <= 0:
            raise ValueError(
                f"`cycle_seconds` must be greater than 0. "
                f"Got {self.cycle_seconds}."
            )
        if self.cycle_threshold <= 0:
            raise ValueError(
                f"`cycle_threshold` must be greater than 0. "
                f"Got {self.cycle_threshold}."
            )
        if self.lease_duration_seconds_override < 0:
            raise ValueError(
                f"`lease_duration_seconds_override` must be no less than 0. "
                f"Got {self.lease_duration_seconds_override}."
            )


class MountDir(NamedTuple):
    """
    A path to be mounted into the appliance containers.

    Parameters:
        path: Path to be mounted.
        container_path: Path that appears in the container. If no value was provided,
            then it will default to use the value of "path"
    """

    path: str
    container_path: str


class ClusterJobInitError(RuntimeError):
    def __init__(self, job_id: str, message: str, *args):
        super().__init__(*args)
        self.job_id = job_id
        self.message = message


CHUNK_SIZE = 1024 * 100
VENV_CLUSTER_VOLUME_TAG = "allow-venv"

RETRY_POLICY = {
    "methodConfig": [
        {
            "name": [
                {"service": "cluster.cluster_mgmt_pb.ClusterManagement"},
                {"service": "cluster.cluster_mgmt_pb.csctl.CsCtlV1"},
            ],
            "retryPolicy": {
                "maxAttempts": 5,
                "initialBackoff": "2s",
                "maxBackoff": "10s",
                "backoffMultiplier": 2,
                "retryableStatusCodes": [
                    "UNAVAILABLE",
                    "UNKNOWN",
                    "RESOURCE_EXHAUSTED",
                ],
            },
        }
    ]
}

AUTH_UID = "auth-uid"
AUTH_GID = "auth-gid"
AUTH_USERNAME = "auth-username"
AUTH_TOKEN = "auth-token"

# The actual user_auth_enabled will be obtained through GetServerConfig call.
is_user_auth_enabled = False


class _ClientCallDetailsFields(NamedTuple):
    method: str
    timeout: Optional[float]
    metadata: Optional[Sequence[Tuple[str, Union[str, bytes]]]]
    credentials: Optional[grpc.CallCredentials]
    wait_for_ready: Optional[bool]
    compression: Any


class ClientCallDetails(_ClientCallDetailsFields, grpc.ClientCallDetails):
    """Describes an RPC to be invoked.
    See https://grpc.github.io/grpc/python/grpc.html#grpc.ClientCallDetails.
    """


class JWToken:
    """
    Encoded JWT with helpers for decoding and returning properties.
    """

    def __init__(self, encoded: str):
        self._encoded = encoded
        if encoded:
            # Decode into a dict without verifying the HMAC
            self._decoded = jwt.decode(
                encoded, options={"verify_signature": False}
            )
        else:
            # Empty encoded token is empty claim
            self._decoded = {}

    def __str__(self):
        return self._encoded

    def will_expire_within(self, seconds: int):
        expiration_time = self._decoded.get("exp", 0)
        return expiration_time < time.time() + seconds


class AuthClientInterceptor(grpc.UnaryUnaryClientInterceptor):
    def __init__(self):
        def default_username() -> str:
            try:
                return getpass.getuser()
            # pylint: disable=broad-except
            except Exception as ex:
                logging.info(f"failed call to getpass.getuser: {ex}")
                return f"pid.{os.getpid()}"

        self._auth_metadata = [
            (AUTH_UID, str(os.getuid())),
            (AUTH_GID, str(os.getgid())),
            (AUTH_USERNAME, default_username()),
        ]
        if token := os.environ.get("CSAUTH_TOKEN", ""):
            self.token = JWToken(token)
        else:
            self.token = None

    def intercept_unary_unary(self, continuation, client_call_details, request):
        """Intercept all gRPC requests to add uid/gid.

        Params:
            continuation: A function that proceeds with the invocation by executing the next
                interceptor in the chain or invoking the actual RPC on the underlying
                channel.
            request: RPC request message.
            call_details: Describes an RPC to be invoked.

        Returns:
            The type of the return should match the type of the return value received
            by calling `continuation`. This is an object that is both a
            `Call <https://grpc.github.io/grpc/python/grpc.html#grpc.Call>`_ for the
            RPC and a `Future <https://grpc.github.io/grpc/python/grpc.html#grpc.Future>`_.
        """

        if self.token and self.token.will_expire_within(60):
            # Check the expiration date. If there is less than a minute left,
            # renew the JWT by expiring this token.
            self.token = None

        if not self.token and is_user_auth_enabled:
            get_cerebras_token_binary = "/usr/local/bin/get-cerebras-token"

            if not os.path.exists(get_cerebras_token_binary):
                raise RuntimeError(
                    f"UserAuth is enabled in the cluster but "
                    f"{get_cerebras_token_binary} does not exist on the "
                    f"user node. Please upgrade the user nodes."
                )

            try:
                output = subprocess.check_output(
                    [get_cerebras_token_binary]
                ).decode()
                if not output.startswith("Token="):
                    raise RuntimeError(
                        f"Unexpected token from "
                        f"{get_cerebras_token_binary}: {output}"
                    )
                self.token = JWToken(output[len("Token=") :])
            except subprocess.CalledProcessError as exp:
                raise RuntimeError(
                    f"Failed to call {get_cerebras_token_binary}: {exp}"
                )
        token = str(self.token) if self.token else ""
        auth_metadata = self._auth_metadata.copy()
        auth_metadata.append((AUTH_TOKEN, token))
        new_details = ClientCallDetails(
            client_call_details.method,
            client_call_details.timeout,
            auth_metadata,
            client_call_details.credentials,
            client_call_details.wait_for_ready,
            client_call_details.compression,
        )

        return continuation(new_details, request)


class ClusterManagementClient:
    """
    Cluster Management Client library that defines the interfaces to Cerebras appliance.
    """

    def __init__(
        self,
        server=None,
        crt_file=None,
        namespace="",
        job_timer: JobTimer = None,
        enable_client_lease_strategy=True,
        heartbeat_options=HeartBeatOptions(),
        options=None,
        workdir=None,
        tracker_execute=None,
        fabric_type_blacklist: Optional[List[str]] = None,
    ):
        csconfig_path, self.cs_cluster_config = get_cs_cluster_config()
        if namespace:
            self.namespace = namespace
            if not self.cs_cluster_config.namespace_exists(self.namespace):
                if not crt_file:
                    raise RuntimeError(
                        f"Usernode config {csconfig_path} does not have access to the "
                        f"{self.namespace} namespace. Please contact sysadmins for support."
                    )
                else:
                    logger.info(
                        f"Certificate {crt_file} is used to access the {namespace} namespace."
                    )
                    self._crt_bytes = Path(crt_file).read_bytes()
            else:
                self._crt_bytes = (
                    self.cs_cluster_config.get_namespace_certificate_authority(
                        self.namespace
                    ).certificate_authority_data
                )
        elif self.cs_cluster_config.namespaces:
            if len(self.cs_cluster_config.namespaces) == 1:
                self.namespace = self.cs_cluster_config.namespaces[0].name
                self._crt_bytes = (
                    self.cs_cluster_config.get_namespace_certificate_authority(
                        self.namespace
                    ).certificate_authority_data
                )
                logger.debug(
                    f"Defaulted to use the {self.namespace} namespace as the usernode config {csconfig_path} "
                    "only has access to that namespace."
                )
            elif len(self.cs_cluster_config.namespaces) == 0:
                raise RuntimeError(
                    f"Usernode config {csconfig_path} does not have access to any namespace. "
                    f"Please contact sysadmins for support."
                )
            else:
                namespace_names = [
                    namespace._name
                    for namespace in self.cs_cluster_config.namespaces
                ]
                raise RuntimeError(
                    f"Usernode config {csconfig_path} has access to multiple namespaces. "
                    f"Please select a namespace with the '--mgmt_namespace' option with one of {namespace_names}."
                )
        else:
            # This case most likely happens in local testing.
            # "namespace" was not provided and usernode config does not have access to any namespace
            self.namespace = 'job-operator'
            logger.warning(
                f"Defaulted to use the {self.namespace} namespace as it appears to be a dev environment."
            )
            if not crt_file:
                logger.warning(
                    "TLS certificate was not provided. Attempting to communicate with "
                    "the appliance in non-TLS insecure mode."
                )
                self._crt_bytes = b''
            else:
                logger.info(
                    f"Certificate {crt_file} is used to access the {self.namespace} namespace."
                )
                self._crt_bytes = Path(crt_file).read_bytes()

        if (
            fabric_type_blacklist is not None
            and self.cs_cluster_config.fabric_type in fabric_type_blacklist
        ):
            raise RuntimeError(
                f"Fabric type '{self.cs_cluster_config.fabric_type}' is not supported"
            )
        self.authority = f"{self.namespace}.{self.cs_cluster_config.authority}"

        self.server = server
        if not self.server:
            self.server = self.cs_cluster_config.mgmt_address
        if options is None:
            options = []
        self.enable_client_lease_strategy = enable_client_lease_strategy
        self.heartbeat_options = heartbeat_options
        self._heartbeat_thread = None
        self._heartbeat_stop = threading.Event()
        self.options = options
        self.options.append(('grpc.service_config', json.dumps(RETRY_POLICY)))
        self.options.append(('grpc.enable_retries', 1))
        # only add authority when crt specified
        if self._crt_bytes and self.authority:
            self.options.append(('grpc.default_authority', self.authority))
            # We usually connect via IP, but nginx-ingress is set up to do SNI
            # dependent cert lookup. In gRPC versions > 1.39, this is set
            # automatically to the gprc.default_authority, but in older
            # versions it needs to be manually set.
            self.options.append(
                ('grpc.ssl_target_name_override', self.authority)
            )
        self.channel = None
        self.stub = None
        self.csctl_stub = None
        self.hostname = socket.gethostname()
        self.workdir = Path(workdir) if workdir is not None else Path.cwd()
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.job_timer = job_timer
        # When using subdirectories, we expect artifact_dir to look like this:
        # .../cerebras_logs/<train|eval>/<timestamp>/executors/<id>/
        # run_meta.json is a shared file across all runs so it needs to be outside
        # of all subdirectories.
        if self.workdir.parent.parent.parent.parent.name == "cerebras_logs":
            self.run_meta_file = (
                self.workdir.parent.parent.parent.parent / "run_meta.json"
            )
        # In the new Trainer flow, there is no train/eval subdirectory.
        # So, the artifact directory is expected to look like this instead:
        # .../cerebras_logs/<timestamp>/executors/<id>/
        elif self.workdir.parent.parent.parent.name == "cerebras_logs":
            self.run_meta_file = (
                self.workdir.parent.parent.parent / "run_meta.json"
            )
        else:
            self.run_meta_file = self.workdir / "run_meta.json"
        self.run_meta_file = str(self.run_meta_file)
        self.image_build_log_file = path.join(
            self.workdir, f"custom_worker_build.out"
        )
        self._current_job = None
        self._is_wsjob = None
        self.grpc_fork_support_value = None
        self.is_message_broker_available = False

        # create a dummy tracker if one is not passed
        self._tracker_execute = tracker_execute or Tracker()

        logger.debug(
            f"ClusterClient"
            f": server={self.server}"
            f", authority={self.authority}"
            f", cert={'EMPTY' if not self._crt_bytes else 'OMITTED'}"
            f", enable-client-lease-strategy={self.enable_client_lease_strategy}"
            f", heartbeat_options={self.heartbeat_options}"
            f", options={self.options}"
        )

        self.surrogate_job = get_surrogate_job(logger, self.workdir)

    def __enter__(self):
        self.validate_connectivity()
        self.grpc_fork_support_value = os.environ.get(
            'GRPC_ENABLE_FORK_SUPPORT', None
        )
        # SW-89390: To suppress the spam messages from gRPC library
        os.environ.update({'GRPC_ENABLE_FORK_SUPPORT': '0'})
        interceptors = [AuthClientInterceptor()]
        if not self._crt_bytes:
            self.channel = grpc.insecure_channel(self.server, self.options)
        else:
            creds = grpc.ssl_channel_credentials(self._crt_bytes)
            self.channel = grpc.secure_channel(self.server, creds, self.options)
        self.channel = grpc.intercept_channel(self.channel, *interceptors)
        self.stub = ClusterManagementStub(self.channel)
        self.csctl_stub = CsCtlV1Stub(self.channel)

        self.check_user_auth_enabled()
        self.check_message_broker_availability()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop_heartbeat()
        self.stop_surrogate()

        if self.job_timer:
            self.job_timer.unregister_client(self)

        self.channel.close()
        self._current_job = None
        self._is_wsjob = None
        if self.grpc_fork_support_value is not None:
            os.environ.update(
                {'GRPC_ENABLE_FORK_SUPPORT': self.grpc_fork_support_value}
            )
        else:
            del os.environ['GRPC_ENABLE_FORK_SUPPORT']

    def _poll_ingress_readiness(self, job_id):
        self._tracker_execute.start("scheduler_wait")
        retries = 0
        while True:
            # request grpc error will auto retry based on our policy
            responses = self.stub.PollIngressV2(
                cluster_pb2.GetIngressRequest(job_id=job_id),
                wait_for_ready=True,
            )
            # stream iteration is not caught as grpc retryable error, need explicit retry
            try:
                for response in responses:
                    if response.is_scheduled:
                        self._tracker_execute.stop("scheduler_wait")
                        self._log_scheduling_events(job_id)
                    if response.is_ready:
                        self._tracker_execute.stop("scheduler_wait")
                        logger.info(f"Ingress is ready: {response.message}")
                        self.dump_job_meta(job_id=job_id)
                        return response
                    if response.job_failed:
                        logger.error(
                            f"Job {job_id} failed during initialization: {response.message}"
                        )
                        raise ClusterJobInitError(job_id, response.message)
                    logger.info(f"Poll ingress status: {response.message}")
            except grpc.RpcError as e:
                # retry for 1min since it should not happen
                if retries < 12:
                    logger.warning(
                        f"Retry on poll ingress error: {e.code()}, {e.details()}"
                    )
                    retries += 1
                    # give enough time in case of server restart
                    time.sleep(5)
                    continue
                logger.error(f"Poll ingress for {job_id} failed: {e.details()}")
                raise e

    def _log_scheduling_events(self, job_id):
        job_events_resp = self.stub.GetJobEvents(
            cluster_pb2.GetJobEventsRequest(job_id=job_id),
        )
        for event in job_events_resp.job_events:
            msg = str(
                f"Event {event.lastTimestamp} reason={event.reason.strip()} "
                f"wsjob={event.name.strip()} message='{event.message.strip()}'"
            )
            logger.warning(msg)

    def _get_curr_time(self):
        return datetime.datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

    def _put_run_meta(self, run_meta_dict):
        with open(self.run_meta_file, "w+") as meta_file:
            json.dump(run_meta_dict, meta_file, indent=4)

    def _update_job_run_meta(
        self, job_mode: JobMode.Job, job_id, new_prop_dict
    ):
        run_meta_dict = self.get_run_meta()
        job_mode_string = JobMode.Job.Name(job_mode).lower()
        if f"{job_mode_string}_jobs" not in run_meta_dict:
            logger.warning(
                f"There is no existing {job_mode_string} job record."
            )
            return

        jobs = run_meta_dict[f"{job_mode_string}_jobs"]
        job = None
        for j in jobs:
            if j["id"] != job_id:
                continue
            job = j
            break

        if not job:
            logger.warning(
                f"There is no {job_mode_string} job record with the id {job_id}"
            )
            return

        job.update(new_prop_dict)
        self._put_run_meta(run_meta_dict)

    def get_image_build_log_path(self):
        return self.image_build_log_file

    def _put_image_build_logs(self, build_log_content):
        with open(self.image_build_log_file, "w+") as log_file:
            log_file.write(build_log_content)

    def start_heartbeat(self, job_id) -> None:
        if not self.enable_client_lease_strategy:
            return

        # First stop the thread if not stopped
        if (
            self._heartbeat_thread is not None
            and not self._heartbeat_stop.is_set()
        ):
            logger.warning(f"Stopping the existing heartbeat thread.")
            self._heartbeat_stop.set()
            self._heartbeat_thread.join(timeout=1)

        logger.debug(
            f"Starting heartbeat thread for {job_id}. Heartbeat requests will be sent "
            f"every {self.heartbeat_options.cycle_seconds} seconds."
        )

        self._heartbeat_stop = threading.Event()
        self._heartbeat_thread = threading.Thread(
            target=_start_heartbeat_thread,
            args=(
                self.stub,
                copy.deepcopy(self.heartbeat_options),
                job_id,
                self._heartbeat_stop,
            ),
            name="cluster_client_heartbeat_thread",
            daemon=True,
        )
        self._heartbeat_thread.start()

    def stop_heartbeat(self) -> None:
        """Command to stop heartbeats with cluster server."""
        if not self.enable_client_lease_strategy:
            return

        if not self._heartbeat_stop.is_set() and self._is_wsjob:
            logger.debug(
                f"Signaling heartbeat thread to stop for {self._current_job}"
            )
            self._heartbeat_stop.set()
            self._heartbeat_thread.join(timeout=1)

    def init_compile_job(
        self,
        compile_dir_relative_path,
        job_mode,
        debug_args: DebugArgs,
        # This is only a test handle and will not be used in production
        skip_ingress_creation=False,
    ) -> Dict[str, Any]:
        if self.surrogate_job:
            (label_key, label_value) = self.surrogate_job.get_job_label()
            debug_args.debug_mgr.labels[label_key] = label_value

        request = cluster_pb2.CompileJobRequest(
            compile_dir_relative_path=compile_dir_relative_path,
            job_mode=job_mode,
            client_workdir=f"{self.hostname}:{self.workdir.absolute()}",
            debug_args=debug_args,
            debug_args_json=MessageToJson(
                debug_args, sort_keys=True, indent=None
            ),
        )
        logger.info(
            "Initiating a new compile wsjob against the cluster server."
        )
        init_response = self.stub.InitCompileJob(request)
        self._current_job = init_response.job_id
        self._is_wsjob = True
        self.log_job(
            job_mode.job,
            init_response.job_id,
            init_response.log_path,
            debug_args.debug_mgr.workflow_id,
        )

        job_props = {
            "compile_dir_absolute_path": init_response.compile_dir_absolute_path,
        }
        return self.get_job_handle(
            init_response.job_id, "", job_props, skip_ingress_creation
        )

    def init_execute_job(
        self,
        compile_artifact_dir,
        job_mode,
        debug_args: DebugArgs,
        mount_dirs: Optional[List[MountDir]] = None,
        python_paths: Optional[List[str]] = None,
        # This is only a test handle and will not be used in production
        skip_ingress_creation=False,
    ) -> Dict[str, Any]:
        if self.surrogate_job:
            (label_key, label_value) = self.surrogate_job.get_job_label()
            debug_args.debug_mgr.labels[label_key] = label_value

        if mount_dirs:
            mount_dirs = [
                cluster_pb2.MountDir(**md._asdict()) for md in mount_dirs
            ]
        request = cluster_pb2.ExecuteJobRequest(
            compile_artifact_dir=compile_artifact_dir,
            job_mode=job_mode,
            debug_args=debug_args,
            client_workdir=f"{self.hostname}:{self.workdir.absolute()}",
            mount_dirs=mount_dirs,
            python_paths=python_paths,
            debug_args_json=MessageToJson(
                debug_args, sort_keys=True, indent=None
            ),
        )
        logger.info(
            "Initiating a new execute wsjob against the cluster server."
        )
        with self._tracker_execute.entry("job_initializing"):
            init_response = self.stub.InitExecuteJob(request)
        self._current_job = init_response.job_id
        self._is_wsjob = True
        self.log_job(
            job_mode.job,
            init_response.job_id,
            init_response.log_path,
            debug_args.debug_mgr.workflow_id,
        )

        job_props = {
            "compile_artifact_dir": compile_artifact_dir,
        }

        # Get the number of CS2s so we can append it to the SLURM surrogate job name
        num_cs2 = 0
        for task in job_mode.cluster_details.tasks:
            if task.task_type == ClusterDetails.TaskInfo.TaskType.WSE:
                num_cs2 = len(task.task_map)
                break
        if num_cs2 > 0:
            num_cs2_str = "-csx" + str(num_cs2)
        else:
            num_cs2_str = ""

        return self.get_job_handle(
            init_response.job_id,
            num_cs2_str,
            job_props,
            skip_ingress_creation,
        )

    def init_sdk_compile_job(
        self, job_mode, compile_dir_relative_path, skip_ingress_creation=False
    ):
        if job_mode.job != JobMode.Job.SDK_COMPILE:
            raise RuntimeError(
                f"Unexpected job {job_mode.job} (expecting SDK_COMPILE)"
            )

        request = cluster_pb2.SdkCompileJobRequest(
            job_mode=job_mode,
            compile_dir_relative_path=compile_dir_relative_path,
        )
        logger.info(
            "Initiating a new SDK compile job against the cluster server"
        )
        response = self.stub.InitSdkCompileJob(request)
        self._current_job = response.job_id
        self._is_wsjob = True
        # SDK compile job does not provide a workflow id
        self.log_job(job_mode.job, response.job_id, response.log_path, "")
        return self.get_job_handle(
            response.job_id, "", {}, skip_ingress_creation
        )

    def init_sdk_execute_job(self, job_mode, skip_ingress_creation=False):
        if job_mode.job != JobMode.Job.SDK_EXECUTE:
            raise RuntimeError(
                f"Unexpected job {job_mode.job} (expecting SDK_EXECUTE)"
            )

        request = cluster_pb2.SdkExecuteJobRequest(
            job_mode=job_mode,
        )
        logger.info(
            "Initiating a new SDK execute job against the cluster server"
        )
        response = self.stub.InitSdkExecuteJob(request)
        self._current_job = response.job_id
        self._is_wsjob = True
        # SDK execute job does not provide a workflow id
        self.log_job(job_mode.job, response.job_id, response.log_path, "")
        return self.get_job_handle(
            response.job_id, "", {}, skip_ingress_creation
        )

    def init_image_build_job(
        self,
        pip_options: Optional[str] = None,
        frozen_dependencies: Optional[List[str]] = None,
        base_image_override: Optional[str] = None,
        workdir_hostpath_override: Optional[str] = None,
    ) -> cluster_pb2.ImageBuildResponse:
        request = cluster_pb2.InitImageBuildRequest(
            pip_options=pip_options,
            frozen_dependencies=frozen_dependencies,
            base_image_override=base_image_override,
            workdir_hostpath_override=workdir_hostpath_override,
        )
        logger.info(
            f"Initiating a new image build job against the cluster server."
        )
        init_response = self.stub.InitImageBuildJob(request)
        self._current_job = init_response.job_id
        self._is_wsjob = False
        # Image build job does not provide a workflow id
        self.log_job(
            JobMode.Job.IMAGE_BUILD,
            init_response.job_id,
            init_response.log_path,
            "",
        )
        self._log_image_reference(
            init_response.job_id,
            init_response.image_reference,
            init_response.image_ready,
        )
        return init_response

    def get_server_versions(self) -> Dict[str, str]:
        """Return a map of server versions, including cluster-server and job-operator."""
        request = cluster_pb2.GetServerVersionsRequest()
        response = self.stub.GetServerVersions(request)
        return response.versions

    def get_job_handle(
        self,
        job_id,
        num_cs2_suffix,
        job_props,
        skip_ingress_creation,
    ) -> Dict[str, Any]:
        self.start_heartbeat(job_id)

        response = {"job_id": job_id}
        if skip_ingress_creation:
            return response

        ingress_response = self._poll_ingress_readiness(job_id)
        response["service_authority"] = f"{ingress_response.service_authority}"
        response["service_url"] = self.server
        if ingress_response.service_url:
            response["service_url"] = str(ingress_response.service_url)
        response["certificate_bytes"] = self._crt_bytes

        # Append the number of CSX
        self.start_surrogate(job_id, num_cs2_suffix)

        logger.debug(f"Cluster mgmt job handle: {response}")

        if self.job_timer:
            self.job_timer.register_client(self)

        response.update(job_props)
        return response

    def get_run_meta(self):
        run_meta_dict = {}
        if path.exists(self.run_meta_file):
            try:
                with open(self.run_meta_file, "r") as meta_file:
                    run_meta_dict = json.load(meta_file)
            except:
                pass

        return run_meta_dict

    def dump_job_meta(self, job_id):
        """Retrieve fully populated cluster details, software versions and system versions."""
        request = cluster_pb2.GetJobMetaRequest(job_id=job_id)
        response = self.stub.GetJobMeta(request)

        with open(self.workdir / f"{job_id}-cluster-details.json", "w") as f:
            f.write(MessageToJson(response.cluster_details, indent=4))

        software_versions = dict(response.software_versions)
        from cerebras.appliance import __version__

        software_versions["appliance-client"] = __version__
        _sorted = {k: software_versions[k] for k in sorted(software_versions)}
        self._update_job_run_meta(
            response.job_mode, job_id, {"software_versions": _sorted}
        )

        system_versions = dict(response.system_versions)
        _sorted = {}
        for k in sorted(system_versions):
            serialized_software_versions = system_versions[k]
            system_version_details = json.loads(serialized_software_versions)
            attrs = ["product", "execmode", "components"]
            _sorted[k] = {
                _k: system_version_details[_k]
                for _k in attrs
                if _k in system_version_details
            }
        self._update_job_run_meta(
            response.job_mode, job_id, {"system_versions": _sorted}
        )

    def log_job(self, job_mode: JobMode.Job, job_id, log_path, workflow_id):
        """
        Write various job metadata (including namesapce, job_id, workflow_id) to run_meta_file.
        """
        run_meta_dict = self.get_run_meta()
        job_mode_string = JobMode.Job.Name(job_mode).lower()
        if f"{job_mode_string}_jobs" not in run_meta_dict:
            run_meta_dict[f"{job_mode_string}_jobs"] = []

        run_meta_dict[f"{job_mode_string}_jobs"].append(
            {
                "namespace": self.namespace,
                "id": job_id,
                "workflow_id": workflow_id,
                "log_path": log_path,
                "start_time": self._get_curr_time(),
            }
        )

        self._put_run_meta(run_meta_dict)

        logger.debug(f"Run meta is available at {self.run_meta_file}.")
        if job_id and log_path:
            logger.info(
                f"{job_mode_string.capitalize()} job id: {job_id}, "
                f"remote log path: {log_path}"
            )

    def log_cache_compile(self, job_id, cache_compile_dir):
        prefix = ""
        if self.stub:
            response = self.stub.HasMultiMgmtNodes(
                cluster_pb2.HasMultiMgmtNodesRequest()
            )
            if response.has_multi_mgmt_nodes:
                prefix = "pvc:"
        prop_dict = {
            "cache_compile": {
                "location": prefix + cache_compile_dir,
                "available_time": self._get_curr_time(),
            },
        }
        self._update_job_run_meta(JobMode.Job.COMPILE, job_id, prop_dict)

    def _log_image_reference(self, job_id, image_ref, image_ready):
        prop_dict = {
            "image": {
                "reference": image_ref,
                "ready": image_ready,
            },
        }
        if image_ready:
            prop_dict["image"]["available_time"] = self._get_curr_time()
        self._update_job_run_meta(JobMode.Job.IMAGE_BUILD, job_id, prop_dict)

    def get_latest_job(self):
        """
        Retrieve the latest job reference mostly for testing purposes.
        """
        run_meta_dict = self.get_run_meta()
        if not run_meta_dict:
            return None

        # Flattens the job list regardless of job types
        jobs = [job for job_list in run_meta_dict.values() for job in job_list]
        jobs_sorted_by_time = sorted(jobs, key=lambda x: x["start_time"])

        return None if not jobs_sorted_by_time else jobs_sorted_by_time[-1]

    def get_job(self, job_id):
        """Get Job Request."""
        request = cluster_pb2.GetJobRequest(
            job_id=job_id,
        )
        return self.stub.GetJob(request)

    def get_image_build_job(self, job_id, image_reference=None):
        """Get image build job request."""
        request = cluster_pb2.ImageBuildRequest(
            job_id=job_id,
            image_reference=image_reference,
        )
        response = self.stub.GetImageBuildJob(request)
        if response.image_ready:
            self._log_image_reference(
                response.job_id, response.image_reference, response.image_ready
            )
        if response.build_log_content:
            self._put_image_build_logs(response.build_log_content)
        return response

    def delete_job(self, job_id):
        """Delete existing Job Request."""
        request = cluster_pb2.DeleteJobRequest(
            job_id=job_id,
        )
        return self.stub.DeleteJob(request)

    def delete_image_build_job(self, job_id):
        """Delete existing image job request."""
        request = cluster_pb2.ImageBuildRequest(
            job_id=job_id,
        )
        return self.stub.DeleteImageBuildJob(request)

    def cancel_job(self, job_id, job_status):
        """Cancel existing Job Request."""
        request = cluster_pb2.CancelJobRequest(
            job_id=job_id,
            job_status=job_status,
        )
        response = cluster_pb2.CancelJobResponse()
        try:
            response = self.stub.CancelJobV2(request)
        except grpc.RpcError as e:
            logger.error(f"Cancelling {job_id} failed: {e.details()}")
        else:
            self.stop_heartbeat()
        return response

    def start_surrogate(self, job_id, num_cs2_suffix=""):
        """Start surrogate job."""
        if self.surrogate_job:
            # TODO(joy): should lift this up to the constructor later.
            namespace = self.namespace if self.namespace else 'job-operator'
            self.surrogate_job.start(job_id, namespace, num_cs2_suffix)

    def stop_surrogate(self):
        """Stop surrogate job."""
        if self.surrogate_job:
            # There is a time gap between the wsjob completing and the client exiting.
            # Here, we wait for all appliance jobs to complete before stopping the surrogate
            # jobs. Otherwise, the surrogate job might find the job in progress and try to
            # cancel it.
            for job in self.surrogate_job.get_appliance_jobs():
                while job and True:
                    response = self.get_job(job)
                    logger.debug(
                        f"Wait for job {job} to complete. Current status {response.status}"
                    )
                    if response.status != cluster_pb2.JOB_STATUS_IN_PROGRESS:
                        break
                    time.sleep(1)
            self.surrogate_job.stop()

    def cancel(self):
        """Cancel the current running job."""
        if self._current_job:
            if self._is_wsjob:
                self.cancel_job(self._current_job, "JOB_STATUS_CANCELLED")
            else:
                self.delete_image_build_job(self._current_job)
            self._current_job = None
            self._is_wsjob = None

    # workaround to check if address is accessible to avoid grpc infinite retry at connect time
    def validate_connectivity(self):
        # skip for test cases
        if "localhost" in self.server:
            return
        try:
            subprocess.check_output(
                shlex.split(f"ping -c 1 -W 3 {self.server.split(':')[0]}")
            )
        except subprocess.CalledProcessError as e:
            logger.error(
                f"Failed to ping cluster mgmt svc: {self.server}, please check network, err: {e}"
            )
            raise e

    def check_message_broker_availability(self):
        response = self.stub.IsMessageBrokerAvailable(
            cluster_pb2.MessageBrokerAvailabilityCheckRequest()
        )
        self.is_message_broker_available = response.is_available

    def check_user_auth_enabled(self):
        global is_user_auth_enabled
        try:
            response = self.stub.GetServerConfig(
                cluster_pb2.GetServerConfigRequest()
            )
            is_user_auth_enabled = response.is_user_auth_enabled
        except grpc.RpcError as exp:
            if exp.code() == grpc.StatusCode.UNIMPLEMENTED:
                # Assume that user auth is not enabled, to support backward compatibility
                logger.error(
                    f"Unimplemented error occurred while getting server config: {exp}. Assume user auth disabled."
                )
                is_user_auth_enabled = False
            else:
                raise exp

    def publish_messages(self, job_id, message_iterator, max_attempts=5):
        if not self.is_message_broker_available:
            logger.warning(
                "Message broker is not available hence skipping publishing messages."
            )
            return

        def request_generator():
            init_msg = cluster_pb2.PublishMessagesRequest(job_id=job_id)
            yield init_msg  # send the initialization message first
            for message in message_iterator:
                yield cluster_pb2.PublishMessagesRequest(message=message)

        for i in range(max_attempts):
            try:
                self.stub.PublishMessages(request_generator())
                logger.debug(
                    "Published all messages from the message iterator."
                )
                break
            except grpc.RpcError as e:
                logger.error(f"Error occurred while publishing messages: {e}")
                if i < max_attempts - 1:
                    time.sleep(2**i)
                else:
                    raise e

    def subscribe_messages(self, job_id, from_beginning, max_attempts=5):
        if not self.is_message_broker_available:
            logger.warning(
                "Message broker is not available hence skipping subscribing messages."
            )
            return

        consecutive_errors = 0
        while True:
            try:
                req = cluster_pb2.SubscribeMessagesRequest(
                    job_id=job_id, from_beginning=from_beginning
                )
                responses = self.stub.SubscribeMessages(req)
                consecutive_errors = 0
                for response in responses:
                    yield response.message
            except grpc.RpcError as e:
                logger.error(f"Error occurred while polling messages: {e}")
                if consecutive_errors < max_attempts:
                    consecutive_errors += 1
                    time.sleep(2**consecutive_errors)
                else:
                    raise e

    def get_volumes(self):
        volume_list = VolumeList()
        try:
            result = self.csctl_stub.Get(
                api_pb2.GetRequest(
                    type="volumes",
                    accept=api_pb2.PROTOBUF_METHOD,
                    representation=api_pb2.OBJECT_REPRESENTATION,
                    options=api_pb2.GetOptions(namespace=self.namespace),
                )
            )
            volume_list.ParseFromString(result.raw)
        except Exception as e:
            raise RuntimeError(f"Failed to get volumes:{self.namespace}/{e}")
        return volume_list

    def get_user_venv_cluster_volume_path(
        self, venv_src: Path
    ) -> Tuple[bool, str]:
        """
        Retrieve cluster volume path for staging the user virtual environment over NFS.
        Return value is a tuple where the first element in the tuple indicates whether
        venv copying should be honored, and the second element is the cluster volume path
        that the user-node virtual environment should be replicated to.

        In the event where the user-node virtual environment is on a cluster volume path
        already, we do not need to replicate the environment again over NFS.
        """
        logger.debug(f"start checking venv with src: {venv_src}")
        volume_list = self.get_volumes()
        try:
            for vol in volume_list.items:
                logger.debug(f"start validating cluster vol: {vol}")
                mount_path = (
                    vol.nfs.container_path
                    if vol.nfs.container_path
                    else vol.host_path.container_path
                )
                is_nfs_volume = True if vol.nfs.container_path else False
                if is_nfs_volume and str(venv_src).startswith(mount_path):
                    # Does not require replicating the virtual environment
                    # if the source venv is already on a NFS volume
                    return False, ""

                if vol.meta.labels.get(VENV_CLUSTER_VOLUME_TAG) != "true":
                    logger.debug(
                        f"Cluster volume {vol.meta.name} is not a venv-allowed volume, skip to check next volume"
                    )
                    continue

                if not Path(mount_path).exists():
                    logger.debug(
                        f"Cluster volume {vol.meta.name} is not set up on the user node: {mount_path}, "
                        f"skip to check next volume"
                    )
                    continue

                try:
                    cmd = f"df {mount_path} --output=fstype"
                    result = subprocess.run(
                        cmd.split(), capture_output=True, text=True, check=True
                    )
                    lines = str(result.stdout).strip().split("\n")
                    if len(lines) > 1:
                        fs_type = lines[1]
                        if fs_type.startswith('nfs') == is_nfs_volume:
                            logger.info(
                                f"User venv cluster volume {vol.meta.name} on {mount_path} validated."
                            )
                            return True, mount_path
                        else:
                            logger.warning(
                                f"{vol.meta.name} on {mount_path} is {fs_type} but inconsistent with cluster setup, "
                                f"skip to check next volume"
                            )
                except subprocess.CalledProcessError as e:
                    logger.warning(
                        f"An error occurred while checking the filesystem for {mount_path}: {e}"
                    )
        except Exception as e:
            raise RuntimeError(
                f"Failed to parse cluster volume path for user venv: {e}"
            )

        raise RuntimeError(
            f"No valid cluster volume was set up to allow user venv mounting on this user node. "
            f"Please contact your organization's sysadmin to configure one."
        )


def _start_heartbeat_thread(
    stub: ClusterManagementStub,
    options: HeartBeatOptions,
    job_id: str,
    stop_event: threading.Event,
    timeout: int = 1,
) -> None:
    """Thread that continuously sends heartbeat signals to the cluster server.

    Args:
        stub: The client to use for sending the heartbeat signals.
        options: HeartBeat configuration options.
        job_id: The job which should send heartbeats to.
        stop_event: Event that will stop the heartbeat thread when set.
        timeout: Timeout for the heartbeat RPC.
    """
    failure_count = 0
    # wait one cycle to send HB in case lease not created yet
    while not stop_event.wait(options.cycle_seconds):
        try:
            request = cluster_pb2.HeartbeatRequest(
                job_id=job_id,
                lease_duration_seconds_override=options.lease_duration_seconds_override,
            )
            stub.SendClientHeartbeat(request, timeout=timeout)
            if failure_count:
                logger.debug(
                    f"Heartbeat({job_id}) to the Appliance succeeded after "
                    f"{failure_count} consecutive failures."
                )
            failure_count = 0
        except grpc.RpcError as rpc_error:
            rpc_error_code = rpc_error.code()  # pylint: disable=no-member
            failure_count += 1
            # We decided to change the logging level from warning to debug due to the
            # liveness check is not particularly interested to ML users and had raised
            # confusion. In the future when we decide to formally support internal
            # client side logs, we should raise the logging level here again.
            # Ref: SW-98069
            logger.debug(
                f"Heartbeat({job_id}) to the Appliance failed with error code "
                f"`{rpc_error_code.name}` (consecutive failure count: "
                f"{failure_count}). Retrying in {options.cycle_seconds} "
                f"seconds."
            )
            if failure_count == options.cycle_threshold:
                logger.debug(
                    f"Heartbeat({job_id}) failure count, {failure_count}, has exceeded "
                    f"the threshold. The Appliance will begin self-destructing "
                    f"soon as it hasn't heard from the client for longer than 2 minutes."
                )

    logger.debug(f"Heartbeat thread stopped for {job_id}.")
