import asyncio
import datetime
import os
import random
import urllib
from json import JSONDecodeError
from multiprocessing.managers import BaseManager
from typing import Dict, List, Tuple, Any
from urllib.parse import urlparse

import httpx
import pyrogram.errors.exceptions.unauthorized_401
from fake_useragent import UserAgent
from pyrogram import Client
from pyrogram.errors import SessionExpired, Unauthorized, AuthKeyUnregistered
from pyrogram.errors.exceptions import unauthorized_401
from sqlalchemy import exists, select, and_, Column, func

from apps.accounts.models import Account, BlumAccount, Proxy
from apps.accounts.scheme import AccountCreateScheme, Status, BlumAccountCreateScheme, ProxyDetailScheme
from apps.common.exceptions import InvalidRequestException
from apps.common.settings import settings
from apps.core.models import User
from apps.accounts.scheme import ProxyResponseScheme, ProxyCreateScheme
from apps.core.scheme import BlumBalanceScheme
from apps.payment.managers import SubscriptionManager
from apps.payment.models import AccountSubscription
from apps.scripts.blum.blum_bot import BlumBot
from bot import bot, i18n, logger
from db.setup import AsyncSessionLocal
from utils import text
from utils.events import sendError, sendToUser
from asyncio import Lock

dbLock = Lock()

