"""
Sentinel API — main FastAPI application.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from loguru import logger

from app.api.routers import moderate, health, eval_router
from app.core.config import settings
from app.core.database import init_db

app = FastAPI(
    title="Sentinel Content Intelligence API",
    description="Multimodal content moderation pipeline with RAG-powered policy enforcement.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics endpoint at /metrics
Instrumentator().instrument(app).expose(app)

# Routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(moderate.router, prefix="/api/v1", tags=["moderation"])
app.include_router(eval_router.router, prefix="/api/v1/eval", tags=["evaluation"])


@app.on_event("startup")
async def startup():
    logger.info("Starting Sentinel API...")
    await init_db()
    logger.info("Database initialised.")
