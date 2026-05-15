"""
Application entrypoint for local development and ASGI servers.
"""

from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
from fastapi import FastAPI

app = FastAPI(title=settings.app_name, version="0.1.0")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
