from fastapi import FastAPI
import socket
from .routers import basic_sql, raster, statistics

app = FastAPI()
localIP = socket.gethostbyname(socket.gethostname())

# Include the routers from the router folder
app.include_router(basic_sql.router)
app.include_router(raster.router)
app.include_router(statistics.router)


@app.get("/")
def root():
    return {"Message": "Hello, i am the Query Processing Interface (QPI) for DIPALL! "
                       f"To see the full documentation for QPI, please visit {localIP}:8000/docs "
                       "Please be careful when using the SQL endpoints, as they are not protected."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/test/{text}")
def test(text: str):
    return {"status": f"{text}"}

