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
    GET_WORKFLOWS_STATUS_URL,
)
from .custom_types import (
    Error,
    RequestResponseGeneric,
    UpdateAPIKeyRequest,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Refresh API Key handler
class WorkflowsHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        logger.error("Getting all workflows from endpoint")
        try:
            response = RequestResponseGeneric()

            current_user = get_request_attr_value(self, "owner")
            endpointId = get_request_attr_value(self, "endpointId")
            versionId = get_request_attr_value(self, "versionId")

            logger.error(f"current_user => {type(current_user)} {current_user}")
            logger.error(f"endpointId => {type(endpointId)} {endpointId}")
            logger.error(f"versionId => {type(versionId)}  {versionId}")

            if not endpointId or not current_user:
                raise Exception("The request to the extension backend is not valid")

            headers = {
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(current_user),
            }            
            get_endpoint_workflows = requests.get(
                GET_WORKFLOWS_STATUS_URL.format(endpointId, versionId),
                headers=headers,
            )
            logger.error(f"Endpoints Workflows => {get_endpoint_workflows.json()}")
        except Exception as exc:
            logger.error(
                f"Generic exception from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            self.status_code = 200
            self.finish(json.dumps(get_endpoint_workflows.json()))
