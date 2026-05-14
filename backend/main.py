"""
Application entrypoint for local development and ASGI servers.
"""

from app.api.router import api_router
from app.core.config import settings
from fastapi import FastAPI

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
