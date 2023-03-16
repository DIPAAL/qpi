"""
Main API file for QPI. This file contains the FastAPI app and the routers for the different endpoints.

Note: Does not get called as main when called with uvicorn.
"""
from fastapi import FastAPI
import socket
from .routers import basic_sql, raster
from starlette.responses import RedirectResponse

app = FastAPI()
localIP = socket.gethostbyname(socket.gethostname())

# Include all routers from the router folder
app.include_router(basic_sql.router)
app.include_router(raster.router)


@app.get("/")
def root():
    """Root endpoint. Redirects to the documentation."""
    return RedirectResponse(url="/docs")


@app.get("/health")
def health():
    """Heartbeat endpoint. Returns status message 'ok'."""
    return {"status": "ok"}