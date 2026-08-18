from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.seed.loader import load_seed_files
from app.api.routes.health import router as health_router
from app.api.routes.transactions import router as transactions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and seed initial demo data
    init_db()
    load_seed_files()
    yield


app = FastAPI(
    title="Decentro Trace API",
    description="AI-powered transaction debugger and deterministic lifecycle reconstruction for fintech payouts.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes under /api
app.include_router(health_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Welcome to Decentro Trace API",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
