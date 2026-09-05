from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.firebase import initialize_firebase_admin
from app.database.connection import init_database_for_development
from app.routes import analyze, auth, consent, health, history, ocr, profile, user_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_firebase_admin()
    await init_database_for_development()
    yield


app = FastAPI(
    title="CodeSense AI API",
    description="API hệ thống gia sư lập trình thích ứng (Adaptive Programming Tutor for Beginner C# OOP Students)",
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

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(ocr.router, prefix="/api", tags=["ocr"])
app.include_router(profile.router, prefix="/api", tags=["profile"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(consent.router, prefix="/api", tags=["consent"])
app.include_router(user_data.router, prefix="/api", tags=["user-data"])
app.include_router(auth.router, prefix="/api", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "CodeSense AI API"}


@app.get("/health")
async def root_health_check():
    return {
        "status": "healthy",
        "service": "CodeSense AI API",
    }
