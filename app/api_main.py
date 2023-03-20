"""
Main API file for QPI. This file contains the FastAPI app and the routers for the different endpoints.

Note: Does not get called as main when called with uvicorn.
"""
from fastapi import FastAPI
from app.routers import router_main
from starlette.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Include main router, which includes all other routers
app.include_router(router_main.router_main)


@app.get("/", include_in_schema=False)
def root():
    """Root endpoint. Redirects to the documentation."""
    return RedirectResponse(url="/docs")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="DIPAAL API",
        version="1.0.0",
        description="API for querying the DIPAAL data warehouse.",
        routes=app.routes,
    )
    # Add security schemes to OpenAPI spec
    openapi_schema["components"]["securitySchemes"] = {
        "Cloudflare Client ID": {
            "type": "apiKey",
            "in": "header",
            "name": "CF-Access-Client-Id",
            "description": "Cloudflare Access Client ID",
            "scheme": "https",
        },
        "Cloudflare Client Secret": {
            "type": "apiKey",
            "in": "header",
            "name": "CF-Access-Client-Secret",
            "description": "Cloudflare Access Client Secret",
            "scheme": "https"
        },
        "Cloudflare Authorization JWT Cookie": {
            "type": "apiKey",
            "in": "cookie",
            "name": "CF_Authorization",
            "description": "Cloudflare Access JWT Cookie, which is set by Cloudflare Access, "
                           "when authorized with Cloudflare Client ID and Client Secret",
            "scheme": "https"
        }
    }

    # Either use both Cloudflare Access Client ID and Client Secret or Cloudflare Access JWT Cookie
    openapi_schema["security"] = [
        {
            "Cloudflare Client ID": [],
            "Cloudflare Client Secret": []
        },
        {
            "Cloudflare Authorization JWT Cookie": []
        }
    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
