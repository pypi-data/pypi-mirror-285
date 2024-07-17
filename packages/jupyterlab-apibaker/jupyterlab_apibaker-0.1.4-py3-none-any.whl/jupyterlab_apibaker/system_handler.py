import json
import logging
import os
import sys
from logging import Logger

import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class SystemHandler(APIHandler):
    @tornado.web.authenticated
    def get(self):
        try:
            data = os.environ.get("API_BAKER_DOMAIN", None)
        except Exception as exc:
            logger.error(
                f"There has been an error getting API_BAKER_DOMAIN system environment variable {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            self.finish(json.dumps({
                "data": data,
            }))