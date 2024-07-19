import json
from typing import Optional
from dataclasses import dataclass
from jupyter_activity_monitor_extension.docker_sidecar_check import (
    DockerSidecarActivityCheckerMetadata,
    get_docker_path,
    get_all_sidecars,
    register_sidecar_idle_checkers,
    check_if_sidecars_idle,
    PORT_LABEL,
    ENDPOINT_LABEL,
    RESPONSE_TEMPLATE_LABEL,
)
from unittest.mock import patch

mock_container_labels = {
    PORT_LABEL: "8080",
    ENDPOINT_LABEL: "mock/idle/endpoint",
    RESPONSE_TEMPLATE_LABEL: "mockresponsetemplate",
}


@dataclass
class MockCompletedResponse:
    stdout: bytes


@dataclass
class MockResponse:
    status_code: int
    content: Optional[str] = None

    def json(self):
        return json.loads(self.content)


@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.subprocess.run",
    side_effect=[MockCompletedResponse(stdout=b"")],
)
def test_get_docker_path_when_docker_not_installed(mock_subprocess_run):
    actual = get_docker_path()
    assert actual == None


@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.subprocess.run",
    side_effect=[MockCompletedResponse(stdout=b"/usr/var/docker")],
)
def test_get_docker_path_when_docker_installed(mock_subprocess_run):
    actual = get_docker_path()
    assert actual == "/usr/var/docker"


@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.subprocess.run",
    side_effect=[
        MockCompletedResponse(stdout=b""),
    ],
)
def test_register_sidecar_idle_checkers_when_no_sidecars_running(mock_subprocess_run):
    sidecar_metadata = register_sidecar_idle_checkers(docker_path="usr/var/docker")
    assert sidecar_metadata == []


@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.subprocess.run",
    side_effect=[
        MockCompletedResponse(stdout=b"container1\ncontainer2\n"),
        MockCompletedResponse(
            stdout=(f"'{json.dumps(mock_container_labels)}'").encode()
        ),
        MockCompletedResponse(
            stdout=("'" + json.dumps({"dummy.label": "value"}) + "'").encode()
        ),
    ],
)
def test_register_sidecar_idle_checkers_when_sidecars_running(mock_subprocess_run):
    sidecar_metadata = register_sidecar_idle_checkers(docker_path="usr/var/docker")
    assert sidecar_metadata == [
        DockerSidecarActivityCheckerMetadata(
            container_id="container1",
            port="8080",
            endpoint="mock/idle/endpoint",
            response_template="mockresponsetemplate",
        )
    ]


@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.get_docker_path",
    side_effect=["usr/bin/docker"],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.register_sidecar_idle_checkers",
    side_effect=[[]],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.serverapp.list_running_servers",
    side_effect=[iter([{"url": "http://default:8888/jupyterlab/default"}])],
)
def test_docker_sidecar_check_when_no_sidecars_running(
    mock_running_servers,
    mock_register_sidecar_idle_checkers,
    mock_docker_path,
):
    actual = check_if_sidecars_idle()
    assert actual is True


@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.get_docker_path",
    side_effect=["usr/bin/docker"],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.register_sidecar_idle_checkers",
    side_effect=[
        [
            DockerSidecarActivityCheckerMetadata(
                container_id="container1",
                port="8080",
                endpoint="mock/idle/endpoint",
                response_template="mockresponsetemplate",
            )
        ]
    ],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.serverapp.list_running_servers",
    side_effect=[iter([{"url": "http://default:8888/jupyterlab/default"}])],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.requests.get",
    side_effect=[
        MockResponse(status_code=200, content=json.dumps({"mockresponsetemplate": 1}))
    ],
)
def test_docker_sidecar_check_when_sidecar_is_running_and_is_not_idle(
    mock_response,
    mock_running_servers,
    mock_register_sidecar_idle_checkers,
    mock_docker_path,
):
    actual = check_if_sidecars_idle()
    assert actual is False


@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.get_docker_path",
    side_effect=["usr/bin/docker"],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.register_sidecar_idle_checkers",
    side_effect=[
        [
            DockerSidecarActivityCheckerMetadata(
                container_id="container1",
                port="8080",
                endpoint="mock/idle/endpoint",
                response_template="mockresponsetemplate",
            )
        ]
    ],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.serverapp.list_running_servers",
    side_effect=[iter([{"url": "http://default:8888/jupyterlab/default"}])],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.requests.get",
    side_effect=[
        MockResponse(status_code=200, content=json.dumps({"mockresponsetemplate": 0}))
    ],
)
def test_docker_sidecar_check_when_sidecar_is_running_and_is_idle(
    mock_response,
    mock_running_servers,
    mock_register_sidecar_idle_checkers,
    mock_docker_path,
):
    actual = check_if_sidecars_idle()
    assert actual is True


@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.get_docker_path",
    side_effect=["usr/bin/docker"],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.register_sidecar_idle_checkers",
    side_effect=[
        [
            DockerSidecarActivityCheckerMetadata(
                container_id="container1",
                port="8080",
                endpoint="mock/idle/endpoint",
                response_template="mockresponsetemplate",
            )
        ]
    ],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.serverapp.list_running_servers",
    side_effect=[iter([{"url": "http://default:8888/jupyterlab/default"}])],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.requests.get",
    side_effect=[MockResponse(status_code=404)],
)
def test_docker_sidecar_check_when_idle_endpoint_is_unreachable(
    mock_response,
    mock_running_servers,
    mock_register_sidecar_idle_checkers,
    mock_docker_path,
):
    actual = check_if_sidecars_idle()
    assert actual is True


@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.get_docker_path",
    side_effect=["usr/bin/docker"],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.register_sidecar_idle_checkers",
    side_effect=[
        [
            DockerSidecarActivityCheckerMetadata(
                container_id="container1",
                port="8080",
                endpoint="mock/idle/endpoint",
                response_template="mockresponsetemplate",
            ),
            DockerSidecarActivityCheckerMetadata(
                container_id="container2",
                port="8081",
                endpoint="mock/idle/endpoint2",
                response_template="mockresponsetemplate",
            ),
            DockerSidecarActivityCheckerMetadata(
                container_id="container3",
                port="8083",
                endpoint="mock/idle/endpoint3",
                response_template="mockresponsetemplate",
            ),
        ]
    ],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.serverapp.list_running_servers",
    side_effect=[iter([{"url": "http://default:8888/jupyterlab/default"}])],
)
@patch(
    "jupyter_activity_monitor_extension.docker_sidecar_check.requests.get",
    side_effect=[
        MockResponse(status_code=200, content=json.dumps({"mockresponsetemplate": 1})),
        MockResponse(status_code=404),
        MockResponse(status_code=200, content=json.dumps({"mockresponsetemplate": 0})),
    ],
)
def test_docker_sidecar_check_when_multiple_containers_are_running(
    mock_response,
    mock_running_servers,
    mock_register_sidecar_idle_checkers,
    mock_docker_path,
):
    actual = check_if_sidecars_idle()
    assert actual is False
