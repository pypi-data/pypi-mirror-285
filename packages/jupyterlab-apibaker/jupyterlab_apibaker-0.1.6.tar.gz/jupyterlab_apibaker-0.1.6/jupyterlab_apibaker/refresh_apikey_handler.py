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
    REFRESH_API_KEY,
)
from .custom_types import (
    Error,
    RequestResponseGeneric,
    UpdateAPIKeyRequest,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Refresh API Key handler
class RefreshAPIKeyHandler(APIHandler):
    # Refresh API Key
    @tornado.web.authenticated
    def put(self):
        try:
            response = RequestResponseGeneric()
            request = self.get_json_body()
            if not request:
                raise Exception("Token Information is missing to create a token.")

            api_key_info = UpdateAPIKeyRequest(**json.loads(json.dumps(request)))
            logger.error(f"Token Info Received => {api_key_info}")
            headers = {
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(api_key_info.current_user),
            }
            update_api_key_response = requests.put(
                REFRESH_API_KEY.format(api_key_info.endpoint_id, api_key_info.api_key_id),
                headers=headers,
                json={
                    "expiresInDays": 30,
                },
            )
            logger.error(f"Refresh API Key Request => {update_api_key_response.text}")
            response.data = update_api_key_response.json()
            if update_api_key_response.status_code >= 400:
                response.error = Error(
                    update_api_key_response.status_code,
                    update_api_key_response.json()["message"],
                )
                update_api_key_response.raise_for_status()

            response.status_code = update_api_key_response.status_code
        except requests.HTTPError as exc:
            logger.error(
                f"HTTP Error from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        except Exception as exc:
            logger.error(exc)
        else:
            logger.error(f"Response => {response.to_dict()}")
            self.finish(json.dumps(response.to_json()))