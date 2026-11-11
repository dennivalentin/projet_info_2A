"""Main entry point for the NEO-Watch FastAPI web service.

Initializes logging, loads environment variables, and sets up API routers
for NEOs, Dashboard, Statistics, and Authentication.
"""
import os
from dao.db_connection import DBConnection

from fastapi import FastAPI, Request, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse
from contextlib import asynccontextmanager

from utils.env_variables import display_values, load_environment_variables
load_environment_variables()
display_values()

from utils.log_utils import LogMiddleware, get_logger, initialize_logs
from utils.reset_database import ResetDatabase
from utils.security import require_admin


from controller import (
    dashboard_controller,
    favourite_controller,
    alert_controller,
    login_controller,
    neo_controller,
    statistics_controller,
    apod_controller,
    import_controller
)

logger = get_logger(__name__)

def run_init_db():
    sql_path = os.path.abspath("data/init_db.sql")
    if not os.path.exists(sql_path):
        return

    try:
        with DBConnection().connection as conn:
            with conn.cursor() as cur: #check if there is already a db in cloudbeaver
                cur.execute(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user');"
                )
                already_initialized = cur.fetchone()[0]

                if not already_initialized:
                    logger.info("Table empty: initialization")
                    with open(sql_path, "r", encoding="utf-8") as f:
                        cur.execute(f.read())
                    logger.info("Table initialized")
                else:
                    logger.info("Table already existing, nothing done")
    except Exception as e:
        logger.error(f"Error init db : {e}")


@asynccontextmanager  #run code at the very beggining of the app
async def lifespan(app: FastAPI):
    run_init_db()
    yield

app = FastAPI(title="NEO-Watch Webservice", lifespan=lifespan)

# Initialization
initialize_logs("Webservice")


app.add_middleware(LogMiddleware)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Intercepts Pydantic 422 errors to log them."""
    body = await request.body()
    body_str = body.decode() if body else "empty body"

    logger.error(f"Validation Error\nErrors: {exc.errors()}\nBody: {body_str}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": body_str},
    )


# API Routers
app.include_router(neo_controller.router, prefix="/neo", tags=["NEOs"])
app.include_router(dashboard_controller.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(statistics_controller.router, prefix="/statistics", tags=["Statistics"])
app.include_router(apod_controller.router, prefix="/apod", tags=["APOD"])
app.include_router(login_controller.router, prefix="/login", tags=["Login"])
app.include_router(alert_controller.router)
app.include_router(favourite_controller.router)
app.include_router(import_controller.router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")


@app.get("/hello/{name}", tags=["Misc"])
async def hello_name(name: str):
    """Display Hello"""
    logger.info("Display Hello")
    return {"message": f"Hello {name}"}


@app.post("/reset_database", tags=["Misc"])
async def reset_database(admin=Depends(require_admin)):
    """Reset the database"""
    logger.info("Database reset")
    success = ResetDatabase().run()

    return {
        "message": f"Database re-initialization - {'SUCCESS' if success else 'FAILURE'}"
    }


# Run the FastAPI application
if __name__ == "__main__":
    import os

    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", "5000")),
    )

    logger.info("Webservice stopped")
