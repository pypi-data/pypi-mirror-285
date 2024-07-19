import ast
import logging
import re
from ast import FunctionDef
from logging import Logger
from typing import List

import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler

from .custom_types import (
    Error,
    NBFunctions,
    RequestResponseForModel,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ParseNBModel(APIHandler):
    @tornado.web.authenticated
    def post(self):
        response: RequestResponseForModel = RequestResponseForModel()
        try:
            nb_model = self.get_json_body()

            if not nb_model:
                response.error = Error(600, "NB Model has not been received.")
                self.finish(response.to_json())
            else:
                response.data.nbpython_version = nb_model["metadata"]["language_info"][
                    "version"
                ]

                for cell in nb_model["cells"]:
                    if cell["cell_type"] == "code":
                        functions_list = self.get_functions_list(cell["source"])
                        if functions_list:
                            for function in functions_list:
                                response.data.nbfunctions.append(
                                    NBFunctions(function.name, cell["source"])
                                )
                response.status_code = 200
                response.error = None
        except Exception as exc:
            logger.info(
                f"There as been an error trying to parse the NB Model to get the list of functions: {exc}"
            )
            response.error = Error(
                600,
                f"There as been an error trying to parse the NB Model to get the list of functions: {exc}",
            )
        else:
            self.finish(response.to_json())

    def get_functions_list(self, source_code: str) -> List[FunctionDef] | None:
        is_function = (
            True
            if sum(
                1
                for _ in re.finditer(
                    r"def (\w+)\s*\((.*?)\)(.*?):", source_code, re.MULTILINE
                )
            )
            > 0
            else False
        )

        if not is_function:
            return None

        source = ast.parse(source_code, type_comments=True)
        return [node for node in ast.walk(source) if type(node) == ast.FunctionDef]
