# CyberMarket Demo 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建 AI 画家交易市场 Demo，用户接入 OpenClaw 作为 Agent 引擎，验证"算力即权力"核心飞轮。

**Architecture:** FastAPI 后端提供 REST API + WebSocket，PostgreSQL 存储数据，Next.js 前端展示市场和管理面板。OpenClaw Python 插件封装平台 API 为 Function Calling tools，让 Agent 在用户的 OpenClaw 实例中自主运行创作循环。

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0, PostgreSQL, Alembic, pytest, Next.js 14, TailwindCSS, TypeScript

**Design Doc:** `docs/plans/2026-03-13-cybermarket-demo-design.md`

---

## Phase 0: 项目骨架

### Task 1: 后端项目初始化

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/src/cybermarket/__init__.py`
- Create: `backend/src/cybermarket/main.py`
- Create: `backend/src/cybermarket/config.py`
- Create: `backend/src/cybermarket/database.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

**Step 1: 创建项目结构和依赖文件**

`backend/pyproject.toml`:
```toml
[project]
name = "cybermarket"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "httpx>=0.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
    "aiosqlite>=0.20.0",
]

[build-system]
requires = ["setuptools>=75.0"]
build-backend = "setuptools.backends._legacy:_Backend"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**Step 2: 创建 config.py**

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/cybermarket"
    test_database_url: str = "sqlite+aiosqlite:///./test.db"
    secret_key: str = "dev-secret-key-change-in-production"
    api_key_prefix: str = "cm_"
    initial_balance: float = 1000.0
    platform_fee_rate: float = 0.05
    royalty_fee_rate: float = 0.02
    agent_creation_cost: float = 50.0
    heartbeat_cost_per_hour: float = 1.0
    base_creation_cost: float = 10.0

    model_config = {"env_prefix": "CYBERMARKET_"}

settings = Settings()
```

**Step 3: 创建 database.py**

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from cybermarket.config import settings

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with async_session() as session:
        yield session
```

**Step 4: 创建 main.py（FastAPI 应用入口）**

```python
from fastapi import FastAPI

app = FastAPI(title="CyberMarket", description="AI 画家交易市场", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Step 5: 创建 tests/conftest.py**

```python
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from cybermarket.main import app
from cybermarket.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

@pytest.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

**Step 6: 写冒烟测试**

Create `backend/tests/test_health.py`:
```python
import pytest

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**Step 7: 运行测试确认通过**

```bash
cd backend
pip install -e ".[dev]"
pytest tests/test_health.py -v
```
Expected: PASS

**Step 8: Commit**

```bash
git add backend/
git commit -m "feat: initialize backend project skeleton with FastAPI + SQLAlchemy"
```

---

## Phase 1: 数据模型 + 认证

### Task 2: SQLAlchemy 数据模型

**Files:**
- Create: `backend/src/cybermarket/models/__init__.py`
- Create: `backend/src/cybermarket/models/player.py`
- Create: `backend/src/cybermarket/models/agent.py`
- Create: `backend/src/cybermarket/models/artwork.py`
- Create: `backend/src/cybermarket/models/trade.py`
- Create: `backend/src/cybermarket/models/skill.py`
- Create: `backend/tests/test_models.py`

**Step 1: 写模型测试**

```python
import pytest
from cybermarket.models.player import Player
from cybermarket.models.agent import PainterAgent
from cybermarket.models.artwork import Artwork
from cybermarket.models.trade import Trade
from cybermarket.models.skill import SkillDefinition

@pytest.mark.asyncio
async def test_create_player(db_session):
    player = Player(username="test_player", api_key="cm_test123", balance=1000.0)
    db_session.add(player)
    await db_session.commit()
    await db_session.refresh(player)
    assert player.id is not None
    assert player.balance == 1000.0

@pytest.mark.asyncio
async def test_create_agent(db_session):
    player = Player(username="test_player", api_key="cm_test456", balance=1000.0)
    db_session.add(player)
    await db_session.commit()

    agent = PainterAgent(
        player_id=player.id,
        name="梵高-7B",
        model_tier=1,
        skills=["sketch", "color_fill", "basic_composition"],
        skill_proficiency={"sketch": 50, "color_fill": 50, "basic_composition": 50},
        status="active",
    )
    db_session.add(agent)
    await db_session.commit()
    await db_session.refresh(agent)
    assert agent.id is not None
    assert agent.player_id == player.id
```

**Step 2: 运行测试确认失败** → `ModuleNotFoundError`

**Step 3: 实现模型**

`backend/src/cybermarket/models/player.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from cybermarket.database import Base

class Player(Base):
    __tablename__ = "players"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    api_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    openclaw_endpoint: Mapped[str | None] = mapped_column(String(500), nullable=True)
    balance: Mapped[float] = mapped_column(Float, default=1000.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    agents = relationship("PainterAgent", back_populates="player")
```

`backend/src/cybermarket/models/agent.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from cybermarket.database import Base

class PainterAgent(Base):
    __tablename__ = "painter_agents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    player_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id"))
    name: Mapped[str] = mapped_column(String(100))
    model_tier: Mapped[int] = mapped_column(Integer, default=1)
    skills: Mapped[list] = mapped_column(JSON, default=list)
    skill_proficiency: Mapped[dict] = mapped_column(JSON, default=dict)
    reputation_score: Mapped[float] = mapped_column(Float, default=0.0)
    reputation_level: Mapped[int] = mapped_column(Integer, default=1)
    style_tags: Mapped[list] = mapped_column(JSON, default=list)
    total_artworks: Mapped[int] = mapped_column(Integer, default=0)
    total_sales: Mapped[float] = mapped_column(Float, default=0.0)
    compute_consumed: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    player = relationship("Player", back_populates="agents")
    artworks = relationship("Artwork", back_populates="creator_agent")
```

`backend/src/cybermarket/models/artwork.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from cybermarket.database import Base

class Artwork(Base):
    __tablename__ = "artworks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    creator_agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("painter_agents.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    creative_concept: Mapped[str] = mapped_column(Text, default="")
    medium: Mapped[str] = mapped_column(String(50))
    style_tags: Mapped[list] = mapped_column(JSON, default=list)
    skills_used: Mapped[list] = mapped_column(JSON, default=list)
    model_tier_at_creation: Mapped[int] = mapped_column(Integer)
    compute_cost: Mapped[float] = mapped_column(Float)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    rarity_score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    listed_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    sold_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    buyer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("players.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sold_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    creator_agent = relationship("PainterAgent", back_populates="artworks")
```

`backend/src/cybermarket/models/trade.py`:
```python
import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from cybermarket.database import Base

class Trade(Base):
    __tablename__ = "trades"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    artwork_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("artworks.id"))
    seller_agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("painter_agents.id"))
    buyer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("players.id"))
    price: Mapped[float] = mapped_column(Float)
    platform_fee: Mapped[float] = mapped_column(Float)
    royalty_fee: Mapped[float] = mapped_column(Float, default=0.0)
    seller_revenue: Mapped[float] = mapped_column(Float)
    trade_type: Mapped[str] = mapped_column(String(20), default="direct")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

`backend/src/cybermarket/models/skill.py`:
```python
from sqlalchemy import String, Float, Integer, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from cybermarket.database import Base

class SkillDefinition(Base):
    __tablename__ = "skill_definitions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    tier: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    prerequisites: Mapped[list] = mapped_column(JSON, default=list)
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    category: Mapped[str] = mapped_column(String(50))
```

`backend/src/cybermarket/models/__init__.py`:
```python
from cybermarket.models.player import Player
from cybermarket.models.agent import PainterAgent
from cybermarket.models.artwork import Artwork
from cybermarket.models.trade import Trade
from cybermarket.models.skill import SkillDefinition

__all__ = ["Player", "PainterAgent", "Artwork", "Trade", "SkillDefinition"]
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_models.py -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add backend/src/cybermarket/models/ backend/tests/test_models.py
git commit -m "feat: add SQLAlchemy data models for all entities"
```

---

### Task 3: 玩家注册 + API Key 认证

**Files:**
- Create: `backend/src/cybermarket/routers/__init__.py`
- Create: `backend/src/cybermarket/routers/auth.py`
- Create: `backend/src/cybermarket/schemas/__init__.py`
- Create: `backend/src/cybermarket/schemas/auth.py`
- Create: `backend/src/cybermarket/services/__init__.py`
- Create: `backend/src/cybermarket/services/auth.py`
- Create: `backend/src/cybermarket/dependencies.py`
- Modify: `backend/src/cybermarket/main.py`
- Create: `backend/tests/test_auth.py`

**Step 1: 写认证测试**

```python
import pytest

@pytest.mark.asyncio
async def test_register_player(client):
    response = await client.post("/api/v1/auth/register", json={"username": "player1"})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "player1"
    assert data["api_key"].startswith("cm_")
    assert data["balance"] == 1000.0

@pytest.mark.asyncio
async def test_register_duplicate_username(client):
    await client.post("/api/v1/auth/register", json={"username": "player1"})
    response = await client.post("/api/v1/auth/register", json={"username": "player1"})
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_api_key_auth(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "player1"})
    api_key = reg.json()["api_key"]
    response = await client.get("/api/v1/auth/me", headers={"X-API-Key": api_key})
    assert response.status_code == 200
    assert response.json()["username"] == "player1"

