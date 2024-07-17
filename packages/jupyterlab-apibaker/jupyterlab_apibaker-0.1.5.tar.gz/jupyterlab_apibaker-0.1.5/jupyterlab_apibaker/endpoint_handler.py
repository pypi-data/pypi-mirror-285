import ast
import json
import logging
import os
import re
import shutil
import sys
from ast import Module
from itertools import groupby
from logging import Logger
from pathlib import Path
from typing import Dict, List
from xmlrpc.client import boolean

import requests
import tornado
import tornado.web
from jupyter_server.base.handlers import APIHandler
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style

from .api_code_variables import app_code
from .common.requests_utils import (
    get_request_attr_value,
    getCreateAdminAPIKey,
)
from .common.variables import (
    DELETE_ENDPOINT,
    ENDPOINT,
    GET_OWN_ENDPOINTS,
)
from .custom_types import (
    Endpoint,
    EndpointListResponse,
    EndpointResponse,
    Error,
    FunctionParameters,
    NotebookInfo,
    RequestResponseGeneric,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class EndpointHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        create_endpoint_response = EndpointResponse()
        try:
            nb_info_json = self.get_json_body()
            response = RequestResponseGeneric()

            if nb_info_json is None:
                response.error = Error(600, "No notebook information was received")
                self.finish(response.to_json())

            nb_info = NotebookInfo(**json.loads(json.dumps(nb_info_json)))

            # TODO: Change this to make it configurable
            user_files_dst_path = Path(
                f"{os.environ['API_BAKER_EFS_PATH']}/{nb_info.owner}/{nb_info.notebookName}/{nb_info.functionName}"
            )

            nb_path_expanded = Path(os.path.expanduser(os.path.dirname(nb_info.nbPath)))

            logger.error(f"Notebook Info => {nb_info}")
            logger.error(f"User Files Destination => {user_files_dst_path}")

            requirements_list = self.prepare_requirements(
                nb_info.functionCode, nb_path_expanded
            )

            function_parameters = self.get_params_from_function_signature(
                nb_info.functionCode, nb_info.functionName
            )

            if nb_info_json:
                del nb_info_json["functionCode"]
                del nb_info_json["nbPath"]
                nb_info_json["parameters"] = [
                    json.loads(fp.to_json()) for fp in function_parameters
                ]

            self.create_readme(nb_info, function_parameters, nb_path_expanded)

            files_copied = self.copy_user_files_to_common_storage(
                nb_path_expanded,
                user_files_dst_path,
                requirements_list if requirements_list else [],
            )
            build_app_py = self.create_app(function_parameters, user_files_dst_path)
            build_main_py = self.create_main(nb_info.functionCode, user_files_dst_path)

            if not files_copied:
                response = RequestResponseGeneric(
                    None,
                    Error(
                        600,
                        f"Error copying files from {nb_info.nbPath} to {user_files_dst_path}",
                    ),
                )
                self.finish(response.to_json())

            if not build_app_py:
                response = RequestResponseGeneric(
                    None,
                    Error(
                        600,
                        "Error building app.py",
                    ),
                )
                self.finish(response.to_json())

            if not build_main_py:
                response = RequestResponseGeneric(
                    None,
                    Error(
                        600,
                        "Error building main.py",
                    ),
                )
                self.finish(response.to_json())

            logger.error(
                f"File List in Destination => {os.listdir(user_files_dst_path)}"
            )

            logger.error(f"NB Info JSON to NSQ => {nb_info_json}")
            # TODO: Clean the JSON being sent to the Brain as it has way more than necessary.
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(nb_info.owner),
            }
            create_endpoint_raw = requests.post(
                ENDPOINT, headers=headers, json=nb_info_json
            )

            logger.error(f"Data => {create_endpoint_raw.json()}")
            create_endpoint = Endpoint(
                **json.loads(json.dumps(create_endpoint_raw.json()))
            )
            create_endpoint_response.data = create_endpoint
            # create_endpoint = JLCreateEndpointResponse(
            #     **json.loads(json.dumps(create_endpoint_raw.json()))
            # )
            logger.error(f"Create Endpoint => {create_endpoint_response}")

        except requests.exceptions.RequestException as err:
            logger.info(f"There has been an error making the request. {err}")
            create_endpoint_response.error = Error(
                600,
                f"There has been an error making the request {sys._getframe(  ).f_code.co_name} with error: {err}",
            )
        except TypeError as err:
            logger.error(
                f"There has been an error trying to serialize the NB Info: {err}"
            )
            create_endpoint_response.error = Error(
                600,
                f"There has been an error TypeError {sys._getframe(  ).f_code.co_name} with error: {err}",
            )
        except json.JSONDecodeError as err:
            logger.error(
                f"There has been an error parsing the serialized NB Info into NotebookInfo: {err}"
            )
            create_endpoint_response.error = Error(
                600,
                f"There has been an error parsing the serialized NB Info into NotebookInfo {sys._getframe(  ).f_code.co_name} with error: {err}",
            )
        else:
            create_endpoint_response.status_code = 200
            # self.finish(json.dumps(create_endpoint_response.to_json()))
            self.finish(create_endpoint_response.to_dict())

    def delete(self):
        try:
            endpoint_id = self.get_json_body()["endpoint_id"]  # type: ignore
            owner = self.get_json_body()["owner"]  # type: ignore
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(owner),
            }
            delete_endpoint = requests.delete(
                DELETE_ENDPOINT.format(endpoint_id), headers=headers
            )
            logger.info(f"Delete Endpoint Resp => {delete_endpoint}")
        except requests.exceptions.RequestException as err:
            logger.info(
                f"There has been an error making the request {sys._getframe(  ).f_code.co_name} with error: {err}"
            )
            self.set_status(400)
        else:
            self.set_status(200)
            self.finish()

    def requirements_exists(self, nb_path: Path) -> bool:
        return (nb_path / "requirements.txt").is_file()

    def prepare_requirements(self, function_code: str, nb_path: Path) -> List | None:
        try:
            user_provided_requirements_path = nb_path / "requirements.txt"
            user_provided_requirements: list[str] = []

            if user_provided_requirements_path.is_file():
                with open(nb_path / "requirements.txt", "r") as f:
                    user_provided_requirements = f.readlines()

            files_list: list[str] = os.listdir(nb_path)
            source: Module = ast.parse(function_code)

            imports = [
                im.name if "." not in im.name else im.name.split(".")[0]
                for node in ast.walk(source)
                if type(node) == ast.Import
                for im in node.names
            ]

            imports_from: list[str] = [
                node.module if "." not in node.module else node.module.split(".")[0]
                for node in ast.walk(source)
                if node and type(node) == ast.ImportFrom and node.module
            ]

            imports_list = list(set(imports + imports_from))

            code_imports_list = set(
                [
                    imp
                    for imp in imports_list
                    for file in files_list
                    if imp + ".py" in str(file) or imp in str(file)
                ]
            ) ^ set(imports_list)

            final_imports_list = self.unify_requirements(
                user_provided_requirements, code_imports_list
            )

        except Exception as exc:
            logger.error(
                f"There has been an issue processing the imports for {function_code} in {nb_path}=> {exc}"
            )
            return None
        else:
            return final_imports_list

    def unify_requirements(
        self, user_provided_reqs: List[str], code_imports_list: set
    ) -> List[str]:
        usr_prov_reqs_set = set([r.split("==")[0].strip() for r in user_provided_reqs])
        imports_intersection = code_imports_list.intersection(usr_prov_reqs_set)
        tmp_imports_list = [
            v.strip()
            for v in user_provided_reqs
            if v.split("==")[0].strip() in imports_intersection
        ]
        tmp_imports_list_union = set(tmp_imports_list).union(code_imports_list)

        unified_imports_list = []
        for _, grp in groupby(
            sorted(
                list(tmp_imports_list_union),
                key=lambda req: req.split("==")[0].strip(),
            ),
            key=lambda req: req.split("==")[0].strip(),
        ):
            unified_imports_list.append(sorted(grp, key=lambda x: -len(x))[0])
        return unified_imports_list

    def write_requirements(self, reqs_list: List[str], dst_path: Path) -> None:
        try:
            with open(dst_path / "requirements.txt", "w") as requirements_file:
                requirements_file.write("\n".join(reqs_list))
        except IOError as err:
            logger.error(
                f"There has been an error while writing the requirements.txt file: {err}"
            )
            logger.error(f"Error => {sys._getframe(  ).f_code.co_name}")

    def copy_user_files_to_common_storage(
        self, src: Path, dst: Path, requirements_list: List
    ) -> bool:
        logger.error(f"Copying files from {src} to {dst}")
        try:
            dst.mkdir(parents=True, exist_ok=True)

            self.write_requirements(requirements_list, dst)

            logger.error(f"Files List in Function => {os.listdir(src)}")
            shutil.copytree(
                src,
                dst,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".*", "*.ipynb", "__pycache__"),
            )
        except shutil.Error as exc:
            errors = exc.args[0]
            for error in errors:
                esrc, edst, emsg = error
                logger.error(
                    f"Failed Copying user files: from {esrc} to {edst} with {emsg}"
                )
            return False
        except (OSError, IOError) as e:
            logger.error(f"Error: {sys._getframe(  ).f_code.co_name} - {str(e)}")
            return False
        else:
            return True

    def multiple_replace(self, dict: Dict, text: str) -> str:
        regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
        return regex.sub(
            lambda mo: dict[mo.string[mo.start() : mo.end()]], text, re.MULTILINE
        )

    def get_params_from_function_signature(
        self, function_code: str, function_name: str
    ) -> List[FunctionParameters]:
        parameters = list()
        source = ast.parse(function_code, type_comments=True)
        functions = [node for node in ast.walk(source) if type(node) == ast.FunctionDef]
        for func in functions:
            if func.name == function_name:
                for param in func.args.args:
                    single_param = FunctionParameters()
                    single_param.name = param.arg
                    parameters.append(single_param)
        logger.error(f"Parameters => {parameters}")
        return parameters

    def create_readme(
        self,
        nb_info: NotebookInfo,
        function_parameters: List[FunctionParameters],
        nb_path_expanded: Path,
    ) -> None:
        writer = MarkdownTableWriter(
            column_styles=[
                Style(fg_color="black", font_weight="bold"),
                Style(fg_color="green"),
            ],
            table_name="Endpoint's information",
            headers=["", ""],
            value_matrix=[
                ["Owner", f"{nb_info.owner}"],
                ["Notebook Name", f"{nb_info.notebookName}"],
                ["Function Name", f"{nb_info.functionName}"],
                [
                    "Function Parameters",
                    f"{', '.join(fp.name for fp in function_parameters)}",
                ],
            ],
            margin=1,
            enable_ansi_escape=False,
        )
        writer.dump(str(nb_path_expanded / "README.md"))

    def create_app(
        self, user_function_param_list: List[FunctionParameters], dst: Path
    ) -> boolean:
        try:
            add_args = "\n".join(
                [
                    f'{" " * 3} parser.add_argument("{p.name}")'
                    for p in user_function_param_list
                ]
            ).lstrip()
            var_setup = "\n".join(
                [
                    f"{' ' * 3} {p.name} = args.{p.name}"
                    for p in user_function_param_list
                ]
            ).lstrip()
            logger_code = f'logger.info(f"{", ".join([f"{fp.name.upper()} => {{{fp.name}}}" for fp in user_function_param_list]).strip()}")'
            main_call = f"main({', '.join([fp.name for fp in user_function_param_list]).strip()})"
            sub = {
                "<parser_argument>": add_args,
                "<variables_setup>": var_setup,
                "<logger>": logger_code,
                "<main_call>": main_call,
            }
            app_py = self.multiple_replace(sub, app_code)
            with open(dst / "app.py", "w") as app_source:
                app_source.write(app_py)
        except IOError as err:
            logger.error(f"Thee has been an error trying to create app.py: {err}")
            return False
        else:
            return True

    def create_main(self, user_function_code: str, dst: Path) -> boolean:
        try:
            with open(dst / "main.py", "w") as main:
                main.write(user_function_code)
        except IOError as err:
            logger.info(f"There has been an error creating main.py: {err}")
            return False
        else:
            return True

    @tornado.web.authenticated
    def get(self):
        logger.error("Getting all endpoints from owner")
        try:
            endpoint_list_response = EndpointListResponse()
            current_user = get_request_attr_value(self, "owner")
            logger.error(f"Current User => {current_user}")
            if not current_user:
                raise Exception("The request to the extension backend is not valid")
            headers = {
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(current_user),
            }
            get_owned_endpoints = requests.get(
                GET_OWN_ENDPOINTS.format(current_user),
                headers=headers,
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
