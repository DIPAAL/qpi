"""
Main API file for QPI. This file contains the FastAPI app and the routers for the different endpoints.

Note: Does not get called as main when called with uvicorn.
"""
from fastapi import FastAPI
import socket
from .routers import basic_sql, raster, statistics

app = FastAPI()
localIP = socket.gethostbyname(socket.gethostname())

# Include all routers from the router folder
app.include_router(basic_sql.router)
app.include_router(raster.router)
app.include_router(statistics.router)


@app.get("/")
def root():
    """Root endpoint. Returns a message with the IP address of the QPI and a warning."""
    return {"Message": "Hello, i am the Query Processing Interface (QPI) for DIPAAL! "
                       "Please be careful when using the SQL endpoints, as they are not protected."}


@app.get("/health")
def health():
    """Heartbeat endpoint. Returns status message 'ok'."""
    return {"status": "ok"}
