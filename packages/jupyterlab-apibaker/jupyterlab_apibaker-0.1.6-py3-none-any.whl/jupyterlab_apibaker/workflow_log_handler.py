import json
import logging
import sys
from logging import Logger

import requests
import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler

from .common.requests_utils import (
    get_request_attr_value,
    getCreateAdminAPIKey,
)
from .common.variables import (
    GET_EXECUTION_LOG_URL,
)
from .custom_types import (
    Error,
    RequestResponseGeneric,
    UpdateAPIKeyRequest,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Refresh API Key handler
class WorkflowLogHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        logger.error("Getting all workflows from endpoint")
        try:
            response = RequestResponseGeneric()

            current_user = get_request_attr_value(self, "owner")
            endpoint_id = get_request_attr_value(self, "endpointId")
            version_id = get_request_attr_value(self, "versionId")
            workflow_name = get_request_attr_value(self, "workflowName")

            logger.error(f"current_user => {type(current_user)} {current_user}")
            logger.error(f"endpoint_id => {type(endpoint_id)} {endpoint_id}")
            logger.error(f"version_id => {type(version_id)}  {version_id}")
            logger.error(f"workflow_name => {type(workflow_name)}  {workflow_name}")

            if not endpoint_id or not current_user or not workflow_name:
                raise Exception("The request to the extension backend is not valid")

            headers = {
                "Accept": "text/html",
                "x-api-key": getCreateAdminAPIKey(current_user),
            }            
            get_endpoint_workflows = requests.get(
                GET_EXECUTION_LOG_URL.format(endpoint_id, version_id, workflow_name),
                headers=headers,
            )
            logger.error(f"Endpoints Workflow log => {get_endpoint_workflows.text}")
        except Exception as exc:
            logger.error(
                f"Generic exception from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            self.status_code = 200
            self.finish(get_endpoint_workflows.text)
