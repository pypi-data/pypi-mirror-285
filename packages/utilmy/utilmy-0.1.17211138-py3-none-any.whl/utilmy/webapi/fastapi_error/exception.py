from fastapi.responses import JSONResponse


class PlaygroundError(Exception):
    pass


def handle_exception(request, exc):
    if isinstance(exc, RuntimeError):
        print("handling runtime exception", exc)
    if isinstance(exc, PlaygroundError):
        print("handling custom exception", exc)
    else:
        print("handling other exception", exc)
    return JSONResponse({"detail": str(exc)})


    