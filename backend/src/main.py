"""Main entry point for the NEO-Watch FastAPI web service.

Initializes logging, loads environment variables, and sets up API routers
for NEOs, Dashboard, Statistics, and Authentication.
"""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from controller import (
    dashboard_controller,
    game_controller,
    login_controller,
    player_controller,
    statistics_controller,
)
from utils.env_variables import display_values, load_environment_variables
from utils.log_utils import LogMiddleware, get_logger, initialize_logs
#from utils.reset_database import ResetDatabase

logger = get_logger(__name__)

initialize_logs("Webservice")
load_environment_variables()
display_values()


app = FastAPI(title="My Webservice")

app.add_middleware(LogMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Intercepts Pydantic 422 errors to log them.
    """
    body = await request.body()
    body_str = body.decode() if body else "empty body"

    logger.error(f"Validation Error\nErrors: {exc.errors()}\nBody: {body_str}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body_str},
    )


app.include_router(player_controller.router, prefix="/player", tags=["Players"])
app.include_router(login_controller.router, prefix="/login", tags=["Login"])
app.include_router(game_controller.router, prefix="/game", tags=["Games"])
app.include_router(dashboard_controller.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(statistics_controller.router, prefix="/statistics", tags=["Statistics"])

@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to Swagger."""
    return RedirectResponse(url="/docs")


"""@app.get("/reset_database", tags=["Misc"])
async def reset_database():
    Reset the database
    logger.info("Database reset")
    res = ResetDatabase().run()
    return {"message": f"Database reset: {'SUCCESS' if res else 'FAILURE'}"}"""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", "5000")),
    )