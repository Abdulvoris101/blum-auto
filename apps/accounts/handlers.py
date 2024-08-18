import random
from urllib.parse import urlparse

from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from pydantic import ValidationError
from pyrogram.errors import BadRequest, SessionPasswordNeeded
from apps.accounts.keyboards import accountsMarkup, AccountCallback, changeAccountMarkup
from apps.accounts.managers import AccountManager, BlumAccountManager
from apps.accounts.models import Account, BlumAccount
from apps.accounts.scheme import AccountCreateScheme, AccountScheme, Status, BlumAccountScheme, BlumAccountCreateScheme
from apps.common.exceptions import InvalidRequestException, InternalServerException
from apps.common.settings import settings
from apps.core.keyboards import backMenuMarkup, startMenuMarkup, cancelMenuMarkup
from apps.core.models import User
from apps.payment.managers import SubscriptionManager
from apps.payment.models import UserPayment
from apps.scripts.blum.blum_bot import BlumBot
from bot import bot, logger
from db.states import AddAccountState, AvailablePlayPassState
from utils import text, getProxies
from aiogram.fsm.context import FSMContext
from pyrogram import Client
from pyrogram.errors.exceptions import bad_request_400, not_acceptable_406, flood_420

from utils.events import sendEvent
from utils.validator import validatePhoneNumber
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

accountsRouter = Router(name="accountsRouter")


