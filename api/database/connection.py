from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
import os
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session_db():
    async with AsyncSessionLocal() as session:
        yield session