class AccountManager:
    def __init__(self):
        pass

    @classmethod
    async def isExistsByUserId(cls, userId: int) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(exists().where(Account.userId == userId)))
            return result.scalar()

    @classmethod
    async def isExistsByPhoneNumber(cls, phoneNumber: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(exists().where(Account.phoneNumber == phoneNumber)))
            return result.scalar()

    @classmethod
    async def isExistsBySessionName(cls, sessionName: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(exists().where(Account.sessionName == sessionName)))
            return result.scalar()

    @classmethod
    async def getUserAccountsCount(cls, userId: int):
        async with AsyncSessionLocal() as session:
            accountsCount = 0
            result = await session.execute(select(Account).filter_by(userId=userId))
            accounts = result.scalars().all()

            for account in accounts:
                if sessionManager.sessionExists(account.sessionName):
                    accountsCount += 1

            return accountsCount

    @classmethod
    async def isUserHasAccounts(cls, userId: int) -> bool:
        if await cls.getUserAccountsCount(userId) < 1:
            return False
        return True

    @classmethod
    async def createOrActivate(cls, scheme: AccountCreateScheme) -> Account:
        isAccount = await cls.isExistsByPhoneNumber(scheme.phoneNumber)

        if isAccount:
            account = await Account.getByPhoneNumber(scheme.phoneNumber)
            account.status = Status.ACTIVE
            account.telegramId = scheme.telegramId
            await account.save()

            # Set account's proxy inUse to true
            await ProxyManager.activateProxyInUse(account.proxyId)
            return account

        account = Account(**scheme.model_dump())
        await account.save()

        return account

    @classmethod
    async def getUserAccounts(cls, userId):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Account).filter_by(userId=userId))
            accounts = result.scalars().all()
        return accounts

    @classmethod
    async def getActiveAccounts(cls, telegramId: int):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Account).filter_by(telegramId=telegramId, status=Status.ACTIVE))
            accounts = result.scalars().all()
        return accounts

    @classmethod
    async def getAccountCreateScheme(cls, user, phoneNumber, sessionName, accountInfo, proxyId):
        # Assign none if account exists bcs account has already proxy assigned

        return AccountCreateScheme(
            sessionName=sessionName, phoneNumber=phoneNumber,
            userId=user.id, telegramId=accountInfo.id, proxyId=proxyId
        )

    @classmethod
    async def isActiveAccount(cls, account: Account):
        if account is None:
            logger.error(text.ACCOUNT_NOT_FOUND)
            return False

        if not sessionManager.sessionExists(account.sessionName):
            account.status = Status.INACTIVE
            await account.save()
            logger.error(text.SESSION_FILE_NOT_EXISTS)
            return False

        try:
            proxy = None

            if account.proxyId is not None:
                proxy = await Proxy.get(account.proxyId)
                proxy = {
                    "scheme": proxy.type,
                    "hostname": proxy.host,
                    "port": proxy.port,
                    "username": proxy.user,
                    "password": proxy.password
                }

            async with dbLock:
                client = Client(name=account.sessionName, api_id=settings.API_ID, api_hash=settings.API_HASH,
                                workdir=settings.WORKDIR, proxy=proxy)
                await client.connect()
                await client.get_me()
                await client.disconnect()

            return True

        except (SessionExpired) as e:
            logger.error(text.SESSION_EXPIRED.format(e=e))
            return False
        except (unauthorized_401.AuthKeyInvalid, Unauthorized) as e:
            logger.error(text.SESSION_EXPIRED.format(e=e))
            return False
        except (unauthorized_401.AuthKeyUnregistered, AuthKeyUnregistered) as e:
            logger.error(text.SESSION_EXPIRED.format(e=e))
            account.status = Status.INACTIVE
            await account.save()

            filePath = os.path.join("sessions/", f"{account.sessionName}.session")
            fullPath = os.path.abspath(filePath)
            os.remove(fullPath)
            return False
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return False

    @classmethod
    async def getValidAccounts(cls, user: User):
        validAccounts = []
        accounts = await cls.getUserAccounts(user.id)

        for account in accounts:
            try:
                proxy = None

                if account.proxyId is not None:
                    proxy = await Proxy.get(account.proxyId)
                    proxy = {
                        "scheme": proxy.type,
                        "hostname": proxy.host,
                        "port": proxy.port,
                        "username": proxy.user,
                        "password": proxy.password
                    }

                async with dbLock:
                    client = Client(name=account.sessionName, api_id=settings.API_ID, api_hash=settings.API_HASH,
                                    workdir=settings.WORKDIR, proxy=proxy)

                    if not await SubscriptionManager.isAccountSubscriptionActive(account.id):
                        await bot.send_message(user.telegramId, text.SUBSCRIPTION_INACTIVE.format(sessionName=account.sessionName))

                    if await client.connect() and await SubscriptionManager.isAccountSubscriptionActive(account.id):
                        await client.get_me()
                        account.status = Status.ACTIVE
                        validAccounts.append(account)
                    else:
                        account.status = Status.INACTIVE

                    await client.disconnect()
                await account.save()

            except pyrogram.errors.exceptions.unauthorized_401.SessionRevoked as e:
                logger.error("Session revoked")
                await bot.send_message(user.telegramId, text.SESSION_ENDED.format(sessionName=account.sessionName))
                continue
            except Exception as e:
                logger.error(e)
                await bot.send_message(user.telegramId, text.SESSION_ENDED.format(sessionName=account.sessionName))
                continue

        return validAccounts

    @classmethod
    async def reminderAvailableFarmingAccounts(cls):
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(BlumAccount).filter(
                    BlumAccount.farmingFreezeHours > 0, BlumAccount.needRemind == True))
                blumDetails = result.scalars().all()

                for blumDetail in blumDetails:
                    accountId = blumDetail.accountId
                    account = await Account.get(accountId)
                    user = await User.getById(account.userId)
                    duration = datetime.datetime.now() - account.lastUpdated

                    if duration >= datetime.timedelta(hours=blumDetail.farmingFreezeHours):
                        user = await User.get(user.telegramId)
                        i18n.ctx_locale.set(user.languageCode)
                        with i18n.context():
                            await sendToUser(user.telegramId, text.ACCOUNT_AVAILABLE_TO_FARM.format(
                                sessionName=account.sessionName))
                        blumDetail.farmingFreezeHours = 0
                        blumDetail.needRemind = False

                        session.add(blumDetail)
                        session.add(account)

                        await session.commit()

        except Exception as e:
            logger.error(str(e))
            await sendError(text.ERROR_TEMPLATE.format(message=f"Reminder user - {e}", telegramId="no"))

    @classmethod
    async def getNotUsingAccounts(cls):
        async with AsyncSessionLocal() as session:
            oneDayAgo = datetime.datetime.now() - datetime.timedelta(days=1)
            result = await session.execute(select(Account).filter(Account.lastUpdated < oneDayAgo,
                                                                  Account.status == Status.ACTIVE))
            accounts = result.scalars().all()

        return accounts


