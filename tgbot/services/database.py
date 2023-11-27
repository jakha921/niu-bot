import asyncpg
from tgbot.config import Config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from tgbot.services.db_base import Base

async def create_db_session(config: Config) -> AsyncSession:
    """Create DB session"""
    auth_data = {
        "user": config.db.user,
        "password": config.db.password,
        "host": config.db.host,
        "port": config.db.port,
        "database": config.db.database,
    }

    print('auth_data', auth_data)

    # Connect to the PostgreSQL default database
    conn = await asyncpg.connect(**auth_data)

    # Check if the target database exists
    db_exists = await conn.fetchval(
        "SELECT EXISTS(SELECT 1 FROM pg_database WHERE datname=$1)", config.db.database
    )

    # If the database doesn't exist, create it
    if not db_exists:
        await conn.execute(f"CREATE DATABASE {config.db.database}")

    # Close the connection to the default database
    await conn.close()

    # Connect to the target database
    db_auth_data = {**auth_data, "database": config.db.database}
    db_conn = await asyncpg.connect(**db_auth_data)

    # Create an async session
    engine = create_async_engine(
        f"postgresql+asyncpg://{auth_data['user']}:{auth_data['password']}@{auth_data['host']}:{auth_data['port']}/{config.db.database}",
        future=True
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create an async session
    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    return async_session
