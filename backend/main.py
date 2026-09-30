import sys
from pathlib import Path

# Add project root directory to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import routes_health, routes_resume, routes_career, routes_market, routes_skill_gap, routes_roadmap, routes_projects, routes_interview, routes_analysis
from backend.config import settings
from backend.models.database import init_db
from backend.utils.logger import logger

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes application resources and SQLite database schema on startup."""
    logger.info("Starting AI Career Intelligence Backend API...")
    init_db()
    logger.info(f"App running with DEMO_MODE={settings.is_demo_mode()}")
    yield
    logger.info("Shutting down AI Career Intelligence Backend API...")


app = FastAPI(
    title="AI Career Intelligence & Growth Platform API",
    description="Multi-Agent AI platform for resume analysis, career matching, skill gap analysis, personalized roadmaps, project recommendations, and interview prep.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler preventing raw unhandled tracebacks from leaking in responses."""
    logger.error(f"Unhandled endpoint error at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your request. Please check application logs for details.",
            "path": request.url.path,
        },
    )


@app.get("/")
def root():
    """API Root endpoint returning project information."""
    return {
        "name": "AI Career Intelligence & Growth Platform API",
        "status": "online",
        "demo_mode": settings.is_demo_mode(),
        "documentation": "/docs",
        "health_check": "/health",
    }


# Register routes
app.include_router(routes_health.router)
app.include_router(routes_resume.router)
app.include_router(routes_career.router)
app.include_router(routes_market.router)
app.include_router(routes_skill_gap.router)
app.include_router(routes_roadmap.router)
app.include_router(routes_projects.router)
app.include_router(routes_interview.router)
app.include_router(routes_analysis.router)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
