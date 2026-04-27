from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .routers import auth, profiles, matching, messages, health, quantum


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler: startup and shutdown events."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Syndi AI API",
    description="AI-native co-founder matching platform backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(profiles.router, prefix="/api/v1/profiles", tags=["Profiles"])
app.include_router(matching.router, prefix="/api/v1/matching", tags=["Matching"])
app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messages"])
app.include_router(quantum.router, prefix="/api/v1/quantum", tags=["Quantum Destiny"])


@app.get("/")
async def root():
    return {"message": "Syndi AI API v1.0", "docs": "/docs"}