@accountsRouter.message(F.text == __("❌ Bekor qilish"))
async def cancelHandler(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(text.CANCELED.value, reply_markup=startMenuMarkup())


@accountsRouter.message(F.text == __("👥 Akkauntlar"))
async def accountsHandler(message: types.Message):
    user = await User.get(message.from_user.id)
    accounts = await AccountManager.getUserAccounts(user.id)

    return await message.answer(text.ACCOUNTS_TEXT.format(accountsCount=len(accounts)),
                                reply_markup=await accountsMarkup(accounts))


@accountsRouter.callback_query(AccountCallback.filter(F.name == "account_details"))
async def accountsDetails(callback: types.CallbackQuery, callback_data: AccountCallback):
    account = await Account.get(callback_data.accountId)
    blumDetails = await BlumAccount.createOrGetByAccountId(account.id)

    try:
        waitMomentMessage = await bot.send_message(callback.from_user.id, text.WAIT_A_MOMENT.value)
        isActiveAccount = await AccountManager.isActiveAccount(account)

        if not isActiveAccount:
            account.status = Status.INACTIVE
            await account.save()
            await bot.delete_message(callback.from_user.id, message_id=waitMomentMessage.message_id)
            return await bot.send_message(callback.from_user.id, text.INACTIVE_SESSION.value)

        blum = BlumBot(sessionName=account.sessionName, proxy=account.proxy)
        await blum.initWebSession()
        await blum.login()
        balance = await blum.balance()

        blumDetails.availableBalance = balance.availableBalance
        blumDetails.allPlayPasses = balance.allPlayPasses
        blumDetails.status = Status.ACTIVE
        account.status = Status.ACTIVE

        await blumDetails.save()
        await account.save()

        await bot.delete_message(callback.from_user.id, message_id=waitMomentMessage.message_id)
        accountScheme = AccountScheme(**account.to_dict())
        blumAccountScheme = BlumAccountScheme(**blumDetails.to_dict())
        PROFILE_INFO = text.PROFILE_INFO.value + text.BOT_COULD_PLAY.value
        await bot.send_message(callback.from_user.id,
                               PROFILE_INFO.format(**blumAccountScheme.model_dump(),
                                                   sessionName=accountScheme.sessionName),
                               reply_markup=changeAccountMarkup(accountScheme.id))
    except TelegramBadRequest as e:
        logger.error(f"Tg bad request: {e}")
        logger.error(text.BAD_REQUEST.format(errorMessage=e.message, userId=account.sessionName))
    except ValidationError as e:
        logger.error(f"Validation error: {e.messageText}")
        await bot.send_message(callback.from_user.id, text.BLUM_ERROR.value)
    except InvalidRequestException as e:
        logger.error(f"Invalid request: {e.messageText}")
        await bot.send_message(callback.from_user.id, e.messageText)
    except Exception as e:
        print(e)
        logger.error(e)
        await bot.send_message(callback.from_user.id,
                               text.SOMETHING_WRONG_ON_BLUM.format(sessionName=account.sessionName))


@accountsRouter.callback_query(F.data == "add_account")
async def addAccount(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("")
    userPayment = await UserPayment.get(callback.from_user.id)

    if userPayment.balance < settings.PRICE and userPayment.trialBalance < settings.PRICE:
        return await bot.send_message(callback.from_user.id, text.NOT_ENOUGH_BALANCE.format(price=settings.PRICE))

    await state.set_state(AddAccountState.phoneNumber)
    await bot.send_message(callback.from_user.id, text.DISCLAIMER_OF_ADDING_ACCOUNT.value)
    await bot.send_message(callback.from_user.id, text.ENTER_PHONE_NUMBER.value, reply_markup=cancelMenuMarkup())


@accountsRouter.message(AddAccountState.phoneNumber)
async def processPhoneNumber(message: types.Message, state: FSMContext):
    phoneNumber = message.text
    sessionName = phoneNumber
    waitMomentMessage = await bot.send_message(message.from_user.id, text.WAIT_A_MOMENT.value)

    if await AccountManager.isExistsBySessionName(sessionName):
        account = await Account.getBySessionName(sessionName)
        if await AccountManager.isActiveAccount(account):
            await bot.delete_message(message.from_user.id, message_id=waitMomentMessage.message_id)
            return await message.answer(text.ALREADY_ADDED.value, reply_markup=startMenuMarkup())

    try:
        global sessions
        sessions = {}

        await validatePhoneNumber(phoneNumber)

        proxies = getProxies()
        proxy = random.choice(proxies)
        proxyParsed = urlparse(proxy)

        proxy = {
            "scheme": proxyParsed.scheme,
            "hostname": proxyParsed.hostname,
            "port": proxyParsed.port,
            "username": proxyParsed.username,
            "password": proxyParsed.password
        }

        session = Client(name=sessionName, api_id=settings.API_ID, api_hash=settings.API_HASH,
                         workdir=settings.WORKDIR, proxy=proxy)
        await bot.delete_message(message.from_user.id, message_id=waitMomentMessage.message_id)
        inWaitMessage = await message.answer(text.SMS_SENDING.value)
        await session.connect()
        sentCode = await session.send_code(phoneNumber)
        sessions[message.from_user.id] = session
        await state.update_data(sentCode=sentCode.phone_code_hash)

    except InvalidRequestException as e:
        logger.error(e.messageText)
        return await message.answer(e.messageText)
    except bad_request_400.ApiIdInvalid as e:
        logger.error(e.MESSAGE)
        return await message.answer(text.INVALID_PHONE_NUMBER.value)
    except not_acceptable_406.PhoneNumberInvalid as e:
        logger.error(e.MESSAGE)
        return await message.answer(text.INVALID_PHONE_NUMBER.value)
    except flood_420.FloodWait as e:
        logger.error(e.MESSAGE)
        return await message.answer(text.TOO_MANY_REQUESTS.value)

    await state.update_data(sessionName=sessionName)
    await state.update_data(phoneNumber=phoneNumber)
    await state.set_state(AddAccountState.verificationCode)
    await bot.delete_message(message.from_user.id, inWaitMessage.message_id)
    await message.answer(text.ENTER_VERIFICATION_CODE.value)


async def processAccountMessage(message: types.Message, state: FSMContext, session: Client):
    data = await state.get_data()
    phoneNumber = data.get('phoneNumber')
    sessionName = data.get("sessionName")

    try:
        proxies = getProxies()
        proxy = random.choice(proxies)

        blum = BlumBot(sessionName=sessionName, proxy=proxy)
        await blum.initWebSession()
        await blum.login()
        balance = await blum.balance()
        accountInfo = await session.get_me()

        user = await User.get(message.from_user.id)
        accountScheme = AccountCreateScheme(sessionName=sessionName, phoneNumber=phoneNumber, userId=user.id,
                                            telegramId=accountInfo.id)

        account = await AccountManager.createOrActivate(accountScheme)
        blumAccountScheme = BlumAccountCreateScheme(accountId=account.id, **balance.model_dump())

        await BlumAccountManager.createOrActivate(scheme=blumAccountScheme)
        await sendEvent(text.ACCOUNT_REGISTERED.format(userTelegramId=user.telegramId, accountTelegramId=accountInfo.id,
                                                       status=accountScheme.status, sessionName=accountScheme.sessionName))

        await session.disconnect()
        await state.clear()
        del sessions[message.from_user.id]

        userPayment = await UserPayment.get(message.from_user.id)

        if userPayment.balance >= settings.PRICE:
            await SubscriptionManager.subscribe(message.from_user.id, accountId=account.id, isFreeTrial=False)
            userPayment.balance -= settings.PRICE
        else:
            await SubscriptionManager.subscribe(message.from_user.id, accountId=account.id, isFreeTrial=True)
            userPayment.trialBalance -= settings.PRICE

        await userPayment.save()
        await user.save()
        await message.answer(text.PROFILE_INFO.format(**blumAccountScheme.model_dump(),
                                                      sessionName=accountScheme.sessionName))
        await message.answer(text.SUCCESSFUL_ADDED_ACCOUNT.value, reply_markup=startMenuMarkup())

    except bad_request_400.PhoneCodeExpired as e:
        logger.error(e.MESSAGE)
        return await message.answer(text.EXPIRED_CODE.value)
    except bad_request_400.PhoneCodeInvalid as e:
        logger.error(e.MESSAGE)
        return await message.answer(text.INVALID_VERIFICATION_CODE.value)
    except AttributeError as e:
        logger.error(str(e))
        await state.clear()
        return await message.answer(text.SOMETHING_WRONG.value)
    except ConnectionError as e:
        logger.error(str(e))
        await state.clear()
        return await message.answer(text.SOMETHING_WRONG.value)
    except InvalidRequestException as e:
        logger.error(e.messageText)
        await state.clear()
        return await message.answer(e.messageText, reply_markup=startMenuMarkup())
    except InternalServerException as e:
        logger.warn(str(e.message_text))
        return await message.answer(e.message_text)


@accountsRouter.message(AddAccountState.verificationCode)
async def processVerificationCode(message: types.Message, state: FSMContext):
    data = await state.get_data()
    verificationCode = message.text

    try:
        phoneNumber = data.get('phoneNumber')
        sentCode = data.get("sentCode")
        waitMomentMessage = await bot.send_message(message.from_user.id, text.WAIT_A_MOMENT.value)
        session = sessions.get(message.from_user.id)
        await session.sign_in(phoneNumber, sentCode, verificationCode)
        await bot.delete_message(message.from_user.id, message_id=waitMomentMessage.message_id)
    except SessionPasswordNeeded:
        await state.set_state(AddAccountState.password)
        return await message.answer(text.ENTER_PASSWORD.value)
    except bad_request_400.PhoneCodeExpired as e:
        logger.warn(str(e))
        await message.answer(text.EXPIRED_VERIFICATION_CODE.value)
        return await message.answer(text.TELEGRAM_NOT_LET.value)
    except BadRequest as e:
        logger.warn(str(e))
        return await message.answer(text.INVALID_VERIFICATION_CODE.value)

    await processAccountMessage(message, state, session)


@accountsRouter.message(AddAccountState.password)
async def processPassword(message: types.Message, state: FSMContext):
    try:
        waitMomentMessage = await bot.send_message(message.from_user.id, text.WAIT_A_MOMENT.value)
        session = sessions.get(message.from_user.id)
        await session.check_password(message.text)
    except (bad_request_400.PasswordHashInvalid, bad_request_400.PasswordEmpty, bad_request_400.PasswordRequired) as e:
        logger.warn(str(e))
        return await message.answer(text.WRONG_PASSWORD.value)
    except BadRequest as e:
        logger.warn(str(e))
        return await message.answer(text.CAN_NOT_CONNECT_TO_TELEGRAM.value)

    await bot.delete_message(message.from_user.id, message_id=waitMomentMessage.message_id)
    await processAccountMessage(message, state, session)


@accountsRouter.callback_query(AccountCallback.filter(F.name == "play_pass_change"))
async def processPlayPasses(callback: types.CallbackQuery, callback_data: AccountCallback, state: FSMContext):
    await callback.answer("")
    account = await Account.get(callback_data.accountId)
    await state.set_state(AvailablePlayPassState.availablePlayPass)
    await state.update_data(accountId=account.id)
    await bot.send_message(callback.from_user.id,
                           text.ENTER_PLAY_PASSES.format(allPlayPasses=account.allPlayPasses),
                           reply_markup=backMenuMarkup())


@accountsRouter.message(AvailablePlayPassState.availablePlayPass)
async def changeAvailablePlayPass(message: types.Message, state: FSMContext):
    data = await state.get_data()
    accountId = data.get("accountId")

    try:
        account = await Account.get(accountId)
        blumAccount = await BlumAccount.getByAccountId(account.id)
        playPasses = int(message.text)

        if playPasses > blumAccount.allPlayPasses:
            return await message.answer(text.NOT_ENOUGH_PLAY_PASS.format(playPasses=playPasses,
                                                                         allPlayPasses=blumAccount.allPlayPasses))

        blumAccount.availablePlayPasses = playPasses
        await blumAccount.save()
        return await message.answer(text.SUCCESSFULLY_CHANGED_PLAY_PASS.format(newPlayPass=playPasses),
                                    reply_markup=startMenuMarkup())
    except ValueError:
        await message.answer(text.NON_ACCEPTABLE_STRING.value)

