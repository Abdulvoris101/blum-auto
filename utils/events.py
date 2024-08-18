from apps.common.settings import settings
from bot import bot


async def sendEvent(text: str):
    await bot.send_message(settings.EVENT_CHANNEL_ID, text)


async def sendToUser(telegramId: int, text):
    await bot.send_message(telegramId, text)


async def sendError(text: str):
    await bot.send_message(settings.ERROR_CHANNEL_ID, text)