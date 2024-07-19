import json
import os
from abc import ABC
from typing import Optional

import requests

from thestage_core.config import THESTAGE_API_URL
from thestage_core.exceptions.auth_exception import AuthException
from thestage_core.exceptions.http_error_exception import HttpClientException


class TheStageApiClientAbstract(ABC):

    _base_url: str = 'https://backend.thestage.ai'

    def __init__(self, timeout: int):
        self.__timeout = timeout

    def _get_host(self, ) -> str:
        return THESTAGE_API_URL or self._base_url

    def _request(
            self,
            method: str,
            url: str,
            data: dict = None,
            query_params: dict = None,
            headers: Optional[dict] = None,
            token: Optional[str] = None,
    ):
        if not data:
            data = {}

        host = self._get_host()
        url = f'{host}{url}'

        request_headers = {
            'Content-Type': 'application/json',
        }

        if token:
            request_headers['Authorization'] = f"Bearer {token}"

        if headers:
            request_headers.update(headers)
        response = requests.request(
            method=method,
            url=url,
            json=data,
            params=query_params,
            headers=request_headers,
            timeout=self.__timeout,

        )
        return self._parse_api_response(response)

    @staticmethod
    def _parse_api_response(raw_response):
        content_type = raw_response.headers.get('content-type')
        message_error = None
        if content_type == 'application/json':
            try:
                result = raw_response.json()
                message_error = result.get('message', None)
            except json.JSONDecodeError:
                raise HttpClientException(
                    message=f"Error http request to thestage, error read json result",
                    status_code=raw_response.status_code,
                )
        else:
            result = raw_response.content.text()

        if raw_response.status_code == 401:
            raise AuthException(
                message=f"Unauthorized",
            )
        elif raw_response.status_code == 403:
            raise HttpClientException(
                message=f"{message_error if message_error else 'Error, your object not present or you dont have permission for him'}",
                status_code=raw_response.status_code,
            )
        elif raw_response.status_code >= 400:
            raise HttpClientException(
                message=f"{message_error if message_error else 'Error, on request, error on validation body'}",
                status_code=raw_response.status_code,
            )
        elif raw_response.status_code < 200 or raw_response.status_code > 300:
            raise HttpClientException(
                message=f"{message_error if message_error else 'Error http request to thestage, backend error'}",
                status_code=raw_response.status_code,
            )

        return result
