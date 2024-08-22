from sqlalchemy import Column, Integer, BigInteger, select
from db.setup import Base, AsyncSessionLocal


class Admin(Base):
    __tablename__ = 'admin'

    id = Column(Integer, primary_key=True)
    telegramId = Column(BigInteger)

    def __init__(self, telegramId):
        self.telegramId = telegramId

    @classmethod
    async def isAdmin(cls, telegramId):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    admin = await session.execute(
                        select(Admin).filter_by(telegramId=telegramId)
                    )
                    admin = admin.scalars().first()
                except Exception as e:
                    raise e

        return admin is not None

    async def register(self):
        if not await self.__class__.isAdmin(self.telegramId):
            await self.save()

    async def save(self):
        async with AsyncSessionLocal() as session:
            session.add(self)
            await session.commit()

        return self



