import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.research import router as research_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend for AI Research & Report Generation Agent",
    version="1.0.0"
)

# Configurable CORS with credentials set to False
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.FRONTEND_CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {
        "project": settings.PROJECT_NAME,
        "status": "online",
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    # Using 127.0.0.1 strictly for local development. 
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=settings.PORT, 
        reload=True
    )