from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware   # ⭐ ADD THIS

from app.api.routes import router
from app.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


# ==========================================================
# 🚀 LIFESPAN
# ==========================================================
@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("================================================================================")
    logger.info("AI SALES COACH API STARTING")
    logger.info("================================================================================")
    logger.info(f"Environment: {settings.AWS_REGION}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"S3 Bucket: {settings.S3_BUCKET_NAME}")
    logger.info("================================================================================")

    yield

    logger.info("Shutting down AI Sales Coach API...")


# ==========================================================
# 🚀 FASTAPI APP
# ==========================================================
app = FastAPI(
    title="AI Sales Coach API",
    version="1.0.0",
    lifespan=lifespan
)

# ==========================================================
# ⭐ CORS MIDDLEWARE (THIS FIXES YOUR FRONTEND ERROR)
# ==========================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8501",
        "https://ai-audio-doog.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# ROUTES
# ==========================================================
app.include_router(router)


# ==========================================================
# ROOT TEST
# ==========================================================
@app.get("/")
def root():
    return {"status": "running", "service": "AI Sales Coach API"}
