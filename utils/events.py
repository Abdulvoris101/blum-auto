import aiogram.exceptions

from apps.common.settings import settings
from utils import text as texts
from bot import bot, logger


async def sendEvent(text: str):
    await bot.send_message(settings.EVENT_CHANNEL_ID, text)


async def sendToUser(telegramId: int, text):
    try:
        await bot.send_message(telegramId, text)
    except aiogram.exceptions.TelegramForbiddenError as e:
        logger.error(str(e.message))
        await sendEvent(texts.BOT_BLOCKED.format(telegramId=telegramId))


async def sendError(text: str):
    await bot.send_message(settings.ERROR_CHANNEL_ID, text)