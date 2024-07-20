# Copyright 2016-2023 Cerebras Systems
# SPDX-License-Identifier: BSD-3-Clause

"""Cerebras Configuration Class"""
import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Union
from warnings import warn

from cerebras.appliance.cluster.client import MountDir
from cerebras.appliance.cluster.config import (
    DEFAULT_JOB_PRIORITY,
    FABRIC_TYPE_CS2,
    FABRIC_TYPE_CS3,
    JOB_PRIORITY_P1,
    JOB_PRIORITY_P2,
    JOB_PRIORITY_P3,
    VALID_JOB_PRIORITIES,
)
from cerebras.appliance.cluster.job_timer import JobTimer
from cerebras.appliance.utils.debug_args import DebugArgs

_DEFAULT_NUM_CSX = 1
_DEFAULT_MAX_WGT_SERVERS = 24
_DEFAULT_MAX_ACT_PER_CSX = 60
_DEFAULT_TRANSFER_PROCESSES = 5
_DEFAULT_NUM_WORKERS_PER_CSX = 1
_DEFAULT_PRECISION_OPT_LEVEL = 1


@dataclass
class CSConfig:
    """Hold config details for WS Appliance Mode.

    Args:
        mgmt_address: Address to connect to appliance.
        mgmt_namespace: Namespace of cluster-mgmt software
            for internal multi-version support only.
        credentials_path: Credentials for connecting to appliance.
        num_csx: Number of Cerebras Systems to run on.
        max_wgt_servers: Number of weight servers to support run.
        max_act_per_csx: Number of activation servers per system.
        transfer_processes: Number of processes to transfer data to/from appliance.
        num_workers_per_csx: Number of streaming workers per system.
        job_labels: A list of equal-sign-separated key-value pairs that
            get applied as part of job metadata.
        job_priority: Priority of the job in scheduling queue.
        job_time_sec: Time limit for the appliance jobs, not including the queue time.
        workflow_id: ID to link multiple jobs together, where all linked jobs get similar priority.
        mount_dirs: Local storage to mount to appliance (ex. training data).
        python_paths: A list of path that worker pods respect as PYTHONPATH
            in addition to the PYTHONPATH set in the container image.
        debug_args: Optional debugging arguments object.
        precision_opt_level: The precision optimization level.
        disable_version_check: Whether to disable version check across client/server components.
    """

    mgmt_address: Optional[str] = None
    mgmt_namespace: Optional[str] = None
    credentials_path: Optional[str] = None

    num_csx: int = _DEFAULT_NUM_CSX
    max_wgt_servers: int = _DEFAULT_MAX_WGT_SERVERS
    max_act_per_csx: int = _DEFAULT_MAX_ACT_PER_CSX
    transfer_processes: int = _DEFAULT_TRANSFER_PROCESSES
    num_workers_per_csx: int = _DEFAULT_NUM_WORKERS_PER_CSX

    fabric_type_blacklist: Optional[List[str]] = None

    job_labels: List[str] = field(default_factory=list)
    job_priority: Optional[str] = DEFAULT_JOB_PRIORITY
    job_time_sec: Optional[int] = None
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mount_dirs: List[MountDir] = field(default_factory=list)
    python_paths: List[str] = field(default_factory=list)

    debug_args: DebugArgs = field(default_factory=DebugArgs)
    precision_opt_level: int = _DEFAULT_PRECISION_OPT_LEVEL

    disable_version_check: bool = False

    _job_timer: Optional[JobTimer] = field(default=None, init=False, repr=False)

    def __post_init__(self):  # pylint: disable=no-self-use
        warn(
            "CSConfig is deprecated. It will be removed in a future release. "
            "Please use ClusterConfig from cerebras.appliance.cluster_config instead."
        )

    @property
    def job_timer(self) -> Optional[JobTimer]:
        """Returns a cached job timer instance."""
        if self.job_time_sec is not None and self.job_time_sec > 0:
            if self._job_timer is None:
                self._job_timer = JobTimer(self.job_time_sec)
        return self._job_timer

    def __setattr__(self, key, val):
        """Override setter to sanitize values if needed."""
        if (
            sanitize := getattr(self, f"_sanitize_{key}", None)
        ) is not None and callable(sanitize):
            val = sanitize(val)
        super().__setattr__(key, val)

    # pylint: disable=no-self-use
    def _sanitize_job_labels(self, labels: Optional[List[str]]) -> List[str]:
        """Sanitize job labels."""
        pattern = r'^([A-Za-z0-9][-A-Za-z0-9_.]{0,61})?[A-Za-z0-9]$'

        labels = labels or []

        for kv_pair in labels:
            tokens = kv_pair.split("=")
            if len(tokens) != 2:
                raise ValueError(
                    f"'{kv_pair}' is an invalid label. Expecting the label key and "
                    f"the label value to be separated by a single equal sign(=) character."
                )
            for token in tokens:
                if re.match(pattern, token) is None:
                    raise ValueError(
                        f"'{kv_pair}' is an invalid label. Expecting the label key and the label "
                        f"value to match regex '{pattern}'."
                    )

        return labels

    # pylint: disable=no-self-use
    def _sanitize_job_priority(
        self, value: Optional[str]
    ) -> DebugArgs.DebugMGR.JobPriority:
        """Sanitize job priority"""
        # Valid job priorities are "p1", "p2" and "p3".
        priority_mapping = {
            JOB_PRIORITY_P1: DebugArgs.DebugMGR.JobPriority.JOB_PRIORITY_P1,
            JOB_PRIORITY_P2: DebugArgs.DebugMGR.JobPriority.JOB_PRIORITY_P2,
            JOB_PRIORITY_P3: DebugArgs.DebugMGR.JobPriority.JOB_PRIORITY_P3,
        }

        if value is not None and value not in VALID_JOB_PRIORITIES:
            raise ValueError(
                f"Invalid job priority value: {value} "
                f"(should be one of {VALID_JOB_PRIORITIES})"
            )
        return _value_or_default(
            priority_mapping.get(value),
            default=DebugArgs.DebugMGR.JobPriority.JOB_PRIORITY_P2,
        )

    def _sanitize_job_time_sec(self, job_time_sec: int) -> int:
        """Sanitize job timer."""
        if job_time_sec is not None and job_time_sec < 0:
            raise ValueError(
                f"Invalid job_time_sec {job_time_sec}. Expected a positive value or None."
            )
        self._job_timer = None
        return job_time_sec

    # pylint: disable=no-self-use
    def _sanitize_mgmt_address(self, mgmt_address: Optional[str]) -> str:
        """Sanitize mgmt_address."""
        pattern = r'.+:[0-9]+'
        if mgmt_address is not None and re.match(pattern, mgmt_address) is None:
            raise ValueError(
                f"mgmt_address '{mgmt_address}' should be in the form of '<name>:<port>'"
            )
        return mgmt_address

    # pylint: disable=no-self-use
    def _sanitize_mount_dirs(
        self, mount_dirs: Optional[List[Union[str, MountDir]]]
    ) -> List[MountDir]:
        """Sanitize mount directories."""
        s = set()
        for md in mount_dirs or []:
            if isinstance(md, (str, Path)):
                real_path = os.path.realpath(md)
                if not os.path.exists(real_path):
                    raise ValueError(f"Mount dir {real_path} does not exist")
                md = MountDir(path=md, container_path=md)
            s.add(md)
        return list(s)

    # pylint: disable=no-self-use
    def _sanitize_python_paths(self, paths: Optional[List[str]]) -> List[str]:
        """Sanitize python paths by turning them into their canonical path."""
        s = set()
        for x in paths or []:
            real_path = os.path.realpath(x)
            if not os.path.exists(real_path):
                raise ValueError(f"{real_path} does not exist")
            s.add(real_path)

        return list(s)

    # pylint: disable=no-self-use
    def _sanitize_num_csx(self, num_csx: Optional[int]) -> int:
        """Sanitize number of csx's requested."""
        return _value_or_default(num_csx, _DEFAULT_NUM_CSX)

    # pylint: disable=no-self-use
    def _sanitize_precision_opt_level(self, pol: Optional[int]) -> int:
        """Sanitize the precision opt level."""
        pol = _value_or_default(pol, _DEFAULT_PRECISION_OPT_LEVEL)

        if not isinstance(pol, int) or pol not in range(0, 3):
            raise ValueError(
                f"POL must be an integer in range [0, 3) but got {pol}."
            )
        return pol

    # pylint: disable=no-self-use
    def _sanitize_max_wgt_servers(self, value: Optional[int]) -> int:
        """Sanitize max_wgt_servers"""
        return _value_or_default(value, default=_DEFAULT_MAX_WGT_SERVERS)

    # pylint: disable=no-self-use
    def _sanitize_max_act_per_csx(self, value: Optional[int]) -> int:
        """Sanitize max_act_per_csx"""
        return _value_or_default(value, default=_DEFAULT_MAX_ACT_PER_CSX)

    # pylint: disable=no-self-use
    def _sanitize_transfer_processes(self, value: Optional[int]) -> int:
        """Sanitize transfer_processes"""
        return _value_or_default(value, default=_DEFAULT_TRANSFER_PROCESSES)

    # pylint: disable=no-self-use
    def _sanitize_num_workers_per_csx(self, value: Optional[int]) -> int:
        """Sanitize num_workers_per_csx"""
        return _value_or_default(value, default=_DEFAULT_NUM_WORKERS_PER_CSX)

    # pylint: disable=no-self-use
    def _sanitize_fabric_type_blacklist(
        self, fabric_type_blacklist: Optional[List[str]]
    ) -> str:
        """Sanitize fabric_type_blacklist."""
        # Valid fabric types are "cs2" and "cs3".
        if fabric_type_blacklist is not None:
            for fabric_type in fabric_type_blacklist:
                if fabric_type not in [FABRIC_TYPE_CS2, FABRIC_TYPE_CS3]:
                    raise ValueError(
                        f"unexpected fabric_type_blacklist: {fabric_type_blacklist} "
                        f"(should contain {FABRIC_TYPE_CS2} and/or {FABRIC_TYPE_CS3})"
                    )
        return fabric_type_blacklist


def _value_or_default(value: Optional[Any], default: Any) -> Any:
    """Return the value if not None, else return the default."""
    if value is None:
        return default
    return value
