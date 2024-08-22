from aiogram import types
from aiogram.enums import ContentType
from aiogram.filters import Filter
from apps.admin.models import Admin
from apps.common.settings import settings


class IsAdmin(Filter):
    async def __call__(self, message: types.Message) -> bool:
        return await Admin.isAdmin(telegramId=message.from_user.id)


def checkPassword(password) -> bool:
    if password == settings.PASSWORD:
        return True
    return False
