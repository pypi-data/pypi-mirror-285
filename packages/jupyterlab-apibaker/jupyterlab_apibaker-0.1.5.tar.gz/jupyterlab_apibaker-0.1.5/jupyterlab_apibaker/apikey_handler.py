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
    CREATE_USER_API_KEY,
    GET_ALL_API_KEYS,
    MODIFY_API_KEY,
)
from .custom_types import (
    APIKey,
    APIKeyType,
    CreateAPIKeyRequest,
    Endpoint,
    EndpointResponse,
    Error,
    RequestResponseGeneric,
    UpdateAPIKeyRequest,
)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Create API Key
class APIKeyHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            response = RequestResponseGeneric()
            request = self.get_json_body()
            if not request:
                raise Exception("Token Information is missing to create a token.")

            api_key_info = CreateAPIKeyRequest(**json.loads(json.dumps(request)))
            logger.error(f"Token Info Received => {api_key_info}")
            headers = {
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(api_key_info.current_user),
            }
            create_api_key_response = requests.post(
                CREATE_USER_API_KEY.format(api_key_info.endpoint_id),
                headers=headers,
                json={
                    "apiKeyName": api_key_info.name,
                    "description": api_key_info.description,
                    "type": APIKeyType.USER,
                },
            )
            logger.error(f"Create API Key Request => {create_api_key_response.text}")
            response.data = create_api_key_response.json()
            if create_api_key_response.status_code >= 400:
                response.error = Error(
                    create_api_key_response.status_code,
                    create_api_key_response.json()["message"],
                )
                create_api_key_response.raise_for_status()

            response.status_code = create_api_key_response.status_code
        except requests.HTTPError as exc:
            logger.error(
                f"HTTP Error from {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        except Exception as exc:
            logger.error(exc)
        else:
            logger.error(f"Response => {response.to_dict()}")
            self.finish(json.dumps(response.to_json()))

    @tornado.web.authenticated
    def get(self):
        try:
            response = EndpointResponse()
            endpoint_id = get_request_attr_value(self, "id")
            logger.error(f"Attributes => {endpoint_id}")
            owner = get_request_attr_value(self, "owner")
            logger.error(f"Endpoint ID => {endpoint_id}")
            logger.error(f"Owner => {owner}")
            if not endpoint_id:
                raise Exception("The request to the extension backend is not valid")
            headers = {
                "Accept": "application/json",
                "x-api-key": getCreateAdminAPIKey(owner),
            }
            all_api_keys_response = requests.get(
                GET_ALL_API_KEYS.format(endpoint_id), headers=headers
            )

            # all_api_keys = APIKey(
            #     **json.loads(json.dumps(all_api_keys_response.json()))
            # )
            all_api_keys = all_api_keys_response.json()
            logger.error(f"API Keys => {all_api_keys}")
            response.data = all_api_keys
        except Exception as exc:
            logger.error(
                f"There has been an error getting all the API Keys {sys._getframe(  ).f_code.co_name} with error: {exc}"
            )
        else:
            response.status_code = 200
            self.finish(json.dumps(response.to_json()))

    @tornado.web.authenticated
    def delete(self):
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
            delete_endpoint = requests.delete(
                MODIFY_API_KEY.format(api_key_info.endpoint_id, api_key_info.api_key_id), headers=headers
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

    # Update API Key
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
                MODIFY_API_KEY.format(api_key_info.endpoint_id, api_key_info.api_key_id),
                headers=headers,
                json={
                    "apiKeyName": api_key_info.name,
                    "description": api_key_info.description,
                    "type": APIKeyType.USER,
                },
            )
            logger.error(f"Create API Key Request => {update_api_key_response.text}")
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