class BlumAccountManager:

    @classmethod
    async def isExistsByAccountId(cls, accountId: int) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(exists().where(BlumAccount.accountId == accountId)))
            return result.scalar()

    @classmethod
    async def createOrActivate(cls, scheme: BlumAccountCreateScheme) -> Account:
        isBlumAccount = await cls.isExistsByAccountId(scheme.accountId)

        if isBlumAccount:
            blumAccount = await BlumAccount.getByAccountId(scheme.accountId)
            blumAccount.status = Status.ACTIVE
            await blumAccount.save()
            return blumAccount

        account = BlumAccount(**scheme.model_dump())
        await account.save()
        return account

    @classmethod
    async def getUserBlumBalance(cls, telegramId: int, sessionName: str, proxy, trigger: bool) -> BlumBalanceScheme:
        retries = 0
        maxRetries = 3

        while retries < maxRetries:
            try:
                blum = BlumBot(sessionName=sessionName, proxy=proxy)
                await blum.initWebSession()
                await blum.login()
                return await blum.balance()
            except InvalidRequestException as e:
                if trigger:
                    raise InvalidRequestException(e.messageText, e.exceptionText)

                logger.error(e)
                await bot.send_message(telegramId, e.messageText)
                return BlumBalanceScheme(availableBalance=0.0, playPasses=0, timestamp=datetime.datetime.now().timestamp())
            except JSONDecodeError as e:
                if trigger:
                    raise InvalidRequestException(text.CANT_GET_BLUM_BALANCE.value)

                logger.error(e)
                await bot.send_message(telegramId, text.CANT_GET_BLUM_BALANCE.value)
                return BlumBalanceScheme(availableBalance=0.0, playPasses=0, timestamp=datetime.datetime.now().timestamp())

            except httpx.TimeoutException as e:
                logger.error(f"Attempt {retries + 1}/{maxRetries} failed: {e}")
                retries += 1

                await bot.send_message(telegramId, text.CONNECTION_TIMEOUT.format(retries=retries))

                if retries >= 3:
                    if trigger:
                        raise InvalidRequestException(text.CANT_GET_BLUM_BALANCE.value)
                    return BlumBalanceScheme(availableBalance=0.0, playPasses=0, timestamp=datetime.datetime.now().timestamp())


