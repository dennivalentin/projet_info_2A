import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from controller import (
    alert_controller,
    favourite_controller,
    #login_controller,
    neo_controller,
    #statistics_controller,
    #dashboard_controller
)
from utils.env_variables import display_values, load_environment_variables
from utils.log_utils import LogMiddleware, get_logger, initialize_logs
#from utils.reset_database import ResetDatabase

logger = get_logger(__name__)

initialize_logs("Webservice")
load_environment_variables()
display_values()

app = FastAPI(title="NEO Tracker Webservice")

app.add_middleware(LogMiddleware)

#app.include_router(login_controller.router, prefix="/login", tags=["Login"])
app.include_router(favourite_controller.router)
app.include_router(alert_controller.router)
#app.include_router(dashboard_controller.router)
app.include_router(neo_controller.router)
#app.include_router(statistics_controller.router)


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