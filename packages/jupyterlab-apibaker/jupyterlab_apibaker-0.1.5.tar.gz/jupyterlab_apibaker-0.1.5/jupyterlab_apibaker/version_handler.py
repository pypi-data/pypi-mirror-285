import json
import logging
import sys
from logging import Logger

import requests
import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler

from .common.requests_utils import (
    getCreateAdminAPIKey,
)
from .common.variables import (
    GET_ENDPOINT_VERSION,
)
from .custom_types import (
    DeleteVersionRequest,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Create API Key
class VersionHandler(APIHandler):
    @tornado.web.authenticated
    def delete(self):
        try:
            request = self.get_json_body()
            if not request:
                raise Exception("Token Information is missing to create a token.")

            version_info = DeleteVersionRequest(**json.loads(json.dumps(request)))
            logger.error(f"Version Info Received => {version_info}")
            headers = {
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(version_info.current_user),
            }
            delete_version_response = requests.delete(
                GET_ENDPOINT_VERSION.format(version_info.endpoint_id, version_info.version_id), headers=headers
            )
            logger.info(f"Delete Version Resp => {delete_version_response}")
        except requests.exceptions.RequestException as err:
            logger.info(
                f"There has been an error making the request {sys._getframe(  ).f_code.co_name} with error: {err}"
            )
            self.set_status(400)
        else:
            self.set_status(200)
            self.finish()