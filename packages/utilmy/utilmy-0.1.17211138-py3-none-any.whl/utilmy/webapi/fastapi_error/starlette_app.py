from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.middleware.errors import ServerErrorMiddleware
from starlette.responses import JSONResponse, Response
from starlette.routing import Route
from middleware import CustomMiddleware
from starlette.middleware import Middleware
from exception import PlaygroundError


def error_handler(request, exc):
    print("error handled gracefully")


def raise_exception():
    raise PlaygroundError("Something went wrong")


async def endpoint(request):
    # background = BackgroundTasks(tasks=[])
    return Response("Hello, world!", background=BackgroundTask(raise_exception))


app = Starlette(
    routes=[Route("/", endpoint=endpoint)],
    exception_handlers={Exception: error_handler},
    middleware=[Middleware(CustomMiddleware, debug=True)],
)

