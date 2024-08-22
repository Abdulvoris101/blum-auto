# tasks.py
import asyncio
from apps.accounts.managers import AccountManager
from apps.core.models import User
from apps.payment.managers import SubscriptionManager
from bot import logger, bot, i18n, _, __
from utils import text


async def reminderFarmingAvailable():
    await AccountManager.reminderAvailableFarmingAccounts()

    logger.info("reminder worked!")


async def cancelOrUpdateSubscriptions():
    await SubscriptionManager.cancelOrUpdateSubscriptions()
    logger.info("Canceled Expired Subscriptions!")


async def reminderNotUsingAccounts():
    accounts = await AccountManager.getNotUsingAccounts()

    for account in accounts:
        user = await User.getById(account.telegramId)
        i18n.ctx_locale.set(user.languageCode)
        with i18n.context():
            await bot.send_message(user.telegramId, text.ACCOUNT_AVAILABLE_TO_FARM
                                   .format(sessionName=account.sessionName))

    logger.info("reminder worked!")
