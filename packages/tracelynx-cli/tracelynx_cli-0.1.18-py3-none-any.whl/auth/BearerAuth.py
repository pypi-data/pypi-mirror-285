import typing

import httpx
from httpx import Request, Response


class BearerAuth(httpx.Auth):

    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(self, request: Request) -> typing.Generator[Request, Response, None]:
        request.headers["Authorization"] = f"Bearer {self.token}"
        yield request
