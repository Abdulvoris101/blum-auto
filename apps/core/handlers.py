import asyncio
import random
from typing import List

from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.fsm.context import FSMContext

from apps.accounts.keyboards import accountsListMarkup
from apps.accounts.managers import AccountManager, UserTaskManager
from apps.accounts.models import Account
from apps.common.exceptions import AiogramException
from apps.common.settings import settings
from apps.core.keyboards import startMenuMarkup, languageMenuMarkup, helperMenuMarkup
from apps.core.managers import UserManager
from apps.core.models import User
from apps.core.scheme import UserScheme
from apps.payment.managers import SubscriptionManager
from apps.payment.models import UserPayment, AccountSubscription
from apps.scripts.blum.blum_bot import BlumBot
from apps.scripts.blum.main import BlumManager
from bot import bot, i18n
from db.states import AccountSelectionState, UserRegisterState
from utils import text, getProxies
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

coreRouter = Router(name="coreRouter")
taskManager = UserTaskManager()


@coreRouter.message(F.text == __("🌐 Tilni o'zgartirish"))
async def selectUserLanguage(message: types.Message, state: FSMContext):
    await state.set_state(UserRegisterState.language)
    return await message.answer(text.SELECT_LANGUAGE.value, reply_markup=languageMenuMarkup)


@coreRouter.message(CommandStart())
async def startWelcome(message: types.Message, command: CommandObject, state: FSMContext):
    await state.clear()
    referral = command.args

    if not await UserManager.isExistsByUserId(message.from_user.id):
        await UserManager.register(message.from_user)
        await UserManager.assignReferredBy(message.from_user.id, referral)

        if await UserManager.isValidReferral(message.from_user.id, referral):
            referral = int(referral)
            referralUser = await User.get(referral)
            userPayment = await UserPayment.getByUserId(referralUser.id)
            await UserManager.addUserToReferrals(referral, message.from_user.id)

            await bot.send_message(referralUser.telegramId,
                                   text.CONGRATS_GAVE_REQUESTS.format(referralPrice=settings.REFERRAL_PRICE))

            userPayment.balance += settings.REFERRAL_PRICE
            await userPayment.save()

        return await selectUserLanguage(message=message, state=state)

    return await message.answer(text.START_WELCOME.value, reply_markup=startMenuMarkup())


@coreRouter.message(UserRegisterState.language)
async def processChangingLanguage(message: types.Message, state: FSMContext):
    languageCodes = {"🇺🇿 O'zbekcha": "uz", "🇷🇺 Русский": "ru", "🇬🇧 English": "en"}
    languageCode = languageCodes.get(message.text, False)

    if not languageCode:
        return await message.answer(text.INCORRECT_LANGUAGE_CODE.value)

    user = await User.get(telegramId=message.from_user.id)
    user.languageCode = languageCode
    await user.save()

    i18n.ctx_locale.set(languageCode)
    await state.clear()
    await message.answer(text.START_WELCOME.value, reply_markup=startMenuMarkup())

    if not user.isGrantGiven:
        user.isGrantGiven = True
        await user.save()
        return await message.answer(text.THANKS_FOR_CHOOSING.value)


@coreRouter.message(F.text == __("⬅️ Bosh sahifa"))
async def backToHome(message: types.Message, state: FSMContext):
    return await startWelcome(message=message, command=CommandObject(), state=state)


@coreRouter.message(F.text == __("👾 Blum ishlash"))
async def processBlumHandler(message: types.Message, state: FSMContext):
    waitMomentMessage = await bot.send_message(message.from_user.id, text.WAIT_A_MOMENT.value)
    user = await User.get(message.from_user.id)
    accounts = await AccountManager.getUserAccounts(user.id)
    await bot.delete_message(message.from_user.id, waitMomentMessage.message_id)

    if not await AccountManager.isUserHasAccounts(user.id):
        await message.answer(text.NO_ACCOUNTS_TO_FARM.value)
        return await message.answer(text.INSTRUCTION_TO_GET_FREE_TG.value)

    await state.set_state(AccountSelectionState.accountName)
    await message.answer(text.SELECT_FARM_ACCOUNT.value,
                         reply_markup=accountsListMarkup(accounts))


@coreRouter.message(AccountSelectionState.accountName)
async def processFarming(message: types.Message, state: FSMContext):
    user = await User.get(message.from_user.id)

    await bot.send_message(message.from_user.id, text.WAIT_A_MOMENT.value, reply_markup=startMenuMarkup())

    if message.text == text.SELECT_ALL.value:
        accounts = await AccountManager.getValidAccounts(user)
    else:
        isSessionExists = await AccountManager.isExistsBySessionName(message.text)

        if not isSessionExists:
            await state.clear()
            await message.answer(text.WRONG_ACCOUNT.value)
            return await startWelcome(message=message, command=CommandObject(), state=state)

        account = await Account.getBySessionName(message.text)
        isAccountActive = await AccountManager.isActiveAccount(account)

        if not isAccountActive:
            return await message.answer(text.INACTIVE_SESSION.value)

        if not await SubscriptionManager.isAccountSubscriptionActive(accountId=account.id):
            return await message.answer(text.SUBSCRIPTION_INACTIVE.format(sessionName=account.sessionName))

        accounts = [account]

    await state.clear()
    task = asyncio.create_task(farmBlum(message, accounts))
    await taskManager.addTasks(message.from_user.id, [task])


async def farmBlum(message: types.Message, accounts: List[Account]):

    try:
        user = await User.get(message.from_user.id)
        tasks = [asyncio.create_task(BlumManager(account=account, user=user).starter()) for account
                 in accounts]
        await taskManager.addTasks(message.from_user.id, tasks)
        await asyncio.gather(*tasks)

    except asyncio.CancelledError:
        await message.answer(text.FARM_STOPPED.value)
        return

    except AiogramException as e:
        return await message.answer(e.message_text)


@coreRouter.message(F.text == "/help")
async def helpHandler(message: types.Message):
    await message.answer(text.HELP_COMMAND.value, reply_markup=helperMenuMarkup())


@coreRouter.message(F.text == __("🤔 Botni qanday ishlataman?"))
async def helpHandler(message: types.Message):
    await message.answer(text.BOT_USAGE_FAQ.value, disable_web_page_preview=True)


@coreRouter.message(F.text == __("🪄 Bot imkoniyatlari"))
async def helpHandler(message: types.Message):
    await message.answer(text.BOT_OPPORTUNITY.value, disable_web_page_preview=True)


@coreRouter.message(F.text == __("💸 Bot bilan qancha ishlashim mumkin?"))
async def helpHandler(message: types.Message):
    await message.answer(text.PRICE_BLUM.value, disable_web_page_preview=True)


@coreRouter.message(F.text == __("🎱 Kriptoni qayerdan olaman?"))
async def helpHandler(message: types.Message):
    await message.answer(text.CRYPTO_FAQ.value, disable_web_page_preview=True)


@coreRouter.message(F.text == __("🚫 Farmingni to'xtatish"))
async def stopBlumFarming(message: types.Message):
    isCanceledFarm = await taskManager.cancelTasks(message.from_user.id)
    if not isCanceledFarm:
        await message.answer(text.NO_ACTIVE_FARMS.value)


