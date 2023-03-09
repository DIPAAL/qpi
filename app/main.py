from fastapi import FastAPI
import socket
from .routers import sql, raster

app = FastAPI()
localIP = socket.gethostbyname(socket.gethostname())

# Include the routers from the router folder
app.include_router(sql.router)
app.include_router(raster.router)


@app.get("/")
def read_root():
    return {"Message": "Hello, i am the Query Processing Interface (QPI) for DIPALL! "
                       f"To see the full documentation for QPI, please visit {localIP}:8000/docs "
                       "Please be careful when using the SQL endpoints, as they are not protected from SQL injection attacks."}


@app.get("/health")
def health():
    return {"status": "ok"}

