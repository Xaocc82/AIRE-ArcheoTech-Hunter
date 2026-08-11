"""Private operational health endpoint for container deployments."""

from fastapi import FastAPI

app = FastAPI(docs_url=None, openapi_url=None, redoc_url=None)


@app.get("/healthz")
def health() -> dict[str, str]:
    """Return liveness metadata without connecting to research data stores."""
    return {
        "service": "aire-archeotech-hunter",
        "status": "ok",
        "version": "0.1.0",
    }
