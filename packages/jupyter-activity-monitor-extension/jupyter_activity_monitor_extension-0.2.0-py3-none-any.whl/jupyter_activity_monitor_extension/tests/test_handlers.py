import json
import pytest
from datetime import datetime
from unittest.mock import patch


@pytest.fixture
def jp_server_config(jp_template_dir):
    return {
        "ServerApp": {
            "jpserver_extensions": {"jupyter_activity_monitor_extension": True}
        },
    }


@patch(
    "jupyter_activity_monitor_extension.handler.check_if_sidecars_idle",
    side_effect=[True],
)
async def test_get_without_sessions_and_terminal(mock_check_if_sidecars_idle, jp_fetch):
    response = await jp_fetch("api", "idle", method="GET")

    assert response.code == 200


@patch(
    "jupyter_activity_monitor_extension.handler.check_if_sidecars_idle",
    side_effect=[True],
)
@patch(
    "jupyter_activity_monitor_extension.handler.IdleHandler.get_last_active_timestamp",
    side_effect=["0"],
)
async def test_get_with_inactive_sidecars(
    mock_get_last_active_timestamp,
    mock_check_if_sidecars_idle,
    jp_fetch,
):
    response = await jp_fetch("api", "idle", method="GET")

    assert response.code == 200
    assert json.loads(response.body) == {
        "lastActiveTimestamp": "0",
    }


@patch(
    "jupyter_activity_monitor_extension.handler.check_if_sidecars_idle",
    side_effect=[False],
)
@patch(
    "jupyter_activity_monitor_extension.handler.IdleHandler.get_last_active_timestamp",
    side_effect=["0"],
)
async def test_get_with_active_sidecars(
    mock_get_last_active_timestamp,
    mock_check_if_sidecars_idle,
    jp_fetch,
):
    response = await jp_fetch("api", "idle", method="GET")

    assert response.code == 200
    assert datetime.strptime(
        json.loads(response.body)["lastActiveTimestamp"],
        "%Y-%m-%dT%H:%M:%S.%fz",
    ) > datetime(2024, 6, 29)


# TODO: Write tests for get with sessions and terminals mocked.
