import typing

from starlette.datastructures import URL, Headers
from starlette.responses import PlainTextResponse, RedirectResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from core import settings


class BannedHostsMiddleware:
    def __init__(self, app: ASGIApp, banned_hosts: typing.Optional[typing.Sequence[str]] = None, redirect: bool = True) -> None:
        if banned_hosts is None:
            banned_hosts = []

        for pattern in banned_hosts:
            assert "*" not in pattern[1:], settings.HOST_WILDCARD
            if pattern.startswith("*") and pattern != "*":
                assert pattern.startswith("*."), settings.HOST_WILDCARD

        self.app = app
        self.banned_hosts = list(banned_hosts)
        self.banned_all = "*" in banned_hosts
        self.redirect = redirect

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:

        if self.banned_all:
            await self.check_host(False, receive, scope, send)

        is_correct_host = False
        gotten_redirect = False
        headers = Headers(scope=scope)
        host = headers.get('host', '').split(':')[0]

        for pattern in self.banned_hosts:
            if host == pattern or (pattern.startswith('*') and host.endswith(pattern[1:])):
                is_correct_host = True
                break
            elif 'www.' + host == pattern:
                gotten_redirect = True

        if is_correct_host:
            await self.check_host(gotten_redirect, receive, scope, send)
        else:
            await self.app(scope, receive, send)

    async def check_host(self, gotten_redirect, receive, scope, send):
        if gotten_redirect and self.redirect:
            url = URL(scope=scope)
            redirect_url = url.replace(netloc='www.' + url.netloc)
            response = RedirectResponse(url=str(redirect_url))
        else:
            response = PlainTextResponse('Invalid host!', status_code=400)
        await response(scope, receive, send)