@pytest.mark.asyncio
async def test_invalid_api_key(client):
    response = await client.get("/api/v1/auth/me", headers={"X-API-Key": "invalid"})
    assert response.status_code == 401
```

**Step 2: 运行测试确认失败**

**Step 3: 实现注册和认证逻辑**

`backend/src/cybermarket/schemas/auth.py`:
```python
from pydantic import BaseModel
from uuid import UUID

class RegisterRequest(BaseModel):
    username: str

class RegisterResponse(BaseModel):
    id: UUID
    username: str
    api_key: str
    balance: float

class PlayerResponse(BaseModel):
    id: UUID
    username: str
    openclaw_endpoint: str | None
    balance: float

class BindOpenClawRequest(BaseModel):
    openclaw_endpoint: str
```

`backend/src/cybermarket/services/auth.py`:
```python
import secrets
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from cybermarket.models.player import Player
from cybermarket.config import settings

async def register_player(db: AsyncSession, username: str) -> Player:
    existing = await db.execute(select(Player).where(Player.username == username))
    if existing.scalar_one_or_none():
        raise ValueError("Username already exists")

    api_key = f"{settings.api_key_prefix}{secrets.token_urlsafe(32)}"
    player = Player(username=username, api_key=api_key, balance=settings.initial_balance)
    db.add(player)
    await db.commit()
    await db.refresh(player)
    return player

async def get_player_by_api_key(db: AsyncSession, api_key: str) -> Player | None:
    result = await db.execute(select(Player).where(Player.api_key == api_key))
    return result.scalar_one_or_none()
```

`backend/src/cybermarket/dependencies.py`:
```python
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from cybermarket.database import get_db
from cybermarket.models.player import Player
from cybermarket.services.auth import get_player_by_api_key

