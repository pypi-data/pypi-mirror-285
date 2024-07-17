import json
import logging
import sys
from logging import Logger

import requests
import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler

from .common.requests_utils import getCreateAdminAPIKey
from .common.variables import GET_OWN_ENDPOINTS
from .custom_types import (
    Endpoint,
    EndpointListResponse,
    OwnerRequest,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GetOwnEndpoints(APIHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            request = OwnerRequest(**json.loads(json.dumps(self.get_json_body())))
            endpoint_list_response = EndpointListResponse()
            logger.error(f"Owner received => {request.owner}")
            headers = {
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(request.owner),
            }
            get_owned_endpoints = requests.get(
                GET_OWN_ENDPOINTS.format(request.owner), headers=headers
            )
            logger.error(f"Owned Endpoints => {get_owned_endpoints.json()}")
            endpoints = [
                Endpoint(**json.loads(json.dumps(end)))
                for end in get_owned_endpoints.json()
            ]
            endpoint_list_response.data = endpoints
        except Exception as exc:
            logger.error(
                f"Generic exception from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            endpoint_list_response.status_code = 200
            self.finish(json.dumps(endpoint_list_response.to_json()))
