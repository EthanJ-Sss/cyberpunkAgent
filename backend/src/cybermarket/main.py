from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cybermarket.database import engine, Base
from cybermarket.routers.auth import router as auth_router
from cybermarket.routers.agents import router as agents_router
from cybermarket.routers.skills import router as skills_router
from cybermarket.routers.artworks import router as artworks_router
from cybermarket.routers.market import router as market_router
from cybermarket.routers.leaderboard import router as leaderboard_router

import cybermarket.models  # noqa: F401 — ensure all models are registered with Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="CyberMarket",
    description="AI 画家交易市场",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(agents_router)
app.include_router(skills_router)
app.include_router(artworks_router)
app.include_router(market_router)
app.include_router(leaderboard_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
