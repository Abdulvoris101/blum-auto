from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from apps.common.settings import settings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async_engine = None

try:
    async_engine = create_async_engine(settings.DB_URL)
except Exception as error:
    print("Error while connecting to PostgreSQL:", error)


AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


# Create a base class for declarative models
Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        await session.close()


