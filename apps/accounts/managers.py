import asyncio
import datetime
import os
import urllib
from typing import Dict, List
from urllib.parse import urlparse

from pyrogram import Client
from pyrogram.errors import SessionExpired, Unauthorized
from pyrogram.errors.exceptions import unauthorized_401
from sqlalchemy import exists, select

from apps.accounts.models import Account, BlumAccount
from apps.accounts.scheme import AccountCreateScheme, Status, BlumAccountCreateScheme
from apps.common.settings import settings
from apps.core.models import User
from apps.payment.managers import SubscriptionManager
from apps.payment.models import AccountSubscription
from bot import bot, i18n, logger
from db.setup import AsyncSessionLocal
from utils import text
from utils.events import sendError


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
            account.userId = scheme.userId
            await account.save()

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
            if account.proxy:
                parsed_proxy = urlparse(account.proxy)
                proxy = {
                    "scheme": parsed_proxy.scheme,
                    "hostname": parsed_proxy.hostname,
                    "port": parsed_proxy.port,
                    "username": parsed_proxy.username,
                    "password": parsed_proxy.password
                }

            client = Client(name=account.sessionName, api_id=settings.API_ID, api_hash=settings.API_HASH,
                            workdir=settings.WORKDIR, proxy=proxy)
            await client.disconnect()
            await client.connect()
            await client.get_me()
            return True

        except (SessionExpired, AttributeError) as e:
            logger.error(text.SESSION_EXPIRED.format(e=e))
            return False
        except (unauthorized_401.AuthKeyInvalid, Unauthorized) as e:
            logger.error(text.SESSION_EXPIRED.format(e=e))
            return False
        except unauthorized_401.AuthKeyUnregistered as e:
            logger.error(text.SESSION_EXPIRED.format(e=e))
            account.status = Status.INACTIVE
            await account.save()

            filePath = os.path.join("sessions/", f"{account.sessionName}.session")
            fullPath = os.path.abspath(filePath)
            os.remove(fullPath)
            return False
        except ConnectionError as e:
            logger.error(f"Connection error: {e}")
            async with client:
                await client.get_me()
            return True

    @classmethod
    async def getValidAccounts(cls, user: User):
        validAccounts = []
        accounts = await cls.getUserAccounts(user.id)

        for account in accounts:
            try:
                proxy = None

                if account.proxy:
                    parsed_proxy = urlparse(account.proxy)
                    proxy = {
                        "scheme": parsed_proxy.scheme,
                        "hostname": parsed_proxy.hostname,
                        "port": parsed_proxy.port,
                        "username": parsed_proxy.username,
                        "password": parsed_proxy.password
                    }

                client = Client(name=account.sessionName, api_id=settings.API_ID, api_hash=settings.API_HASH,
                                workdir=settings.WORKDIR, proxy=proxy)
                if not await SubscriptionManager.isAccountSubscriptionActive(account.id):
                    await bot.send_message(text.NO_ACCOUNTS_TO_FARM.value)
                if await client.connect() and await SubscriptionManager.isAccountSubscriptionActive(account.id):
                    account.status = Status.ACTIVE
                    validAccounts.append(account)
                else:
                    account.status = Status.INACTIVE

                await account.save()
                await client.disconnect()

            except Exception as e:
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
                    account = blumDetail.account
                    duration = datetime.datetime.now() - account.lastUpdated

                    if duration >= datetime.timedelta(hours=blumDetail.farmingFreezeHours):
                        user = await User.getById(account.userId)
                        i18n.ctx_locale.set(user.languageCode)
                        with i18n.context():
                            await bot.send_message(user.telegramId,
                                                   text.ACCOUNT_AVAILABLE_TO_FARM.format(sessionName=account.sessionName))
                        blumDetail.farmingFreezeHours = 0
                        blumDetail.needRemind = False
                        await blumDetail.save()
                        await account.save()
                        await session.commit()

        except Exception as e:
            logger.error(str(e))
            await sendError(text.ERROR_TEMPLATE.format(message=f"Reminder user - {e}", telegramId=user.telegramId))

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

    def getSessionPath(self, sessionName: str):
        return os.path.join(self.storage_dir, f'{sessionName}.session')

    def sessionExists(self, sessionName: str):
        return os.path.exists(self.getSessionPath(sessionName))


sessionManager = SessionManager()
