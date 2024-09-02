import aiogram.exceptions

from apps.common.settings import settings
from utils import text as texts
from bot import bot, logger


# Finance topic id - 4
# Users topic id - 6
# Accounts topic id - 2
# Bot errors topic id - 18

async def sendEvent(text: str, messageThreadId):
    await bot.send_message(settings.EVENT_CHANNEL_ID, text, message_thread_id=messageThreadId)


async def sendToUser(telegramId: int, text):
    try:
        await bot.send_message(telegramId, text)
    except aiogram.exceptions.TelegramForbiddenError as e:
        logger.error(str(e.message))
        await sendError(texts.BOT_BLOCKED.format(telegramId=telegramId))


async def sendError(text: str):
    await bot.send_message(settings.ERROR_CHANNEL_ID, text, message_thread_id=18)