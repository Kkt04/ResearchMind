from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.cognee_client import init_cognee
from app.api import papers, query, feedback, generate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🧠 Starting ResearchMind backend...")
    await init_cognee()
    yield
    logger.info("👋 Shutting down ResearchMind backend...")


app = FastAPI(
    title="ResearchMind API",
    description="The Living Literature Review Agent — powered by Cognee",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router, prefix="/api")
app.include_router(query.router, prefix="/api")
app.include_router(feedback.router, prefix="/api")
app.include_router(generate.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "ResearchMind API",
        "status": "running",
        "description": "The Living Literature Review Agent powered by Cognee",
        "cognee_apis_used": ["remember()", "recall()", "improve()/memify()", "forget()"],
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}