import json
import os
import subprocess
from dataclasses import dataclass

import jmespath  # installed via pip
import requests
from jupyter_server import serverapp
from typing import Optional

PORT_LABEL = "com.amazon.jupyter.activity.port"
ENDPOINT_LABEL = "com.amazon.jupyter.activity.endpoint"
RESPONSE_TEMPLATE_LABEL = "com.amazon.jupyter.activity.response"


@dataclass
class DockerSidecarActivityCheckerMetadata:
    container_id: str
    port: int
    endpoint: str
    response_template: str


def get_docker_path() -> Optional[str]:
    """Retrieve the path to the docker executable, if exists."""
    docker_path = subprocess.run(["which", "docker"], capture_output=True).stdout
    if not docker_path:
        # Docker isn't installed on this instance. No sidecars can be running.
        return None
    else:
        # Decode the docker path
        return docker_path.decode("utf-8").strip()


def get_all_sidecars(docker_path: str) -> list[str]:
    running_container_ids = subprocess.run(
        [docker_path, "container", "ls", "-q"],
        capture_output=True,
    ).stdout
    if not running_container_ids:
        return []
    else:
        return running_container_ids.decode("utf-8").strip().split("\n")


def register_sidecar_idle_checkers(
    docker_path: str,
) -> list[DockerSidecarActivityCheckerMetadata]:
    # first, go through all running containers, docker inspect and get their running ports
    sidecar_idle_checkers = []
    running_container_ids = get_all_sidecars(docker_path)
    for container_id in running_container_ids:
        container_labels = json.loads(
            subprocess.run(
                [
                    docker_path,
                    "inspect",
                    "--format",
                    "'{{json .Config.Labels}}'",
                    container_id,
                ],
                capture_output=True,
            )
            .stdout.decode("utf-8")
            .strip()[1:-1]
        )
        if all(
            [
                label in container_labels
                for label in [PORT_LABEL, ENDPOINT_LABEL, RESPONSE_TEMPLATE_LABEL]
            ]
        ):
            sidecar_idle_checkers.append(
                DockerSidecarActivityCheckerMetadata(
                    container_id=container_id,
                    port=container_labels[PORT_LABEL],
                    endpoint=container_labels[ENDPOINT_LABEL],
                    response_template=container_labels[RESPONSE_TEMPLATE_LABEL],
                )
            )
    return sidecar_idle_checkers


def check_if_sidecars_idle() -> bool:
    docker_path = get_docker_path()
    if not docker_path:
        # Docker isn't installed on this instance. No sidecars can be running.
        return True

    sidecar_idle_checkers = register_sidecar_idle_checkers(docker_path)
    try:
        BASE_URL = next(serverapp.list_running_servers())["url"]
    except StopIteration:
        return True
    # for each container, ping the idle endpoint and check the response
    all_sidecars_idle = True
    for checker in sidecar_idle_checkers:
        ping_url = BASE_URL + os.path.join(
            "proxy/absolute",
            checker.port,
            checker.endpoint,
        )
        try:
            response = requests.get(ping_url, timeout=2)
            if response.status_code == 200:
                sidecar_is_not_idle = (
                    jmespath.search(checker.response_template, response.json()) != 0
                )
                if sidecar_is_not_idle:
                    all_sidecars_idle = False
                    break
            else:
                continue
        except requests.exceptions.Timeout:
            continue

    return all_sidecars_idle
