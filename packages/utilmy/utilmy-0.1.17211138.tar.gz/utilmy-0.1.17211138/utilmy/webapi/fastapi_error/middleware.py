from exception import PlaygroundError, handle_exception
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send


class CustomMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive)
        try:
            await self.app(scope, receive, send)
            return
        except PlaygroundError as err:
            print("Error occured while making request to ACE")

            return handle_exception(request, err)
        except RuntimeError as err:
            # Testcases raise RuntimeError when they get exception on background task
            # Capturing that and handling only ACEError
            if isinstance(err.__cause__, PlaygroundError):
                print("Error occured while making request to ACE")
                return handle_exception(request, err.__cause__)
            raise