from sqlalchemy import Column, JSON, Integer, desc, String, Enum, Boolean, Text, BigInteger, DateTime, ForeignKey, \
    select

from db.setup import Base, AsyncSessionLocal
from sqlalchemy.orm import relationship, class_mapper


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    telegramId = Column(BigInteger, unique=True)
    firstName = Column(String)
    lastName = Column(String)
    username = Column(String, nullable=True)
    languageCode = Column(String, nullable=True)
    referredBy = Column(String, nullable=True)
    referralUsers = Column(JSON, nullable=True)
    createdAt = Column(DateTime, nullable=True)
    isFreeTrial = Column(Boolean, default=True)
    lastUpdated = Column(DateTime, nullable=True)

    def __init__(self, telegramId, firstName, lastName, username, referralUsers, languageCode, isGrantGiven,
                 referredBy, createdAt, lastUpdated):
        self.firstName = firstName
        self.telegramId = telegramId
        self.lastName = lastName
        self.username = username
        self.referralUsers = referralUsers
        self.referredBy = referredBy
        self.languageCode = languageCode
        self.createdAt = createdAt
        self.lastUpdated = lastUpdated
        self.isGrantGiven = isGrantGiven

        super().__init__()

    async def save(self):
        async with AsyncSessionLocal() as session:
            session.add(self)
            await session.commit()

        return self

    @classmethod
    async def get(cls, telegramId):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).filter_by(telegramId=telegramId))
            user = result.scalar_one_or_none()
        return user

    @classmethod
    async def getById(cls, id):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).filter_by(id=id))
            user = result.scalar_one_or_none()
        return user

    @classmethod
    async def isExistsByUserId(cls, telegramId) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).filter_by(telegramId=telegramId))
            user = result.scalar_one_or_none()
        return user is not None

    @classmethod
    async def update(cls, instance, column, value):
        async with AsyncSessionLocal() as session:
            setattr(instance, column, value)
            await session.commit()

    @classmethod
    async def delete(cls, telegramId):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).filter_by(telegramId=telegramId))
            user = result.scalar_one_or_none()
            if user:
                session.delete(user)
                await session.commit()

    def to_dict(self):
        """Converts SQL Alchemy model instance to dictionary."""
        return {c.key: getattr(self, c.key) for c in class_mapper(self.__class__).mapped_table.c}

