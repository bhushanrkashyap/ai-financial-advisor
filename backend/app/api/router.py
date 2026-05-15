"""Aggregate API routers (versioned sub-routers mount here)."""

from fastapi import APIRouter

from app.api.credit import credit_router

api_router = APIRouter()
api_router.include_router(credit_router)
