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
