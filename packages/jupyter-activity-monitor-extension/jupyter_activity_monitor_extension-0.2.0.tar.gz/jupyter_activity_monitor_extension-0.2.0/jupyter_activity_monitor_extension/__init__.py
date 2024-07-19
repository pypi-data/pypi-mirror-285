# __init__.py

from .handler import IdleHandler
from jupyter_server.utils import url_path_join


def build_url(web_app, endpoint):
    base_url = web_app.settings["base_url"]
    return url_path_join(base_url, endpoint)


def register_handlers(server_app):
    web_app = server_app.web_app
    host_pattern = ".*$"
    handlers = [
        (
            build_url(web_app, r"/api/idle"),
            IdleHandler,
        ),
    ]
    web_app.add_handlers(host_pattern, handlers)


def _jupyter_server_extension_paths():
    return [{"module": "jupyter_activity_monitor_extension"}]


def load_jupyter_server_extension(server_app):
    register_handlers(server_app)