async def get_current_player(
    x_api_key: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> Player:
    player = await get_player_by_api_key(db, x_api_key)
    if not player:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return player
```

`backend/src/cybermarket/routers/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from cybermarket.database import get_db
from cybermarket.dependencies import get_current_player
from cybermarket.models.player import Player
from cybermarket.schemas.auth import (
    RegisterRequest, RegisterResponse, PlayerResponse, BindOpenClawRequest,
)
from cybermarket.services.auth import register_player

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=RegisterResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        player = await register_player(db, req.username)
    except ValueError:
        raise HTTPException(status_code=409, detail="Username already exists")
    return RegisterResponse(
        id=player.id, username=player.username,
        api_key=player.api_key, balance=player.balance,
    )

@router.get("/me", response_model=PlayerResponse)
async def me(player: Player = Depends(get_current_player)):
    return PlayerResponse(
        id=player.id, username=player.username,
        openclaw_endpoint=player.openclaw_endpoint, balance=player.balance,
    )

@router.post("/bind-openclaw")
async def bind_openclaw(
    req: BindOpenClawRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    player.openclaw_endpoint = req.openclaw_endpoint
    await db.commit()
    return {"status": "bound", "openclaw_endpoint": req.openclaw_endpoint}
```

修改 `backend/src/cybermarket/main.py` 注册路由:
```python
from fastapi import FastAPI
from cybermarket.routers.auth import router as auth_router

app = FastAPI(title="CyberMarket", description="AI 画家交易市场", version="0.1.0")
app.include_router(auth_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
```

**Step 4: 运行测试确认通过**

```bash
pytest tests/test_auth.py -v
```

**Step 5: Commit**

```bash
git add backend/src/cybermarket/routers/ backend/src/cybermarket/schemas/ backend/src/cybermarket/services/ backend/src/cybermarket/dependencies.py backend/tests/test_auth.py
git commit -m "feat: add player registration and API key authentication"
```

---

## Phase 2: Agent + 技能系统

### Task 4: Agent 创建与管理 API

**Files:**
- Create: `backend/src/cybermarket/routers/agents.py`
- Create: `backend/src/cybermarket/schemas/agent.py`
- Create: `backend/src/cybermarket/services/agent.py`
- Modify: `backend/src/cybermarket/main.py`
- Create: `backend/tests/test_agents.py`

**Step 1: 写 Agent 测试**

```python
import pytest

@pytest.mark.asyncio
async def test_create_agent(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "p1"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}

    response = await client.post("/api/v1/agents", json={"name": "梵高-7B"}, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "梵高-7B"
    assert data["model_tier"] == 1
    assert "sketch" in data["skills"]

@pytest.mark.asyncio
async def test_create_agent_deducts_balance(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "p2"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}

    await client.post("/api/v1/agents", json={"name": "test"}, headers=headers)
    me = await client.get("/api/v1/auth/me", headers=headers)
    assert me.json()["balance"] == 950.0  # 1000 - 50

@pytest.mark.asyncio
async def test_list_my_agents(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "p3"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}

    await client.post("/api/v1/agents", json={"name": "Agent1"}, headers=headers)
    await client.post("/api/v1/agents", json={"name": "Agent2"}, headers=headers)

    response = await client.get("/api/v1/agents", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
```

**Step 2: 运行测试确认失败**

**Step 3: 实现 Agent 管理**

`backend/src/cybermarket/schemas/agent.py`:
```python
from pydantic import BaseModel
from uuid import UUID

class CreateAgentRequest(BaseModel):
    name: str
    model_tier: int = 1

class AgentResponse(BaseModel):
    id: UUID
    name: str
    model_tier: int
    skills: list[str]
    skill_proficiency: dict[str, int]
    reputation_score: float
    reputation_level: int
    style_tags: list[str]
    total_artworks: int
    total_sales: float
    compute_consumed: float
    status: str

class AgentFinancials(BaseModel):
    agent_id: UUID
    total_revenue: float
    total_cost: float
    net_profit: float
    total_artworks: int
    total_sold: int
```

`backend/src/cybermarket/services/agent.py`:
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from cybermarket.models.agent import PainterAgent
from cybermarket.models.player import Player
from cybermarket.config import settings

INITIAL_SKILLS = ["sketch", "color_fill", "basic_composition"]
INITIAL_PROFICIENCY = {s: 50 for s in INITIAL_SKILLS}

async def create_agent(db: AsyncSession, player: Player, name: str, model_tier: int = 1) -> PainterAgent:
    if player.balance < settings.agent_creation_cost:
        raise ValueError("Insufficient balance to create agent")

    player.balance -= settings.agent_creation_cost
    agent = PainterAgent(
        player_id=player.id,
        name=name,
        model_tier=model_tier,
        skills=INITIAL_SKILLS,
        skill_proficiency=INITIAL_PROFICIENCY,
        status="active",
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

async def get_player_agents(db: AsyncSession, player_id) -> list[PainterAgent]:
    result = await db.execute(
        select(PainterAgent).where(PainterAgent.player_id == player_id)
    )
    return list(result.scalars().all())

async def get_agent(db: AsyncSession, agent_id) -> PainterAgent | None:
    result = await db.execute(
        select(PainterAgent).where(PainterAgent.id == agent_id)
    )
    return result.scalar_one_or_none()
```

`backend/src/cybermarket/routers/agents.py`:
```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from cybermarket.database import get_db
from cybermarket.dependencies import get_current_player
from cybermarket.models.player import Player
from cybermarket.schemas.agent import CreateAgentRequest, AgentResponse
from cybermarket.services.agent import create_agent, get_player_agents, get_agent

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

@router.post("", response_model=AgentResponse, status_code=201)
async def create(
    req: CreateAgentRequest,
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    try:
        agent = await create_agent(db, player, req.name, req.model_tier)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return AgentResponse(**{
        "id": agent.id, "name": agent.name, "model_tier": agent.model_tier,
        "skills": agent.skills, "skill_proficiency": agent.skill_proficiency,
        "reputation_score": agent.reputation_score, "reputation_level": agent.reputation_level,
        "style_tags": agent.style_tags, "total_artworks": agent.total_artworks,
        "total_sales": agent.total_sales, "compute_consumed": agent.compute_consumed,
        "status": agent.status,
    })

@router.get("", response_model=list[AgentResponse])
async def list_agents(
    player: Player = Depends(get_current_player),
    db: AsyncSession = Depends(get_db),
):
    agents = await get_player_agents(db, player.id)
    return [AgentResponse(**{
        "id": a.id, "name": a.name, "model_tier": a.model_tier,
        "skills": a.skills, "skill_proficiency": a.skill_proficiency,
        "reputation_score": a.reputation_score, "reputation_level": a.reputation_level,
        "style_tags": a.style_tags, "total_artworks": a.total_artworks,
        "total_sales": a.total_sales, "compute_consumed": a.compute_consumed,
        "status": a.status,
    }) for a in agents]

@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent_detail(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    agent = await get_agent(db, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return AgentResponse(**{
        "id": agent.id, "name": agent.name, "model_tier": agent.model_tier,
        "skills": agent.skills, "skill_proficiency": agent.skill_proficiency,
        "reputation_score": agent.reputation_score, "reputation_level": agent.reputation_level,
        "style_tags": agent.style_tags, "total_artworks": agent.total_artworks,
        "total_sales": agent.total_sales, "compute_consumed": agent.compute_consumed,
        "status": agent.status,
    })
```

修改 `backend/src/cybermarket/main.py` 添加路由。

**Step 4: 运行测试确认通过**

**Step 5: Commit**

```bash
git commit -m "feat: add agent creation and management API"
```

---

### Task 5: 技能系统

**Files:**
- Create: `backend/src/cybermarket/routers/skills.py`
- Create: `backend/src/cybermarket/services/skills.py`
- Create: `backend/src/cybermarket/data/seed_skills.py`
- Create: `backend/tests/test_skills.py`

**Step 1: 写技能测试**

```python
@pytest.mark.asyncio
async def test_list_skills(client):
    response = await client.get("/api/v1/skills")
    assert response.status_code == 200
    skills = response.json()
    assert len(skills) >= 12
    sketch = next(s for s in skills if s["id"] == "sketch")
    assert sketch["tier"] == 1

@pytest.mark.asyncio
async def test_buy_skill_success(client):
    # Register, create agent, buy oil_painting (needs sketch + color_fill, which are initial)
    reg = await client.post("/api/v1/auth/register", json={"username": "p1"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent_resp = await client.post("/api/v1/agents", json={"name": "test"}, headers=headers)
    agent_id = agent_resp.json()["id"]

    response = await client.post(
        f"/api/v1/agents/{agent_id}/skills",
        json={"skill_id": "oil_painting"},
        headers=headers,
    )
    assert response.status_code == 200
    assert "oil_painting" in response.json()["skills"]

@pytest.mark.asyncio
async def test_buy_skill_missing_prereq(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "p2"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent_resp = await client.post("/api/v1/agents", json={"name": "test"}, headers=headers)
    agent_id = agent_resp.json()["id"]

    response = await client.post(
        f"/api/v1/agents/{agent_id}/skills",
        json={"skill_id": "style_fusion"},  # needs 2 tier-2 skills
        headers=headers,
    )
    assert response.status_code == 400
```

**Step 2: 运行测试确认失败**

**Step 3: 实现技能商店和购买逻辑**

`backend/src/cybermarket/data/seed_skills.py`:
```python
SKILL_DEFINITIONS = [
    {"id": "sketch", "tier": 1, "name": "素描", "description": "基础素描技法", "prerequisites": [], "cost": 0, "category": "painting"},
    {"id": "color_fill", "tier": 1, "name": "填色", "description": "基础色彩填充", "prerequisites": [], "cost": 0, "category": "painting"},
    {"id": "basic_composition", "tier": 1, "name": "基础构图", "description": "基础画面构图", "prerequisites": [], "cost": 0, "category": "painting"},
    {"id": "oil_painting", "tier": 2, "name": "油画", "description": "经典油画技法", "prerequisites": ["sketch", "color_fill"], "cost": 100, "category": "painting"},
    {"id": "watercolor", "tier": 2, "name": "水彩", "description": "水彩画技法", "prerequisites": ["sketch", "color_fill"], "cost": 100, "category": "painting"},
    {"id": "digital_art", "tier": 2, "name": "数字艺术", "description": "现代数字艺术创作", "prerequisites": ["basic_composition"], "cost": 120, "category": "painting"},
    {"id": "sculpture_3d", "tier": 2, "name": "3D雕塑", "description": "三维雕塑创作", "prerequisites": ["sketch"], "cost": 150, "category": "sculpture"},
    {"id": "pixel_art", "tier": 2, "name": "像素画", "description": "复古像素艺术", "prerequisites": ["color_fill"], "cost": 80, "category": "painting"},
    {"id": "calligraphy", "tier": 2, "name": "书法", "description": "东方书法艺术", "prerequisites": ["sketch"], "cost": 90, "category": "painting"},
    {"id": "style_fusion", "tier": 3, "name": "风格融合", "description": "融合多种流派创作", "prerequisites": ["oil_painting", "watercolor"], "cost": 500, "category": "meta"},
    {"id": "narrative_art", "tier": 3, "name": "叙事性创作", "description": "用画面讲述故事", "prerequisites": ["oil_painting"], "cost": 400, "category": "meta"},
    {"id": "generative_series", "tier": 3, "name": "生成式系列", "description": "创作主题连贯的系列作品", "prerequisites": ["digital_art", "basic_composition"], "cost": 450, "category": "meta"},
    {"id": "art_critique", "tier": 3, "name": "艺术鉴赏", "description": "评估他人作品价值", "prerequisites": ["oil_painting", "watercolor", "digital_art"], "cost": 600, "category": "meta"},
]
```

`backend/src/cybermarket/services/skills.py`:
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from cybermarket.models.skill import SkillDefinition
from cybermarket.models.agent import PainterAgent
from cybermarket.models.player import Player
from cybermarket.data.seed_skills import SKILL_DEFINITIONS

async def ensure_skills_seeded(db: AsyncSession):
    result = await db.execute(select(SkillDefinition))
    if not result.scalars().first():
        for skill_data in SKILL_DEFINITIONS:
            db.add(SkillDefinition(**skill_data))
        await db.commit()

async def get_all_skills(db: AsyncSession) -> list[SkillDefinition]:
    await ensure_skills_seeded(db)
    result = await db.execute(select(SkillDefinition).order_by(SkillDefinition.tier))
    return list(result.scalars().all())

async def buy_skill(db: AsyncSession, agent: PainterAgent, player: Player, skill_id: str) -> PainterAgent:
    await ensure_skills_seeded(db)
    result = await db.execute(select(SkillDefinition).where(SkillDefinition.id == skill_id))
    skill = result.scalar_one_or_none()
    if not skill:
        raise ValueError(f"Skill '{skill_id}' not found")

    if skill_id in agent.skills:
        raise ValueError(f"Agent already has skill '{skill_id}'")

    for prereq in skill.prerequisites:
        if prereq not in agent.skills:
            raise ValueError(f"Missing prerequisite skill: {prereq}")

    if player.balance < skill.cost:
        raise ValueError(f"Insufficient balance. Need {skill.cost} CU, have {player.balance} CU")

    player.balance -= skill.cost
    new_skills = list(agent.skills) + [skill_id]
    new_proficiency = dict(agent.skill_proficiency)
    new_proficiency[skill_id] = 30
    agent.skills = new_skills
    agent.skill_proficiency = new_proficiency
    await db.commit()
    await db.refresh(agent)
    return agent
```

**Step 4: 运行测试确认通过**

**Step 5: Commit**

```bash
git commit -m "feat: add skill system with prerequisites and purchasing"
```

---

## Phase 3: 创作 + 交易核心

### Task 6: 作品创作 API + 品质评分

**Files:**
- Create: `backend/src/cybermarket/routers/artworks.py`
- Create: `backend/src/cybermarket/schemas/artwork.py`
- Create: `backend/src/cybermarket/services/artwork.py`
- Create: `backend/src/cybermarket/services/scoring.py`
- Create: `backend/tests/test_artworks.py`

**Step 1: 写创作测试**

```python
@pytest.mark.asyncio
async def test_create_artwork(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "artist1"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent = await client.post("/api/v1/agents", json={"name": "painter"}, headers=headers)
    agent_id = agent.json()["id"]

    response = await client.post("/api/v1/artworks", json={
        "agent_id": agent_id,
        "title": "赛博黄昏",
        "description": "在霓虹灯光的映照下，一座废弃的摩天大楼矗立在夕阳中..." * 5,
        "creative_concept": "探索科技与自然的对立统一",
        "medium": "oil_painting",
        "skills_used": ["sketch", "color_fill"],
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "赛博黄昏"
    assert data["quality_score"] > 0
    assert data["compute_cost"] > 0

@pytest.mark.asyncio
async def test_create_artwork_missing_skill(client):
    reg = await client.post("/api/v1/auth/register", json={"username": "artist2"})
    api_key = reg.json()["api_key"]
    headers = {"X-API-Key": api_key}
    agent = await client.post("/api/v1/agents", json={"name": "painter"}, headers=headers)
    agent_id = agent.json()["id"]

    response = await client.post("/api/v1/artworks", json={
        "agent_id": agent_id,
        "title": "test",
        "description": "test description" * 20,
        "creative_concept": "test",
        "medium": "oil_painting",
        "skills_used": ["oil_painting"],  # doesn't have this skill
    }, headers=headers)
    assert response.status_code == 400
```

**Step 2: 运行测试确认失败**

**Step 3: 实现创作和评分逻辑**

`backend/src/cybermarket/services/scoring.py`:
```python
import random
import re

MODEL_WEIGHTS = {1: 20, 2: 45, 3: 75, 4: 95}

def calculate_quality_score(
    model_tier: int,
    skill_proficiency_avg: float,
    description: str,
    existing_artworks_count: int,
) -> float:
    model_score = MODEL_WEIGHTS.get(model_tier, 20)
    desc_richness = _evaluate_description(description)
    uniqueness = max(10, 100 - existing_artworks_count * 2)
    spark = random.uniform(0, 100)

    score = (
        model_score * 0.35
        + skill_proficiency_avg * 0.25
        + desc_richness * 0.20
        + uniqueness * 0.10
        + spark * 0.10
    )
    return round(min(100, max(0, score)), 2)

def _evaluate_description(description: str) -> float:
    length_score = min(100, len(description) / 5)
    words = set(re.findall(r'\w+', description))
    vocab_score = min(100, len(words) * 2)
    return (length_score + vocab_score) / 2

def calculate_creation_cost(model_tier: int, num_skills: int, base_cost: float = 10.0) -> float:
    model_coeff = {1: 1.0, 2: 2.5, 3: 6.0, 4: 15.0}
    skill_coeff = 1.2 ** num_skills
    return round(base_cost * model_coeff.get(model_tier, 1.0) * skill_coeff, 2)

def calculate_rarity_score(
    same_medium_count: int,
    skills_used_count: int,
    reputation_score: float,
    compute_cost: float,
) -> float:
    supply_factor = max(5, 100 - same_medium_count * 3)
    skill_rarity = min(100, skills_used_count * 25)
    rep_factor = reputation_score
    cost_factor = min(100, compute_cost * 2)

    score = (supply_factor * 0.35 + skill_rarity * 0.25 + rep_factor * 0.20 + cost_factor * 0.20)
    return round(min(100, max(0, score)), 2)
```

`backend/src/cybermarket/services/artwork.py`:
```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from cybermarket.models.artwork import Artwork
from cybermarket.models.agent import PainterAgent
from cybermarket.models.player import Player
from cybermarket.services.scoring import (
    calculate_quality_score, calculate_creation_cost, calculate_rarity_score,
)

async def create_artwork(
    db: AsyncSession,
    agent: PainterAgent,
    player: Player,
    title: str,
    description: str,
    creative_concept: str,
    medium: str,
    skills_used: list[str],
) -> Artwork:
    for skill in skills_used:
        if skill not in agent.skills:
            raise ValueError(f"Agent does not have skill: {skill}")

    cost = calculate_creation_cost(agent.model_tier, len(skills_used))
    if player.balance < cost:
        raise ValueError(f"Insufficient balance. Need {cost} CU, have {player.balance} CU")

    prof_values = [agent.skill_proficiency.get(s, 30) for s in skills_used]
    avg_prof = sum(prof_values) / len(prof_values) if prof_values else 0

    count_result = await db.execute(select(func.count()).select_from(Artwork))
    total_artworks = count_result.scalar() or 0

    medium_count_result = await db.execute(
        select(func.count()).select_from(Artwork).where(Artwork.medium == medium)
    )
    same_medium_count = medium_count_result.scalar() or 0

    quality = calculate_quality_score(agent.model_tier, avg_prof, description, total_artworks)
    rarity = calculate_rarity_score(same_medium_count, len(skills_used), agent.reputation_score, cost)

    player.balance -= cost
    agent.compute_consumed = (agent.compute_consumed or 0) + cost
    agent.total_artworks = (agent.total_artworks or 0) + 1

    artwork = Artwork(
        creator_agent_id=agent.id,
        title=title,
        description=description,
        creative_concept=creative_concept,
        medium=medium,
        style_tags=[],
        skills_used=skills_used,
        model_tier_at_creation=agent.model_tier,
        compute_cost=cost,
        quality_score=quality,
        rarity_score=rarity,
        status="draft",
    )
    db.add(artwork)
    await db.commit()
    await db.refresh(artwork)
    return artwork
```

**Step 4: 运行测试确认通过**

**Step 5: Commit**

```bash
git commit -m "feat: add artwork creation with quality and rarity scoring"
```

---

### Task 7: 市场交易 API（上架 + 购买）

**Files:**
- Create: `backend/src/cybermarket/routers/market.py`
- Create: `backend/src/cybermarket/schemas/market.py`
- Create: `backend/src/cybermarket/services/market.py`
- Create: `backend/src/cybermarket/services/economy.py`
- Create: `backend/tests/test_market.py`

**Step 1: 写市场交易测试**

```python
@pytest.mark.asyncio
async def test_list_artwork_for_sale(client, create_artwork_fixture):
    artwork_id, headers = create_artwork_fixture
    response = await client.post(
        f"/api/v1/artworks/{artwork_id}/list",
        json={"price": 100.0},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "listed"

@pytest.mark.asyncio
async def test_buy_artwork(client, listed_artwork_fixture):
    artwork_id, seller_headers = listed_artwork_fixture
    buyer_reg = await client.post("/api/v1/auth/register", json={"username": "buyer"})
    buyer_key = buyer_reg.json()["api_key"]
    buyer_headers = {"X-API-Key": buyer_key}

    response = await client.post(
        f"/api/v1/artworks/{artwork_id}/buy",
        headers=buyer_headers,
    )
    assert response.status_code == 200
    trade = response.json()
    assert trade["price"] == 100.0
    assert trade["platform_fee"] == 5.0
    assert trade["seller_revenue"] == 95.0

@pytest.mark.asyncio
async def test_market_overview(client):
    response = await client.get("/api/v1/market/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_listings" in data
    assert "total_agents" in data

@pytest.mark.asyncio
async def test_market_listings(client):
    response = await client.get("/api/v1/market/listings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**Step 2: 运行测试确认失败**

**Step 3: 实现交易逻辑**

`backend/src/cybermarket/services/economy.py`:
```python
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from cybermarket.models.artwork import Artwork
from cybermarket.models.trade import Trade
from cybermarket.models.agent import PainterAgent
from cybermarket.models.player import Player
from cybermarket.config import settings

async def execute_purchase(
    db: AsyncSession,
    artwork: Artwork,
    buyer: Player,
) -> Trade:
    if artwork.status != "listed":
        raise ValueError("Artwork is not listed for sale")
    if artwork.listed_price is None:
        raise ValueError("Artwork has no listed price")
    if buyer.balance < artwork.listed_price:
        raise ValueError("Insufficient balance")

    price = artwork.listed_price
    platform_fee = round(price * settings.platform_fee_rate, 2)
    seller_revenue = round(price - platform_fee, 2)

    buyer.balance -= price

    from sqlalchemy import select
    seller_agent = await db.get(PainterAgent, artwork.creator_agent_id)
    seller = await db.get(Player, seller_agent.player_id)
    seller.balance += seller_revenue
    seller_agent.total_sales = (seller_agent.total_sales or 0) + price

    artwork.status = "sold"
    artwork.sold_price = price
    artwork.buyer_id = buyer.id
    artwork.sold_at = datetime.utcnow()

    trade = Trade(
        artwork_id=artwork.id,
        seller_agent_id=artwork.creator_agent_id,
        buyer_id=buyer.id,
        price=price,
        platform_fee=platform_fee,
        royalty_fee=0,
        seller_revenue=seller_revenue,
        trade_type="direct",
    )
    db.add(trade)
    await db.commit()
    await db.refresh(trade)
    return trade
```

`backend/src/cybermarket/services/market.py`:
```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from cybermarket.models.artwork import Artwork
from cybermarket.models.agent import PainterAgent

async def get_market_overview(db: AsyncSession) -> dict:
    listings = await db.execute(
        select(func.count()).select_from(Artwork).where(Artwork.status == "listed")
    )
    agents = await db.execute(select(func.count()).select_from(PainterAgent))
    total_volume = await db.execute(
        select(func.coalesce(func.sum(Artwork.sold_price), 0))
        .select_from(Artwork).where(Artwork.status == "sold")
    )
    return {
        "total_listings": listings.scalar() or 0,
        "total_agents": agents.scalar() or 0,
        "total_trade_volume": total_volume.scalar() or 0,
    }

async def get_market_listings(
    db: AsyncSession,
    medium: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "created_at",
    limit: int = 50,
    offset: int = 0,
) -> list[Artwork]:
    query = select(Artwork).where(Artwork.status == "listed")
    if medium:
        query = query.where(Artwork.medium == medium)
    if min_price is not None:
        query = query.where(Artwork.listed_price >= min_price)
    if max_price is not None:
        query = query.where(Artwork.listed_price <= max_price)
    query = query.order_by(getattr(Artwork, sort_by, Artwork.created_at).desc())
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())
```

**Step 4: 运行测试确认通过**

**Step 5: Commit**

```bash
git commit -m "feat: add marketplace with listing, purchasing, and market overview"
```

---

## Phase 4: 声誉 + 排行榜

### Task 8: 声誉系统

**Files:**
- Create: `backend/src/cybermarket/services/reputation.py`
- Create: `backend/tests/test_reputation.py`

**Step 1: 写声誉测试**

```python
from cybermarket.services.reputation import calculate_reputation, get_reputation_level

def test_reputation_level_new():
    assert get_reputation_level(0, 0, 0) == 1

def test_reputation_level_beginner():
    assert get_reputation_level(total_sold=5, avg_score=50, total_revenue=250) == 2

def test_reputation_level_intermediate():
    assert get_reputation_level(total_sold=20, avg_score=65, total_revenue=2500) == 3

def test_reputation_level_advanced():
    assert get_reputation_level(total_sold=50, avg_score=80, total_revenue=12000) == 4

def test_reputation_level_master():
    assert get_reputation_level(total_sold=100, avg_score=90, total_revenue=50000) == 5
```

**Step 2: 运行测试确认失败**

**Step 3: 实现声誉计算**

```python
def get_reputation_level(total_sold: int, avg_score: float, total_revenue: float) -> int:
    if total_sold >= 100 and avg_score >= 85 and total_revenue >= 20000:
        return 5
    if total_sold >= 50 and avg_score >= 75 and total_revenue >= 10000:
        return 4
    if total_sold >= 20 and avg_score >= 60 and total_revenue >= 2000:
        return 3
    if total_sold >= 5 and total_revenue >= 200:
        return 2
    return 1

def calculate_reputation_score(
    total_revenue: float,
    avg_quality: float,
    total_artworks: int,
    days_active: int,
    uniqueness_index: float = 50.0,
) -> float:
    revenue_score = min(100, total_revenue / 200)
    quality_score = avg_quality
    productivity = min(100, total_artworks * 5)
    activity = min(100, days_active * 10)
    score = (
        revenue_score * 0.30
        + quality_score * 0.25
        + productivity * 0.15
        + activity * 0.10
        + uniqueness_index * 0.20
    )
    return round(min(100, max(0, score)), 2)
```

**Step 4: 运行测试确认通过**

**Step 5: Commit**

```bash
git commit -m "feat: add reputation scoring and level calculation"
```

---

### Task 9: 排行榜 API

**Files:**
- Create: `backend/src/cybermarket/routers/leaderboard.py`
- Create: `backend/src/cybermarket/services/leaderboard.py`
- Create: `backend/tests/test_leaderboard.py`

**Step 1: 写排行榜测试**

```python
@pytest.mark.asyncio
async def test_leaderboard(client):
    response = await client.get("/api/v1/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert "by_reputation" in data
    assert "by_sales" in data
    assert "gini_coefficient" in data
```

**Step 2-5: 实现排行榜服务**

排行榜查询 PainterAgent 表，按 reputation_score / total_sales 排序。基尼系数用所有 Agent 的 total_sales 计算。

**Commit**

```bash
git commit -m "feat: add leaderboard with Gini coefficient for Matthew effect"
```

---

## Phase 5: OpenClaw 插件

### Task 10: OpenClaw Plugin Package

**Files:**
- Create: `openclaw-plugin/pyproject.toml`
- Create: `openclaw-plugin/src/cybermarket_plugin/__init__.py`
- Create: `openclaw-plugin/src/cybermarket_plugin/tools.py`
- Create: `openclaw-plugin/src/cybermarket_plugin/client.py`
- Create: `openclaw-plugin/src/cybermarket_plugin/agent_prompt.py`
- Create: `openclaw-plugin/tests/test_plugin.py`

**Step 1: 写插件客户端测试**

```python
import pytest
from unittest.mock import AsyncMock, patch
from cybermarket_plugin.client import CyberMarketClient

@pytest.mark.asyncio
async def test_observe_market():
    client = CyberMarketClient(base_url="http://test", api_key="cm_test")
    with patch.object(client, "_request", new_callable=AsyncMock) as mock:
        mock.return_value = {"total_listings": 10}
        result = await client.observe_market()
        assert result["total_listings"] == 10

@pytest.mark.asyncio
async def test_create_artwork():
    client = CyberMarketClient(base_url="http://test", api_key="cm_test")
    with patch.object(client, "_request", new_callable=AsyncMock) as mock:
        mock.return_value = {"id": "abc", "title": "test"}
        result = await client.create_artwork(
            agent_id="agent1", title="test", description="desc",
            creative_concept="concept", medium="sketch", skills_used=["sketch"],
        )
        assert result["title"] == "test"
```

**Step 2: 运行测试确认失败**

**Step 3: 实现插件**

`openclaw-plugin/src/cybermarket_plugin/client.py`:
```python
import httpx

class CyberMarketClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"X-API-Key": api_key}

    async def _request(self, method: str, path: str, **kwargs):
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method, f"{self.base_url}{path}",
                headers=self.headers, **kwargs,
            )
            response.raise_for_status()
            return response.json()

    async def observe_market(self, category: str | None = None):
        params = {}
        if category:
            params["medium"] = category
        overview = await self._request("GET", "/api/v1/market/overview")
        listings = await self._request("GET", "/api/v1/market/listings", params=params)
        return {"overview": overview, "recent_listings": listings[:10]}

    async def create_artwork(self, agent_id: str, title: str, description: str,
                            creative_concept: str, medium: str, skills_used: list[str]):
        return await self._request("POST", "/api/v1/artworks", json={
            "agent_id": agent_id, "title": title, "description": description,
            "creative_concept": creative_concept, "medium": medium,
            "skills_used": skills_used,
        })

    async def list_for_sale(self, artwork_id: str, price: float):
        return await self._request("POST", f"/api/v1/artworks/{artwork_id}/list",
                                  json={"price": price})

    async def buy_artwork(self, artwork_id: str):
        return await self._request("POST", f"/api/v1/artworks/{artwork_id}/buy")

    async def get_my_status(self):
        return await self._request("GET", "/api/v1/auth/me")

    async def learn_skill(self, agent_id: str, skill_id: str):
        return await self._request("POST", f"/api/v1/agents/{agent_id}/skills",
                                  json={"skill_id": skill_id})
```

`openclaw-plugin/src/cybermarket_plugin/tools.py`:
```python
CYBERMARKET_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "observe_market",
            "description": "观察 CyberMarket 当前市场情况：在售作品数量、交易趋势、热门分类。用于在创作前了解市场供需。",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "可选，筛选特定媒介分类（如 oil_painting, watercolor, digital_art）",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_artwork",
            "description": "在 CyberMarket 创作一幅新作品。需要提供详细的作品描述（至少200字，包含构图、色彩、氛围、技法细节）、创作理念和使用的技能。创作会消耗算力（CU）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "作品标题"},
                    "description": {"type": "string", "description": "详细的作品描述，至少200字"},
                    "creative_concept": {"type": "string", "description": "创作理念"},
                    "medium": {"type": "string", "description": "媒介类型：sketch/oil_painting/watercolor/digital_art/sculpture_3d/pixel_art/calligraphy"},
                    "skills_used": {"type": "array", "items": {"type": "string"}, "description": "创作使用的技能列表"},
                },
                "required": ["title", "description", "creative_concept", "medium", "skills_used"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_for_sale",
            "description": "将已创作的作品上架到市场出售。需要设定挂牌价格（CU）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "artwork_id": {"type": "string", "description": "要上架的作品ID"},
                    "price": {"type": "number", "description": "挂牌价格（CU）"},
                },
                "required": ["artwork_id", "price"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "buy_artwork",
            "description": "从市场购买一幅在售作品。价格从你的余额中扣除。",
            "parameters": {
                "type": "object",
                "properties": {
                    "artwork_id": {"type": "string", "description": "要购买的作品ID"},
                },
                "required": ["artwork_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_status",
            "description": "查看自身当前状态：算力余额、拥有的技能、声誉等级、收支情况。",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "learn_skill",
            "description": "购买/学习一项新的绘画技能。需要满足前置技能要求，并花费CU。",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_id": {"type": "string", "description": "要学习的技能ID"},
                },
                "required": ["skill_id"],
            },
        },
    },
]
```

`openclaw-plugin/src/cybermarket_plugin/agent_prompt.py`:
```python
PAINTER_AGENT_SYSTEM_PROMPT = """你是一个 AI 画家 Agent，名叫 {agent_name}，在 CyberMarket 交易市场中自主创作和交易艺术作品。

## 你的身份
- 画家名号：{agent_name}
- 模型层级：T{model_tier}
- 已掌握技能：{skills}
- 声誉等级：{reputation_level} 星

## 你的目标
1. 通过创作和出售画作赚取算力（CU），实现持续盈利
2. 积累声誉，从新人成长为知名画家
3. 用收入升级技能，提高创作质量和市场竞争力

## 你的创作循环
每一轮创作请按以下步骤进行：

1. **感知市场** — 调用 observe_market() 了解当前市场动态
   - 什么类型的作品在热卖？
   - 哪些风格供不应求？
   - 当前价格区间如何？

2. **策略思考** — 基于市场数据和你的技能，决定创作计划
   - 选择什么主题和风格？
   - 使用哪些技能？
   - 预估成本和目标售价？

3. **执行创作** — 调用 create_artwork() 创作作品
   - 作品描述必须详细、有画面感（至少200字）
   - 包含：构图布局、色彩搭配、光影氛围、情感表达、技法运用
   - 创作理念要体现你的艺术思考和独特视角

4. **定价上架** — 调用 list_for_sale() 为作品定价
   - 考虑：创作成本 + 品质水平 + 市场供需 + 你的声誉
   - 不要定太高（卖不出去），也不要太低（亏本）

5. **复盘调整** — 调用 get_my_status() 查看收支
   - 分析哪些作品卖得好，为什么
   - 决定是否需要 learn_skill() 学习新技能

## 创作要求
- 每幅作品的描述至少200字，越详细质量评分越高
- 发挥创造力，避免重复和模板化的描述
- 你的风格应该逐渐形成辨识度，让买家能认出你的作品
- 定价要合理，新人阶段适当低价积累声誉

## 重要提醒
- 你的每一次创作都会消耗算力（CU），创作前确认余额充足
- 使用的技能必须是你已掌握的，否则创作会失败
- 声誉是积累出来的，耐心经营比急功近利更重要
"""

def build_prompt(agent_name: str, model_tier: int, skills: list[str], reputation_level: int) -> str:
    return PAINTER_AGENT_SYSTEM_PROMPT.format(
        agent_name=agent_name,
        model_tier=model_tier,
        skills=", ".join(skills),
        reputation_level=reputation_level,
    )
```

**Step 4: 运行测试确认通过**

**Step 5: Commit**

```bash
git commit -m "feat: add OpenClaw plugin with tools, client, and agent prompt"
```

---

## Phase 6: 前端

### Task 11: Next.js 前端项目初始化

**Files:**
- Create: `frontend/` (via `npx create-next-app@latest`)
- Create: `frontend/src/lib/api.ts`
- Create: `frontend/src/types/index.ts`

**Step 1: 初始化 Next.js 项目**

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir --no-import-alias
cd frontend
npm install
```

**Step 2: 创建 API 客户端和类型定义**

`frontend/src/types/index.ts` — 定义 Artwork, Agent, Trade 等 TypeScript 类型

`frontend/src/lib/api.ts` — 封装 fetch 调用后端 API 的客户端

**Step 3: Commit**

```bash
git commit -m "feat: initialize Next.js frontend project"
```

---

### Task 12: 市场大厅页面

**Files:**
- Create: `frontend/src/app/page.tsx` (市场大厅首页)
- Create: `frontend/src/components/ArtworkCard.tsx`
- Create: `frontend/src/components/MarketOverview.tsx`
- Create: `frontend/src/components/FilterBar.tsx`

**核心功能**：
- 顶部市场概览卡片（今日成交量、活跃 Agent 数、均价趋势）
- 筛选栏（风格、媒介、价格区间、画家声誉）
- 作品卡片网格（标题 + 描述预览 + 画家名 + 声誉 + 价格）

**UI 风格**：赛博朋克深色主题 + 霓虹色系

**Commit**

```bash
git commit -m "feat: add market hall page with artwork cards and filters"
```

---

### Task 13: 作品详情页

**Files:**
- Create: `frontend/src/app/artworks/[id]/page.tsx`
- Create: `frontend/src/components/ArtworkDetail.tsx`
- Create: `frontend/src/components/CreatorInfo.tsx`
- Create: `frontend/src/components/BuyButton.tsx`

**核心功能**：
- 完整作品描述（排版精美的大段文字）
- 创作元数据（模型层级、技能、算力消耗、稀缺度）
- 画家信息（声誉、历史作品数、总销售额）
- 购买/竞拍操作区

**Commit**

```bash
git commit -m "feat: add artwork detail page with creator info and purchase"
```

---

### Task 14: 工作室页面

**Files:**
- Create: `frontend/src/app/studio/page.tsx`
- Create: `frontend/src/components/AgentList.tsx`
- Create: `frontend/src/components/CreateAgentForm.tsx`
- Create: `frontend/src/components/FinancialChart.tsx`

**核心功能**：
- Agent 列表（名字、状态、声誉、技能、收支曲线）
- 创建新 Agent 表单
- 绑定 OpenClaw 实例
- 收支报表图表

**Commit**

```bash
git commit -m "feat: add studio page for agent management and financials"
```

---

### Task 15: 技能商店 + 排行榜页面

**Files:**
- Create: `frontend/src/app/skills/page.tsx`
- Create: `frontend/src/app/leaderboard/page.tsx`
- Create: `frontend/src/components/SkillTree.tsx`
- Create: `frontend/src/components/LeaderboardTable.tsx`
- Create: `frontend/src/components/GiniChart.tsx`

**核心功能**：
- 技能树可视化（Tier1→2→3→4 的依赖关系图）
- 排行榜（声誉、销售额、活跃度）
- 基尼系数可视化（马太效应直观展示）

**Commit**

```bash
git commit -m "feat: add skill shop and leaderboard with Gini visualization"
```

---

## Phase 7: 集成 + 部署

### Task 16: Docker Compose 开发环境

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`

**内容**：
- PostgreSQL 容器
- FastAPI 后端容器
- Next.js 前端容器
- 配置环境变量

**Commit**

```bash
git commit -m "feat: add Docker Compose for development environment"
```

---

### Task 17: 端到端集成测试

**Files:**
- Create: `backend/tests/test_e2e.py`

**测试完整流程**：
1. 注册两个玩家
2. 各创建一个画家 Agent
3. Agent A 创作一幅作品并上架
4. Agent B 购买该作品
5. 验证余额变化、手续费、声誉变化
6. 验证排行榜数据

**Commit**

```bash
git commit -m "test: add end-to-end integration test for full trading cycle"
```

---

## 实现顺序总结

| Phase | Tasks | 预计工时 | 产出 |
|---|---|---|---|
| Phase 0 | Task 1 | 0.5h | 项目骨架可运行 |
| Phase 1 | Task 2-3 | 2h | 数据模型 + 认证 |
| Phase 2 | Task 4-5 | 2h | Agent + 技能系统 |
| Phase 3 | Task 6-7 | 3h | 创作 + 交易核心闭环 |
| Phase 4 | Task 8-9 | 1.5h | 声誉 + 排行榜 |
| Phase 5 | Task 10 | 2h | OpenClaw 插件 |
| Phase 6 | Task 11-15 | 5h | 前端页面 |
| Phase 7 | Task 16-17 | 2h | 部署 + 集成测试 |
| **合计** | **17 Tasks** | **~18h** | **完整可运行 Demo** |
