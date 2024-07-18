"""Base client for interact with backend server"""
import os
import uuid
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from nlpbridge.audio import get_default_header

from ._exception import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    PreconditionFailedException,
    InternalServerErrorException,
    InvalidRequestArgumentError,
    GZUServerException,
    BaseRPCException
)
from .utils.logger_util import logger


class HTTPClient:
    r"""HTTPClient类,实现与后端服务交互的公共方法"""

    def __init__(self, secret_key: Optional[str] = None, gateway: str = ""):
        self.secret_key = secret_key if secret_key else os.getenv(
            "GZU_TOKEN", "")
        if not self.secret_key:
            raise ValueError(
                "secret_key is empty, please pass a nonempty secret_key "
                'or set a secret_key in environment variable "GZU_TOKEN"'
            )
        if not self.secret_key.startswith("Bearer"):
            self.secret_key = "Bearer {}".format(self.secret_key)
        self.gateway = gateway
        self.session = requests.sessions.Session()
        self.retry = Retry(total=0, backoff_factor=0.1)
        self.session.mount(self.gateway, HTTPAdapter(max_retries=self.retry))

    @staticmethod
    def check_response_header(response: requests.Response):
        status_code = response.status_code
        if status_code == requests.codes.ok:
            return
        message = "request_id={} , http status code is {}, body is {}".format(
            __class__.response_request_id(response), status_code, response.text)
        if status_code == requests.codes.bad_request:
            raise BadRequestException(message)
        elif status_code == requests.codes.forbidden:
            raise ForbiddenException(message)
        elif status_code == requests.codes.not_found:
            raise NotFoundException(message)
        elif status_code == requests.codes.precondition_required:
            raise PreconditionFailedException(message)
        elif status_code == requests.codes.internal_server_error:
            raise InternalServerErrorException(message)
        else:
            raise BaseRPCException(message)

    @staticmethod
    def check_response_json(data: dict):
        if "code" in data and "message" in data and "requestId" in data:
            raise GZUServerException(
                data["requestId"], data["code"], data["message"])

    @staticmethod
    def check_console_response(response: requests.Response):
        data = response.json()
        if "code" in data and data.get("code") != 0:
            requestId = __class__.response_request_id(response)
            raise GZUServerException(
                requestId, data["code"], data["message"])

    def auth_header(self):
        auth_header = get_default_header()
        auth_header["X-GZU-Request-Id"] = str(uuid.uuid4())
        auth_header["X-GZU-Authorization"] = self.secret_key
        auth_header["X-Appbuilder-Authorization"] = self.secret_key
        logger.debug("Request header: {}\n".format(auth_header))
        return auth_header

    @staticmethod
    def response_request_id(response: requests.Response):
        return response.headers.get("X-GZU-Request-Id", "")

    @staticmethod
    def check_param(func):
        def inner(*args, **kwargs):
            retry = kwargs.get("retry", 0)
            if retry < 0 or not isinstance(retry, int):
                raise InvalidRequestArgumentError(
                    'Rqeuest argument "retry" format error. Expected retry >=0. Got {}'.format(
                        retry
                    )
                )
            timeout = kwargs.get("timeout", None)
            if timeout and not (isinstance(timeout, float) or isinstance(timeout, tuple)):
                raise InvalidRequestArgumentError(
                    "Request argument \"timeout\" format error, Expected timeout be float or tuple of float"
                )
            return func(*args, **kwargs)

        return inner
