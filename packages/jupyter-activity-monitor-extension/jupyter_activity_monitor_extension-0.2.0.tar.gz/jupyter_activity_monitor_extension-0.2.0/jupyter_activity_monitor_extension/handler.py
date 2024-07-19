from jupyter_server.base.handlers import JupyterHandler, json_errors
import json
from datetime import datetime, timezone
from tornado import gen, web
from jupyter_activity_monitor_extension.docker_sidecar_check import (
    check_if_sidecars_idle,
)


class IdleHandler(JupyterHandler):
    @web.authenticated
    @json_errors
    @gen.coroutine
    def get(self):
        sm = self.settings["session_manager"]
        tm = self.terminal_manager
        sessions = yield sm.list_sessions()
        terminals = tm.list()
        largest_last_activity = self.get_last_active_timestamp(sessions, terminals)
        # check if any running sidecars are broadcasting as not idle
        all_sidecars_idle = check_if_sidecars_idle()
        current_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fz")
        if (largest_last_activity is not None) and all_sidecars_idle:
            response = {"lastActiveTimestamp": largest_last_activity}
        elif not all_sidecars_idle:
            response = {"lastActiveTimestamp": current_time}
        else:
            response = {}
        self.finish(json.dumps(response))

    def get_last_active_timestamp(self, sessions, terminals):
        session_last_activity_time = [
            datetime.strptime(
                session["kernel"]["last_activity"], "%Y-%m-%dT%H:%M:%S.%fz"
            )
            for session in sessions
        ]
        terminals_last_activity_time = [
            datetime.strptime(terminal["last_activity"], "%Y-%m-%dT%H:%M:%S.%fz")
            for terminal in terminals
        ]
        if session_last_activity_time and terminals_last_activity_time:
            max_last_activity_time = max(
                session_last_activity_time + terminals_last_activity_time
            )
        elif session_last_activity_time and not terminals_last_activity_time:
            max_last_activity_time = max(session_last_activity_time)
        elif terminals_last_activity_time and not session_last_activity_time:
            max_last_activity_time = max(terminals_last_activity_time)
        else:
            max_last_activity_time = None

        # Print the greatest last_activity time
        if max_last_activity_time is not None:
            return max_last_activity_time.strftime("%Y-%m-%dT%H:%M:%S.%fz")
        else:
            return self.settings["started"].strftime("%Y-%m-%dT%H:%M:%S.%fz")
