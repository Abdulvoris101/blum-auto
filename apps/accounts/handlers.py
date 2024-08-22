import os
import pickle
import random
from datetime import datetime
from urllib.parse import urlparse

from aiogram import Router, types, F
from aiogram.exceptions import TelegramBadRequest
from pydantic import ValidationError
from pyrogram.errors import BadRequest, SessionPasswordNeeded, AuthKeyUnregistered
from apps.accounts.keyboards import accountsMarkup, AccountCallback, accountParamsMarkup
from apps.accounts.managers import AccountManager, BlumAccountManager, sessionManager, ProxyManager
from apps.accounts.models import Account, BlumAccount, Proxy
from apps.accounts.scheme import AccountCreateScheme, AccountScheme, Status, BlumAccountScheme, BlumAccountCreateScheme, \
    ProxyCreateScheme, ProxyDetailScheme
from apps.common.exceptions import InvalidRequestException, InternalServerException, AiogramException
from apps.common.settings import settings
from apps.core.keyboards import backMenuMarkup, startMenuMarkup, cancelMenuMarkup
from apps.core.models import User
from apps.payment.managers import SubscriptionManager
from apps.payment.models import UserPayment, AccountSubscription
from apps.scripts.blum.blum_bot import BlumBot
from bot import bot, logger, redis
from db.states import AddAccountState, AvailablePlayPassState
from utils import text
from aiogram.fsm.context import FSMContext
from pyrogram import Client
from pyrogram.errors.exceptions import bad_request_400, not_acceptable_406, flood_420, unauthorized_401

from utils.events import sendEvent, sendError
from utils.validator import validatePhoneNumber
from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

accountsRouter = Router(name="accountsRouter")


@accountsRouter.message(F.text == __("👥 Akkauntlar"))
async def accountsHandler(message: types.Message):
    user = await User.get(message.from_user.id)
    accounts = await AccountManager.getUserAccounts(user.id)

    return await message.answer(text.ACCOUNTS_TEXT.format(accountsCount=len(accounts)),
                                reply_markup=await accountsMarkup(accounts))


@accountsRouter.callback_query(AccountCallback.filter(F.name == "account_details"))
async def accountsDetails(callback: types.CallbackQuery, callback_data: AccountCallback):
    account = await Account.get(callback_data.accountId)
    blumAccount = await BlumAccount.createOrGetByAccountId(account.id)

    try:
        waitMomentMessage = await bot.send_message(callback.from_user.id, text.LOADING_ACCOUNT_INFORMATION.value)
        isActiveAccount = await AccountManager.isActiveAccount(account)

        if not isActiveAccount:
            account.status = Status.INACTIVE
            await account.save()
            await bot.delete_message(callback.from_user.id, message_id=waitMomentMessage.message_id)
            return await bot.send_message(callback.from_user.id, text.INACTIVE_SESSION.value)

        proxy = None

        if account.proxyId is not None:
            proxy = await Proxy.get(account.proxyId)
            proxy = ProxyDetailScheme(**proxy.to_dict())

        blum = BlumBot(sessionName=account.sessionName, proxy=proxy)
        await blum.initWebSession()
        await blum.login()
        balance = await blum.balance()

        blumAccount.availableBalance = balance.availableBalance
        blumAccount.allPlayPasses = balance.allPlayPasses
        blumAccount.status = Status.ACTIVE
        account.status = Status.ACTIVE

        await blumAccount.save()
        await account.save()

        await bot.delete_message(callback.from_user.id, message_id=waitMomentMessage.message_id)
        accountScheme = AccountScheme(**account.to_dict())
        blumAccountScheme = BlumAccountScheme(**blumAccount.to_dict())
        PROFILE_INFO = text.PROFILE_INFO.value + text.BOT_COULD_PLAY.value

        isSubscriptionActive = await SubscriptionManager.isAccountSubscriptionActive(account.id)
        subscription = await AccountSubscription.getByAccountId(account.id)

        subscriptionStatus = text.ACTIVE_STATUS.value if isSubscriptionActive else text.INACTIVE_STATUS.value
        type_ = text.FREE_TYPE.value if subscription.isFreeTrial else text.PREMIUM_TYPE.value
        currentPeriodEnd = subscription.currentPeriodEnd.strftime("%d %B")

        await bot.send_message(callback.from_user.id,
                               PROFILE_INFO.format(**blumAccountScheme.model_dump(),
                                                   sessionName=accountScheme.sessionName,
                                                   subscriptionStatus=subscriptionStatus,
                                                   type=type_, currentPeriodEnd=currentPeriodEnd),
                               reply_markup=accountParamsMarkup(accountScheme.id))
    except TelegramBadRequest as e:
        logger.error(f"Tg bad request: {e}")
        logger.error(text.BAD_REQUEST.format(errorMessage=e.message, userId=account.sessionName))
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        await bot.send_message(callback.from_user.id, text.BLUM_ERROR.value)
    except InvalidRequestException as e:
        logger.error(f"Invalid request: {e.messageText}")
        await bot.send_message(callback.from_user.id, e.messageText)
    except Exception as e:
        print(e)
        logger.error(e)
        await sendError(text.ERROR_TEMPLATE.format(message=str(e), telegramId=callback.from_user.id))
        await bot.send_message(callback.from_user.id,
                               text.SOMETHING_WRONG_ON_BLUM.format(sessionName=account.sessionName))


