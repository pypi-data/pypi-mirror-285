import json
import logging
import sys
from logging import Logger

import requests
import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler
from requests import HTTPError

from .common.requests_utils import getCreateAdminAPIKey
from .common.variables import (
    ENDPOINT,
    GET_EXECUTION_STATUS_URL,
    GET_IMAGE_STATUS_URL,
    LOGS_URL,
    README_URL,
)
from .custom_types import (
    Endpoint,
    EndpointResponse,
    EndpointUpdatesInterface,
    EndpointVersion,
    EndpointVersionResponse,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class GetProcessUpdates(APIHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            request_info = EndpointUpdatesInterface(
                **json.loads(json.dumps(self.get_json_body()))
            )
            logger.error(f"Owner Image Status Update => {request_info.owner}")
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(request_info.owner),
            }
            logger.error(f"ID Received => {request_info.id}")
            logger.error(f"Action Received => {request_info.action}")
            resp = None

            if request_info.action == "image":
                logger.error(
                    f"Get Image Status URL => {GET_IMAGE_STATUS_URL.format(request_info.id, request_info.version)}"
                )

                image_creation_status = requests.get(
                    GET_IMAGE_STATUS_URL.format(request_info.id, request_info.version),
                    headers=headers,
                )
                logger.error(f"Image Creation Status => {image_creation_status.json()}")
                if image_creation_status.status_code != 200:
                    image_creation_status.raise_for_status()

                respImageStatus = EndpointVersion(
                    **json.loads(json.dumps(image_creation_status.json()))
                )
                temp_resp = EndpointVersionResponse()
                temp_resp.status_code = image_creation_status.status_code
                temp_resp.data = respImageStatus
                resp = temp_resp.to_json()

            if request_info.action == "readme":
                logger.error(
                    f"Get README URL => {README_URL.format(ENDPOINT, request_info.id)}"
                )
                resp = requests.get(
                    README_URL.format(ENDPOINT, request_info.id), headers=headers
                )
                logger.error(f"Readme => {resp.json()}")

            if request_info.action == "execution":
                logger.error(
                    f"Get Execution Status => {GET_EXECUTION_STATUS_URL.format(request_info.id, request_info.version)}"
                )
                resp = requests.get(
                    GET_EXECUTION_STATUS_URL.format(
                        request_info.id, request_info.version
                    )
                )
                logger.error(f"Execution Status => {resp.json()}")

            if request_info.action == "logs":
                logger.error(
                    f"Get Execution Status => {LOGS_URL.format(request_info.id)}"
                )
                resp = requests.get(LOGS_URL.format(request_info.id), headers=headers)
                logger.error(f"Logs => {resp.json()}")
        except HTTPError as exc:
            logger.error(
                f"There has been an error: {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        except Exception as exc:
            logger.error(
                f"There has been an error: {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            self.finish(resp)
