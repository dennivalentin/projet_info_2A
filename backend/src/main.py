"""Main entry point for the NEO-Watch FastAPI web service.

Initializes logging, loads environment variables, and sets up API routers
for NEOs, Dashboard, Statistics, and Authentication.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from dao.db_connection import DBConnection
from utils.env_variables import display_values, load_environment_variables

load_environment_variables()
display_values()

from controller import (  # noqa: E402 (needs the .env loaded above)
    alert_controller,
    apod_controller,
    dashboard_controller,
    favourite_controller,
    import_controller,
    login_controller,
    neo_controller,
    statistics_controller,
    user_controller,
)
from service.import_scheduler import DailyImportScheduler  # noqa: E402
from utils.log_utils import LogMiddleware, get_logger, initialize_logs  # noqa: E402
from utils.reset_database import ResetDatabase  # noqa: E402

logger = get_logger(__name__)

# Schema fixes applied to databases created with an older init_db.sql
MIGRATIONS = [
    # diameters are in km: NUMERIC(10, 2) rounded every NEO under 5 m to 0
    "ALTER TABLE neo ALTER COLUMN diameter_min TYPE NUMERIC(12, 6);",
    "ALTER TABLE neo ALTER COLUMN diameter_max TYPE NUMERIC(12, 6);",
    "ALTER TABLE alert ALTER COLUMN diameter_min TYPE NUMERIC(12, 6);",
    # NEOs created by users have no NASA id
    "ALTER TABLE neo ALTER COLUMN nasa_id DROP NOT NULL;",
]


def run_init_db():
    """Creates the tables and the seed data on the first launch, or applies MIGRATIONS."""
    try:
        with DBConnection().connection as conn:
            with conn.cursor() as cur:
                # Only look in the current schema (POSTGRES_SCHEMA), not in the whole database.
                # If the schema does not exist yet, current_schema() is NULL: 0 table found.
                cur.execute("""
                    SELECT COUNT(*) AS nb_tables
                    FROM information_schema.tables
                    WHERE table_schema = current_schema()
                      AND table_name IN ('user', 'neo', 'approach', 'favourite', 'import');
                    """)
                already_initialized = cur.fetchone()["nb_tables"] == 5

        if not already_initialized:
            logger.info("Empty database: creation of the tables and of the seed data")
            ResetDatabase().run()
        else:
            logger.info("Tables already existing, applying schema migrations")
            with DBConnection().connection as conn:
                with conn.cursor() as cur:
                    for migration in MIGRATIONS:
                        cur.execute(migration)
    except Exception as e:
        logger.error(f"Error init db : {e}")


@asynccontextmanager  # run code at the very beginning of the app
async def lifespan(app: FastAPI):
    """Runs at the start of the web service, before the first request.

    Creates the database if needed, then starts the automatic daily NASA import
    (FO7), unless AUTO_IMPORT=false in .env.
    """
    run_init_db()
    scheduler = DailyImportScheduler()
    if os.getenv("AUTO_IMPORT", "true").lower() != "false":
        scheduler.start()
    yield
    scheduler.stop()


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

    # jsonable_encoder: an error can contain the exception itself (not JSON serializable)
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors(), "body": body_str}),
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
app.include_router(user_controller.router)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/docs")


# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.getenv("UVICORN_HOST", "127.0.0.1"),
        port=int(os.getenv("UVICORN_PORT", "5000")),
    )

    logger.info("Webservice stopped")