class ProxyManager:
    apiKey = settings.PROXY_KEY
    baseUrl = settings.PROXY_BASE_URL

    @classmethod
    async def isExistsByHostAndPort(cls, host: str, port: int) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(exists().where((Proxy.host == host) & (Proxy.port == port)))
            )
            return result.scalar()

    @classmethod
    def getProxies(cls):
        proxies = []

        with open("apps/common/src/proxies.txt", 'r') as file:
            for line in file:
                proxies.append(line.strip())

        return proxies

    @classmethod
    async def isExistsBySessionName(cls, sessionName: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(exists().where(Account.sessionName == sessionName)))
            return result.scalar()

    @classmethod
    async def isExistsByProxyHostAndPort(cls, host: str, port: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(exists().where(and_(Proxy.host == host, Proxy.port == port)))
            )
            return result.scalar()

    @classmethod
    async def createByJson(cls, telegramId: int, response: dict) -> Proxy:
        proxyResponse = ProxyResponseScheme(**response)
        firstKey = next(iter(proxyResponse.list))
        proxyDetail = proxyResponse.list[firstKey]
        proxyDetail.port = int(proxyDetail.port)
        proxyDetail.type = 'socks5' if proxyDetail.type == 'socks' else 'http'
        proxyCreateScheme = ProxyCreateScheme(telegramId=telegramId, phoneCode=48, **proxyDetail.model_dump())

        proxy = Proxy(**proxyCreateScheme.model_dump())
        await proxy.save()

        return proxy

    @classmethod
    async def buyProxy(cls, telegramId: int) -> dict:
        url = f"{cls.baseUrl}/{cls.apiKey}/buy?count=1&period=30&version=4&type=socks&descr={telegramId}&country=pl"

        headers = {'User-Agent': UserAgent(os='android').random}
        webSession = httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(timeout=60))

        response = await webSession.post(url)
        responseJson = response.json()

        return responseJson

    @classmethod
    async def buyAndCreateProxy(cls, user: User) -> int | None:
        response = await ProxyManager.buyProxy(telegramId=user.telegramId)

        if response.get("status") == "yes":
            proxy_obj = await ProxyManager.createByJson(telegramId=user.telegramId, response=response)
            return proxy_obj.id

        await sendError(text.PROXY_BUY_ERROR.format(
            error=response.get("error"),
            errorCode=response.get("error_id")
        ))

        return None

    @classmethod
    async def changeOwnerOfProxy(cls, proxyId: int, user: User) -> int:
        proxy = await Proxy.get(proxyId)
        proxy.telegramId = user.telegramId
        proxy.inUse = True
        await proxy.save()
        return proxy.id

    @classmethod
    async def activateProxyInUse(cls, proxyId: int) -> int:
        proxy = await Proxy.get(proxyId)
        if proxy is not None:
            proxy.inUse = True
            await proxy.save()
            return proxy.id

    @classmethod
    async def getOrCreateProxy(cls, user) -> int:
        availableProxy = await ProxyManager.getNotUsingProxy()

        if availableProxy:
            return await cls.changeOwnerOfProxy(availableProxy.id, user)

        return await cls.buyAndCreateProxy(user)

    @classmethod
    async def getNotUsingProxy(cls) -> Proxy:
        async with AsyncSessionLocal() as session:
            query = select(Proxy).where((Proxy.inUse == False) & (Proxy.isCommon == False)).limit(1)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def getRandomProxy(cls) -> ProxyDetailScheme:
        proxies = ProxyManager.getProxies()
        proxy = random.choice(proxies)
        proxy_parsed = urlparse(proxy)

        return ProxyDetailScheme(
            id=None, telegramId=None, ip=None, proxyId=None, dateEnd=None,
            host=proxy_parsed.hostname, port=str(proxy_parsed.port),
            user=proxy_parsed.username, password=proxy_parsed.password, type=proxy_parsed.scheme
        )

    @classmethod
    async def getGhostProxyByPhoneCode(cls, phoneCode: int) -> ProxyDetailScheme:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Proxy).where((Proxy.phoneCode == phoneCode) & (Proxy.isCommon == True))
            )

            proxies = result.scalars().all()

            if proxies:
                randomProxy = random.choice(proxies)
                return ProxyDetailScheme(**randomProxy.to_dict())

            randomResult = await session.execute(
                select(Proxy).where(Proxy.isCommon == True).order_by(func.random()).limit(1)
            )
            randomProxy = randomResult.scalar_one_or_none()
            return ProxyDetailScheme(**randomProxy.to_dict())


class UserTaskManager:
    def __init__(self):
        self.userTasks: Dict[int, List[asyncio.Task]] = {}
        self.lock = asyncio.Lock()

    async def addTasks(self, userId: int, newTasks: List[asyncio.Task]):
        async with self.lock:
            if userId not in self.userTasks:
                self.userTasks[userId] = []
            self.userTasks[userId].extend(newTasks)

    async def cancelTasks(self, userId: int) -> bool:
        async with self.lock:
            if userId in self.userTasks:
                tasks = self.userTasks[userId]
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                del self.userTasks[userId]
                return True
            return False


class SessionManager:
    def __init__(self):
        self.storage_dir = "sessions"
        os.makedirs(self.storage_dir, exist_ok=True)

        self._sessions = {}
        self._lock = asyncio.Lock()


    def getSessionPath(self, sessionName: str):
        return os.path.join(self.storage_dir, f'{sessionName}.session')

    def sessionExists(self, sessionName: str):
        return os.path.exists(self.getSessionPath(sessionName))

    async def setSession(self, userId: int, session: Client):
        async with self._lock:
            self._sessions[userId] = session

    async def getSession(self, userId: int) -> Client:
        async with self._lock:
            return self._sessions.get(userId)

    async def deleteSession(self, userId: int):
        async with self._lock:
            if userId in self._sessions:
                del self._sessions[userId]


sessionManager = SessionManager()
