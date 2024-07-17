import json
import logging
from logging import Logger

import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import url_path_join

from jupyterlab_apibaker.apikey_handler import APIKeyHandler
from jupyterlab_apibaker.refresh_apikey_handler import RefreshAPIKeyHandler
from jupyterlab_apibaker.notebook_handler import ParseNBModel
from jupyterlab_apibaker.updates_handler import GetProcessUpdates
from jupyterlab_apibaker.workflows_handler import WorkflowsHandler
from jupyterlab_apibaker.workflow_log_handler import WorkflowLogHandler
from jupyterlab_apibaker.version_handler import VersionHandler
from jupyterlab_apibaker.system_handler import SystemHandler

from .api_collection_handler import GetOwnEndpoints
from .endpoint_handler import EndpointHandler

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        self.finish(
            json.dumps({"data": "This is /jupyterlab-apibaker/get-example endpoint!"})
        )


def setup_handlers(web_app: ServerApp) -> None:
    host_pattern = ".*$"
    app_name = "jupyterlab-apibaker"

    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, app_name, "get-example")
    parse_nb_model = url_path_join(base_url, app_name, "parse-model")
    workfow_log_handler = url_path_join(base_url, app_name, "endpoint/workflows/log")
    workfows_handler = url_path_join(base_url, app_name, "endpoint/workflows")
    endpoint = url_path_join(base_url, app_name, "endpoint")
    get_endpoint_updates = url_path_join(base_url, app_name, "get-endpoint-updates")
    get_own_endpoints = url_path_join(base_url, app_name, "get-own-endpoints")
    refresh_api_key_handler = url_path_join(base_url, app_name, "api-keys/refresh")
    api_key_handler = url_path_join(base_url, app_name, "api-keys")
    version_handler = url_path_join(base_url, app_name, "version")
    system_handler = url_path_join(base_url, app_name, "env")
    handlers = [
        (route_pattern, RouteHandler),
        (parse_nb_model, ParseNBModel),
        (get_endpoint_updates, GetProcessUpdates),
        (workfow_log_handler, WorkflowLogHandler),
        (workfows_handler, WorkflowsHandler),
        (endpoint, EndpointHandler),
        (get_own_endpoints, GetOwnEndpoints),
        (api_key_handler, APIKeyHandler),
        (refresh_api_key_handler, RefreshAPIKeyHandler),
        (version_handler, VersionHandler),
        (system_handler, SystemHandler),
    ]
    web_app.add_handlers(host_pattern, handlers)
