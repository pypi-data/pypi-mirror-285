import re
from collections.abc import Iterable
from http.client import HTTPConnection
from typing import Callable, Pattern, Optional, Union

from starlette.authentication import AuthenticationError
from starlette.datastructures import URL
from starlette.requests import Request
from starlette.responses import Response, PlainTextResponse
from starlette.types import ASGIApp, Scope, Receive, Send

from fastapi_pydentity.authentication import AuthenticationBackend


class AuthenticationMiddleware:
    def __init__(
            self,
            app: ASGIApp,
            backend: AuthenticationBackend,
            excluded_urls: Optional[Iterable[Union[Pattern, str]]] = None,
            on_error: Optional[Callable[[HTTPConnection, AuthenticationError], Response]] = None
    ):
        self.app = app
        self.backend = backend
        self.excluded_urls = []
        self.on_error = on_error or self.default_on_error

        for str_or_pattern in excluded_urls:
            if isinstance(str_or_pattern, str):
                self.excluded_urls.append(re.compile(str_or_pattern))
            else:
                self.excluded_urls.append(str_or_pattern)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ["http", "websocket"]:
            await self.app(scope, receive, send)
            return

        request = Request(scope)

        try:
            scope["user"] = await self.backend.authenticate(request)
            scope["auth"] = True
        except AuthenticationError as exc:
            if self.__url_is_excluded(request.url):
                scope["user"] = None
                scope["auth"] = False
            else:
                response = self.on_error(request, exc)

                if scope["type"] == "websocket":
                    await send({"type": "websocket.close", "code": 1000})
                else:
                    await response(scope, receive, send)
                return

        await self.app(scope, receive, send)

    def __url_is_excluded(self, url: URL) -> bool:
        if not self.excluded_urls:
            return False

        for exempt_url in self.excluded_urls:
            if exempt_url.match(url.path):
                return True

        return False

    @staticmethod
    def default_on_error(request: Request, exc: Exception) -> Response:
        return PlainTextResponse(str(exc), status_code=401)