@accountsRouter.callback_query(F.data == "add_account")
async def addAccount(callback: types.CallbackQuery, state: FSMContext):
    userPayment = await UserPayment.get(callback.from_user.id)

    if userPayment.balance < settings.PRICE and userPayment.trialBalance < settings.PRICE:
        return await bot.send_message(callback.from_user.id, text.NOT_ENOUGH_BALANCE.format(price=settings.PRICE))

    await state.set_state(AddAccountState.phoneNumber)
    await bot.send_message(callback.from_user.id, text.DISCLAIMER_OF_ADDING_ACCOUNT.value)
    await bot.send_message(callback.from_user.id, text.ENTER_PHONE_NUMBER.value, reply_markup=cancelMenuMarkup())


class AccountCreationHandler:
    def __init__(self):
        self.session = None

    async def processPhoneNumber(self, message: types.Message, state: FSMContext):
        global inWaitMessage
        phoneNumber = message.text
        sessionName = phoneNumber
        waitMomentMessage = await bot.send_message(message.from_user.id, text.WAIT_A_MOMENT.value)

        if await AccountManager.isExistsBySessionName(sessionName):
            account = await Account.getBySessionName(sessionName)
            if await AccountManager.isActiveAccount(account):
                await bot.delete_message(message.from_user.id, message_id=waitMomentMessage.message_id)
                return await message.answer(text.ALREADY_ADDED.value, reply_markup=startMenuMarkup())

        try:
            await validatePhoneNumber(phoneNumber)

            proxies = ProxyManager.getProxies()
            proxy = random.choice(proxies)
            proxyParsed = urlparse(proxy)

            proxy = {
                "scheme": proxyParsed.scheme,
                "hostname": proxyParsed.hostname,
                "port": proxyParsed.port,
                "username": proxyParsed.username,
                "password": proxyParsed.password
            }

            self.session = Client(name=sessionName, api_id=settings.API_ID, api_hash=settings.API_HASH,
                                  workdir=settings.WORKDIR, proxy=proxy)
            await bot.delete_message(message.from_user.id, message_id=waitMomentMessage.message_id)
            inWaitMessage = await message.answer(text.SMS_SENDING.value)
            await self.session.connect()
            sentCode = await self.session.send_code(phoneNumber)
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
        except (unauthorized_401.AuthKeyUnregistered, AuthKeyUnregistered) as e:
            logger.error(text.SESSION_EXPIRED.format(e=e))
            filePath = os.path.join("sessions/", f"{sessionName}.session")
            fullPath = os.path.abspath(filePath)
            os.remove(fullPath)
        finally:
            await bot.delete_message(message.from_user.id, inWaitMessage.message_id)

        await state.update_data(sessionName=sessionName)
        await state.update_data(phoneNumber=phoneNumber)
        await state.set_state(AddAccountState.verificationCode)
        await message.answer(text.ENTER_VERIFICATION_CODE.value)

    async def processVerificationCode(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        verificationCode = message.text

        try:
            phoneNumber = data.get('phoneNumber')
            sentCode = data.get("sentCode")
            waitMomentMessage = await bot.send_message(message.from_user.id, text.WAIT_A_MOMENT.value)
            await self.session.sign_in(phoneNumber, sentCode, verificationCode)
        except SessionPasswordNeeded:
            await state.set_state(AddAccountState.password)
            return await message.answer(text.ENTER_2FA_PASSWORD.value)
        except bad_request_400.PhoneCodeExpired as e:
            logger.warn(str(e))
            await message.answer(text.EXPIRED_VERIFICATION_CODE.value)
            return await message.answer(text.TELEGRAM_NOT_LET.value)
        except BadRequest as e:
            logger.warn(str(e))
            return await message.answer(text.INVALID_VERIFICATION_CODE.value)

        await processAccountMessage(message, state, self.session, waitMomentMessage.message_id)

    async def processPassword(self, message: types.Message, state: FSMContext):
        try:
            waitMomentMessage = await bot.send_message(message.from_user.id, text.WAIT_A_MOMENT.value)
            await self.session.check_password(message.text)
            await bot.delete_message(message.from_user.id, waitMomentMessage.message_id)
            loadingMessage = await bot.send_message(message.from_user.id, text.LOADING_ACCOUNT_INFORMATION.value)
        except (bad_request_400.PasswordHashInvalid, bad_request_400.PasswordEmpty, bad_request_400.PasswordRequired) as e:
            logger.warn(str(e))
            return await message.answer(text.WRONG_PASSWORD.value)
        except BadRequest as e:
            logger.warn(str(e))
            return await message.answer(text.CAN_NOT_CONNECT_TO_TELEGRAM.value)

        await processAccountMessage(message, state, self.session, loadingMessage.message_id)


accountHandler = AccountCreationHandler()


@accountsRouter.message(AddAccountState.phoneNumber)
async def processPhoneNumber(message: types.Message, state: FSMContext):
    await accountHandler.processPhoneNumber(message, state)


async def processAccountMessage(message: types.Message, state: FSMContext, session: Client, message_id: int):
    data = await state.get_data()
    phoneNumber = data.get('phoneNumber')
    sessionName = data.get("sessionName")

    try:
        proxies = ProxyManager.getProxies()
        proxy = random.choice(proxies)
        proxyParsed = urlparse(proxy)

        proxy = ProxyDetailScheme(id=None, telegramId=None, ip=None, proxyId=None, dateEnd=None,
                                  host=proxyParsed.hostname, port=str(proxyParsed.port),
                                  user=proxyParsed.username, password=proxyParsed.password, type=proxyParsed.scheme)

        blum = BlumBot(sessionName=sessionName, proxy=proxy)
        await blum.initWebSession()
        await blum.login()
        balance = await blum.balance()
        accountInfo = await session.get_me()

        user = await User.get(message.from_user.id)
        isAccount = await AccountManager.isExistsByPhoneNumber(phoneNumber)
        proxyId = None

        print(isAccount)

        if not isAccount:
            response = await ProxyManager.buyProxy(telegramId=user.telegramId)
            status = response.get("status")

            if status is not None and status == "yes":
                proxyObj = await ProxyManager.createByJson(telegramId=user.telegramId, response=response)
                proxyId = proxyObj.id
            else:
                await sendError(text.PROXY_BUY_ERROR.format(error=response.get("error"),
                                                            errorCode=response.get("error_id")))

        accountScheme = AccountCreateScheme(sessionName=sessionName, phoneNumber=phoneNumber, userId=user.id,
                                            telegramId=accountInfo.id, proxyId=proxyId)

        account = await AccountManager.createOrActivate(accountScheme)
        blumAccountScheme = BlumAccountCreateScheme(accountId=account.id, **balance.model_dump())

        await BlumAccountManager.createOrActivate(scheme=blumAccountScheme)
        proxyInfo = "⚠️ Account need proxy to assign" if proxyId is None else "Proxy successfully assigned ✅"
        await sendEvent(text.ACCOUNT_REGISTERED.format(userTelegramId=user.telegramId, accountTelegramId=accountInfo.id,
                                                       status=accountScheme.status,
                                                       sessionName=accountScheme.sessionName,
                                                       proxyInfo=proxyInfo))

        await session.disconnect()
        await state.clear()

        await sessionManager.deleteSession(message.from_user.id)

        userPayment = await UserPayment.get(message.from_user.id)

        if userPayment.balance >= settings.PRICE:
            await SubscriptionManager.subscribe(message.from_user.id, accountId=account.id, isFreeTrial=False)
            userPayment.balance -= settings.PRICE
        else:
            await SubscriptionManager.subscribe(message.from_user.id, accountId=account.id, isFreeTrial=True)
            userPayment.trialBalance -= settings.PRICE

        await userPayment.save()
        await user.save()

        await bot.delete_message(message.from_user.id, message_id=message_id)

        isSubscriptionActive = await SubscriptionManager.isAccountSubscriptionActive(account.id)
        subscription = await AccountSubscription.getByAccountId(account.id)

        subscriptionStatus = text.ACTIVE_STATUS.value if isSubscriptionActive else text.INACTIVE_STATUS.value
        type_ = text.FREE_TYPE.value if subscription.isFreeTrial else text.PREMIUM_TYPE.value
        currentPeriodEnd = subscription.currentPeriodEnd.strftime("%d %B")

        await message.answer(text.PROFILE_INFO.format(**blumAccountScheme.model_dump(),
                                                      sessionName=accountScheme.sessionName,
                                                      subscriptionStatus=subscriptionStatus,
                                                      type=type_, currentPeriodEnd=currentPeriodEnd))
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
    except AiogramException as e:
        logger.error(e.message_text)
        await state.clear()
        return await message.answer(e.message_text, reply_markup=startMenuMarkup())
    except InternalServerException as e:
        logger.warn(str(e.message_text))
        return await message.answer(e.message_text)


@accountsRouter.message(AddAccountState.verificationCode)
async def processVerificationCode(message: types.Message, state: FSMContext):
    await accountHandler.processVerificationCode(message, state)


@accountsRouter.message(AddAccountState.password)
async def processPassword(message: types.Message, state: FSMContext):
    await accountHandler.processPassword(message, state)


@accountsRouter.callback_query(AccountCallback.filter(F.name == "play_pass_change"))
async def processPlayPasses(callback: types.CallbackQuery, callback_data: AccountCallback, state: FSMContext):
    await callback.answer("")
    account = await Account.get(callback_data.accountId)
    blumAccount = await BlumAccount.getByAccountId(account.id)
    await state.set_state(AvailablePlayPassState.availablePlayPass)
    await state.update_data(accountId=account.id)
    await bot.send_message(callback.from_user.id,
                           text.ENTER_PLAY_PASSES.format(allPlayPasses=blumAccount.allPlayPasses),
                           reply_markup=backMenuMarkup())


@accountsRouter.callback_query(AccountCallback.filter(F.name == "update_subscription"))
async def updateSubscription(callback: types.CallbackQuery, callback_data: AccountCallback):
    await callback.answer("")
    account = await Account.get(callback_data.accountId)
    userPayment = await UserPayment.get(callback.from_user.id)

    if await SubscriptionManager.isAccountSubscriptionActive(account.id):
        return await bot.send_message(callback.from_user.id,
                                      text.SUBSCRIPTION_ALREADY_ACTIVATED.value)

    if userPayment.balance < settings.PRICE:
        return await bot.send_message(callback.from_user.id, text.NOT_ENOUGH_BALANCE.format(price=settings.PRICE))

    userPayment.balance -= settings.PRICE
    await userPayment.save()

    await SubscriptionManager.updateSubscription(accountId=account.id, isFreeTrial=False)
    return await bot.send_message(callback.from_user.id, text.SUBSCRIPTION_UPDATED.format(
        sessionName=account.sessionName))


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


@accountsRouter.callback_query(AccountCallback.filter(F.name == "proxy_info"))
async def accountProxy(callback: types.CallbackQuery, callback_data: AccountCallback):
    await callback.answer("")

    account = await Account.get(callback_data.accountId)

    if account.proxyId is None:
        return await bot.send_message(callback.from_user.id, text.PROXY_NOT_AVAILABLE.value)

    proxy = await Proxy.get(account.proxyId)
    return await bot.send_message(callback.from_user.id,
                            text.ACCOUNT_PROXY_DETAIL.format(type=proxy.type, host=proxy.host,
                                                             port=proxy.port, username=proxy.user,
                                                             password=proxy.password))

