import logging
import sys
from http import HTTPStatus
from logging import Logger

import requests
import tornado
import tornado.escape as escape

from ..custom_types import Error, RequestResponseGeneric
from .variables import CREATE_ADMIN_API_KEY

logger: Logger = logging.getLogger(__name__)  # noqa: F821
logger.setLevel(logging.DEBUG)


def get_request_attr_value(handler, arg):
    try:
        param = handler.get_argument(arg)
        if not param:
            logger.error(f"Invalid argument '{arg}', cannot be blank.")
            raise tornado.web.HTTPError(
                status_code=HTTPStatus.BAD_REQUEST,
                reason=f"Invalid argument '{arg}', cannot be blank.",
            )
        return param
    except tornado.web.MissingArgumentError as e:
        logger.error(f"Missing argument '{arg}'.", exc_info=e)
        raise tornado.web.HTTPError(
            status_code=HTTPStatus.BAD_REQUEST, reason=f"Missing argument '{arg}'."
        ) from e


def get_body_value(handler):
    try:
        if not handler.request.body:
            raise ValueError()
        return escape.json_decode(handler.request.body)
    except ValueError as e:
        logger.error("Invalid body.", exc_info=e)
        raise tornado.web.HTTPError(
            status_code=HTTPStatus.BAD_REQUEST, reason=f"Invalid POST body: {e}"
        ) from e


def getCreateAdminAPIKey(current_user: str) -> str | None:
    logger.error("Getting Admin API Key")
    try:
        response = RequestResponseGeneric()
        logger.error(f"Get User => {current_user}")
        create_api_key_response = requests.post(
            CREATE_ADMIN_API_KEY,
            json={
                "apiKeyName": current_user,
                "description": current_user,
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
        logger.error(f'API Key => {response.to_dict()["data"]["apiKey"]}')
        api_key = response.to_dict()["data"]["apiKey"]
        return api_key
