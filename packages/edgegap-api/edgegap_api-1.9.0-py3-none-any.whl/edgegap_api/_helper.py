from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable

import aiohttp
from aiohttp import ClientResponse
from aiohttp.client import ClientSession

from ._configuration import ApiConfiguration


class ApiHelper:
    def __init__(self, configuration: ApiConfiguration):
        self.__configuration = configuration

    def __get_headers(self, extra_headers: dict = None) -> dict:
        headers = self.__configuration.default_headers

        if headers is None:
            headers = {}

        if isinstance(extra_headers, dict):
            headers.update(extra_headers)

        return headers

    def __get_url(self, endpoint: str) -> str:
        base_url = str(self.__configuration.base_url)

        if base_url.endswith('/'):
            base_url = base_url[:-1]

        if endpoint.startswith('/'):
            endpoint = endpoint[1:]

        return f'{base_url}/{endpoint}'

    @asynccontextmanager
    async def __request(
        self,
        method: Callable,
        endpoint: str,
        headers: dict = None,
        params: dict = None,
        body: dict = None,
    ) -> AsyncIterator[ClientResponse]:
        _headers = self.__get_headers(headers)
        _url = self.__get_url(endpoint)

        async with aiohttp.ClientSession() as session:
            async with method(
                self=session,
                headers=_headers,
                url=_url,
                params=params,
                json=body,
                timeout=aiohttp.ClientTimeout(total=self.__configuration.timeout_in_seconds),
            ) as response:
                yield response

    @staticmethod
    @asynccontextmanager
    async def session() -> AsyncIterator[ClientSession]:
        async with aiohttp.ClientSession() as session:
            yield session

    @asynccontextmanager
    async def get(
        self,
        endpoint: str,
        params: dict = None,
        headers: dict = None,
    ) -> AsyncIterator[ClientResponse]:
        async with self.__request(
            method=aiohttp.ClientSession.get,
            endpoint=endpoint,
            headers=headers,
            params=params,
        ) as response:
            yield response

    @asynccontextmanager
    async def delete(
        self,
        endpoint: str,
        params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> AsyncIterator[ClientResponse]:
        async with self.__request(
            method=aiohttp.ClientSession.delete,
            endpoint=endpoint,
            headers=headers,
            params=params,
            body=body,
        ) as response:
            yield response

    @asynccontextmanager
    async def post(
        self,
        endpoint: str,
        params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> AsyncIterator[ClientResponse]:
        async with self.__request(
            method=aiohttp.ClientSession.post,
            endpoint=endpoint,
            headers=headers,
            params=params,
            body=body,
        ) as response:
            yield response

    @asynccontextmanager
    async def patch(
        self,
        endpoint: str,
        params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> AsyncIterator[ClientResponse]:
        async with self.__request(
            method=aiohttp.ClientSession.patch,
            endpoint=endpoint,
            headers=headers,
            params=params,
            body=body,
        ) as response:
            yield response

    @asynccontextmanager
    async def put(
        self,
        endpoint: str,
        params: dict = None,
        body: dict = None,
        headers: dict = None,
    ) -> AsyncIterator[ClientResponse]:
        async with self.__request(
            method=aiohttp.ClientSession.put,
            endpoint=endpoint,
            headers=headers,
            params=params,
            body=body,
        ) as response:
            yield response
