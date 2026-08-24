from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": f"Database integrity error: {exc.orig.diag.message_detail if exc.orig.diag else exc.args[0]}"},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
