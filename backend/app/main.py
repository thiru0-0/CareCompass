from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import query, hospitals, estimate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Healthcare Navigator API...")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Healthcare Navigator API",
    description="AI-powered healthcare cost estimator and hospital navigator for India",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "https://your-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router,     prefix="/api/query",     tags=["Query"])
app.include_router(hospitals.router, prefix="/api/hospitals", tags=["Hospitals"])
app.include_router(estimate.router,  prefix="/api/estimate",  tags=["Estimate"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "healthcare-navigator"}
