from aiogram import BaseMiddleware

from typing import Dict, Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Update, Message
from aiogram.utils.i18n.middleware import I18nMiddleware

from apps.core.managers import UserManager
from apps.core.models import User
from utils import text


class DynamicI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: Update, data: Dict[str, Any]) -> str:
        user = event.event.from_user

        if user is not None:
            user = await User.get(user.id)

            if user is not None:
                return user.languageCode

            return 'uz'

        return 'uz'


class MessageMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        from bot import bot, _

        data["chat"] = event.chat
        data["user"] = event.from_user

        bypass_commands = ["/start", "/set_language", _("🌐 Tilni o'zgartirish")]

        if not event.text in bypass_commands and not event.text.startswith("/start"):
            if not await User.isExistsByUserId(event.from_user.id):
                return await bot.send_message(event.from_user.id, text.NOT_REGISTERED.value)

        return await handler(event, data)
