from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import analyze, auth, consent, health, history, profile, user_data

app = FastAPI(
    title="Love Emotion API",
    description="API phân tích sắc thái cảm xúc trong hội thoại tình cảm",
    version="1.0.0",
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
app.include_router(profile.router, prefix="/api", tags=["profile"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(consent.router, prefix="/api", tags=["consent"])
app.include_router(user_data.router, prefix="/api", tags=["user-data"])
app.include_router(auth.router, prefix="/api", tags=["auth"])


@app.get("/")
async def root():
    return {"message": "Love Emotion API"}


@app.get("/health")
async def root_health_check():
    return {
        "status": "healthy",
        "service": "Love Emotion API",
    }
