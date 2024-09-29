from sqlalchemy import Column, JSON, Integer, desc, String, Enum, Boolean, Text, BigInteger, DateTime, ForeignKey, \
    select, Float
from db.setup import Base, AsyncSessionLocal
from sqlalchemy.orm import relationship, class_mapper


class Proxy(Base):
    __tablename__ = 'proxy'
    id = Column(Integer, primary_key=True)
    telegramId = Column(BigInteger, nullable=True)
    proxyId = Column(String, nullable=True)
    ip = Column(String, nullable=True)
    host = Column(String)
    port = Column(Integer)
    user = Column(String)
    password = Column(String)
    type = Column(String)
    date = Column(String)
    inUse = Column(Boolean, default=True)
    isCommon = Column(Boolean, default=False)
    isCanceled = Column(Boolean, default=False)
    phoneCode = Column(Integer, nullable=True)
    dateEnd = Column(String, nullable=True)

    def __init__(self, telegramId, proxyId,
                 ip, host, port, user, password, type, inUse, date, isCommon, phoneCode, isCanceled, dateEnd):
        self.telegramId = telegramId
        self.proxyId = proxyId
        self.ip = ip
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.type = type
        self.date = date
        self.inUse = inUse
        self.dateEnd = dateEnd
        self.isCommon = isCommon
        self.phoneCode = phoneCode
        self.isCanceled = isCanceled
        super().__init__()

    async def save(self):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                session.add(self)

        return self

    @classmethod
    async def get(cls, proxyId: int):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Proxy).filter_by(id=proxyId))
            user = result.scalar_one_or_none()
            return user

    @classmethod
    async def update(cls, instance, column, value):
        setattr(instance, column, value)
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await session.commit()

    def to_dict(self):
        """Converts SQL Alchemy model instance to dictionary."""
        return {c.key: getattr(self, c.key) for c in class_mapper(self.__class__).mapped_table.c}


class Account(Base):
    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)
    telegramId = Column(BigInteger, unique=True)
    phoneNumber = Column(String, unique=True)
    userId = Column(Integer)
    sessionName = Column(String)
    status = Column(String)
    proxyId = Column(BigInteger, nullable=True)
    createdAt = Column(DateTime, nullable=True)
    lastUpdated = Column(DateTime, nullable=True)
    isOver = Column(Boolean, nullable=True)

    def __init__(self, telegramId, userId, sessionName,
                 phoneNumber, status, proxyId, isOver, createdAt):
        self.userId = userId
        self.telegramId = telegramId
        self.sessionName = sessionName
        self.phoneNumber = phoneNumber
        self.createdAt = createdAt
        self.lastUpdated = createdAt
        self.status = status
        self.proxyId = proxyId
        self.isOver = isOver

        super().__init__()

    async def save(self):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                session.add(self)

        return self

    @classmethod
    async def get(cls, accountId):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Account).filter_by(id=accountId))
            user = result.scalar_one_or_none()
            return user

    @classmethod
    async def getByPhoneNumber(cls, phoneNumber):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Account).filter_by(phoneNumber=phoneNumber))
            account = result.scalar_one_or_none()
        return account

    @classmethod
    async def getBySessionName(cls, sessionName):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Account).filter_by(sessionName=sessionName))
            account = result.scalar_one_or_none()
        return account

    @classmethod
    async def update(cls, instance, column, value):
        setattr(instance, column, value)
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await session.commit()

    @classmethod
    async def delete(cls, accountId):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Account).filter_by(id=accountId))
            account = result.scalar_one_or_none()
            if account:
                session.delete(account)

    def to_dict(self):
        """Converts SQL Alchemy model instance to dictionary."""
        return {c.key: getattr(self, c.key) for c in class_mapper(self.__class__).mapped_table.c}


class BlumAccount(Base):
    __tablename__ = 'blum_account'

    id = Column(Integer, primary_key=True)
    accountId = Column(Integer)
    availablePlayPasses = Column(Integer)
    allPlayPasses = Column(Integer)
    availableBalance = Column(Float)
    farmingFreezeHours = Column(Integer)
    needRemind = Column(Boolean, default=True)
    playedGames = Column(Integer, nullable=True)
    earnedBlumCoins = Column(BigInteger, nullable=True)
    status = Column(String)

    def __init__(self, accountId: int, availableBalance: float, availablePlayPasses: int,
                 farmingFreezeHours: int, needRemind: bool,
                 allPlayPasses: int, playedGames: int, status: str, earnedBlumCoins: int):
        self.accountId = accountId
        self.availablePlayPasses = availablePlayPasses
        self.availableBalance = availableBalance
        self.allPlayPasses = allPlayPasses
        self.needRemind = needRemind
        self.status = status
        self.farmingFreezeHours = farmingFreezeHours
        self.playedGames = playedGames
        self.earnedBlumCoins = earnedBlumCoins

        super().__init__()

    async def save(self):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                session.add(self)

            return self

    @classmethod
    async def get(cls, id):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(BlumAccount).filter_by(id=id))
            blumDetails = result.scalar_one_or_none()

        return blumDetails

    @classmethod
    async def getByAccountId(cls, accountId):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(BlumAccount).filter_by(accountId=accountId))
            blumDetails = result.scalar_one_or_none()
        return blumDetails

    @classmethod
    async def createOrGetByAccountId(cls, accountId):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(BlumAccount).filter_by(accountId=accountId))
            blumAccount = result.scalar_one_or_none()

            if blumAccount is None:
                blumAccount = BlumAccount(accountId=accountId, availableBalance=0.0, availablePlayPasses=0,
                                          farmingFreezeHours=8, needRemind=True, allPlayPasses=0, status="INACTIVE",
                                          playedGames=0, earnedBlumCoins=0)
                await blumAccount.save()

            return blumAccount

    @classmethod
    async def update(cls, instance, column, value):
        setattr(instance, column, value)
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await session.commit()

    @classmethod
    async def delete(cls, id):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(BlumAccount).filter_by(id=id))
            blumDetails = result.scalar_one_or_none()
            if blumDetails:
                session.delete(blumDetails)

    def to_dict(self):
        """Converts SQL Alchemy model instance to dictionary."""
        return {c.key: getattr(self, c.key) for c in class_mapper(self.__class__).mapped_table.c}
