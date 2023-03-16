"""
Main API file for QPI. This file contains the FastAPI app and the routers for the different endpoints.

Note: Does not get called as main when called with uvicorn.
"""
from fastapi import FastAPI
from .routers import router_main
from starlette.responses import RedirectResponse

app = FastAPI()

# Include main router, which includes all other routers
app.include_router(router_main.router_main)


@app.get("/")
def root():
    """Root endpoint. Redirects to the documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    """Heartbeat endpoint. Returns status message 'ok'."""
    return {"status": "ok"}
