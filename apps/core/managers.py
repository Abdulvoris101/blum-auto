from datetime import datetime
from typing import List

from sqlalchemy import exists, select
from aiogram import types

from apps.common.settings import settings
from apps.core.models import User
from apps.core.scheme import UserScheme, UserCreateScheme
from apps.payment.models import UserPayment
from apps.payment.scheme import UserPaymentCreateScheme
from db.setup import AsyncSessionLocal
from utils import text


class UserManager:
    @classmethod
    async def usersCount(cls) -> int:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).count())
            return result.scalar()

    @classmethod
    async def all(cls) -> List[User]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    @classmethod
    async def isExistsByUserId(cls, telegramId: int) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(exists().where(User.telegramId == telegramId)))
            return result.scalar()

    @classmethod
    async def updateUserLastVisit(cls, telegramId: int):
        async with AsyncSessionLocal() as session:
            user = await session.execute(select(User).filter(User.telegramId == telegramId))
            user = user.scalar_one_or_none()
            if user:
                user.lastUpdated = datetime.now()
                await session.commit()

    @classmethod
    async def register(cls, user: types.User) -> None:
        from utils.events import sendEvent

        userData = user.model_dump()
        scheme = UserCreateScheme(**userData)
        async with AsyncSessionLocal() as session:
            userObj = User(**scheme.model_dump())
            session.add(userObj)

            userPaymentScheme = UserPaymentCreateScheme(telegramId=userObj.telegramId, userId=userObj.id)
            userPayment = UserPayment(**userPaymentScheme.model_dump())
            session.add(userPayment)
            await session.commit()
            await sendEvent(text=text.USER_REGISTERED_EVENT_TEMPLATE.format(**userObj.to_dict()))

    @classmethod
    async def assignReferredBy(cls, telegramId: int, referredBy: str):
        async with AsyncSessionLocal() as session:
            user = await session.execute(select(User).filter(User.telegramId == telegramId))
            user = user.scalar_one_or_none()

            if user is None:
                return

            if referredBy is None:
                if user.referredBy is None:
                    user.referredBy = 'direct'
                    session.add(user)

            elif referredBy != str(telegramId):
                referredUser = await session.execute(
                    select(User).filter(User.telegramId == int(referredBy))
                )
                referredUser = referredUser.scalar_one_or_none()

                if not referredUser:
                    user.referredBy = 'direct'

                referredChatScheme = UserScheme(**referredUser.to_dict())

                if telegramId not in referredChatScheme.referralUsers:
                    user.referredBy = referredBy

            await session.commit()

    @classmethod
    async def addUserToReferrals(cls, userId: int, referralId: int):
        async with AsyncSessionLocal() as session:
            user = await session.execute(select(User).filter(User.telegramId == int(userId)))
            user = user.scalar_one_or_none()
            if user:
                userScheme = UserScheme(**user.to_dict())
                userScheme.referralUsers.append(referralId)
                user.referralUsers = userScheme.model_dump().get("referralUsers")
                await session.commit()

    @classmethod
    async def isActiveReferral(cls, userId: str, referralId: int) -> bool:
        try:
            userId = int(userId)
        except ValueError:
            return False

        if userId != 'direct':
            async with AsyncSessionLocal() as session:
                user = await session.execute(select(User).filter(User.telegramId == userId))
                user = user.scalar_one_or_none()

                if user:
                    userScheme = UserScheme(**user.to_dict())
                    if referralId not in userScheme.referralUsers:
                        return True
                    return False
        return False