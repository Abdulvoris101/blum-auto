from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from pydantic_core import ValidationError

from bot import bot, logger
from db.states import AdminLoginState, SendMessageToUsers, SendMessageToUser
from utils.message import SendAny
from .models import Admin
from apps.core.managers import UserManager
from .keyboards import (adminKeyboardsMarkup, cancelKeyboardsMarkup,
                        sendMessageMarkup, getInlineMarkup, selectAuditionMarkup)
from utils import extractInlineButtonsFromText, text
from utils.events import sendError
from apps.common.filters import IsAdmin, checkPassword
from aiogram.exceptions import TelegramBadRequest

from ..core.keyboards import backMenuMarkup

adminRouter = Router(name="adminRouter")


@adminRouter.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    if await Admin.isAdmin(message.from_user.id):
        return await bot.send_message(message.from_user.id, text.CANCELED_TEXT, reply_markup=adminKeyboardsMarkup)
    return await bot.send_message(message.from_user.id, text.CANCELED_TEXT)


@adminRouter.message(Command('admin'))
async def adminHandler(message: types.Message, state: FSMContext):
    if await Admin.isAdmin(message.from_user.id):
        return await bot.send_message(message.from_user.id, text.WELCOME_ADMIN,
                                      reply_markup=adminKeyboardsMarkup)

    await state.set_state(AdminLoginState.password)
    return await message.answer(text.ENTER_PASSWORD)


@adminRouter.message(AdminLoginState.password)
async def adminLogin(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)

    if checkPassword(password=message.text):
        await state.clear()

        await Admin(message.from_user.id).register()
        return await bot.send_message(message.from_user.id, text.WELCOME_ADMIN, reply_markup=adminKeyboardsMarkup)

    return await message.answer(text.WRONG_PASSWORD.value)


@adminRouter.callback_query(IsAdmin(), F.data == "send_message_to_user")
async def sendMessageToUser(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("")
    await state.set_state(SendMessageToUser.userId)
    return await bot.send_message(callback.from_user.id, text.ENTER_USER_ID)


@adminRouter.message(SendMessageToUser.userId)
async def setUserId(message: types.Message, state: FSMContext):
    await state.update_data(userId=message.text)
    await state.set_state(SendMessageToUser.text)
    return await bot.send_message(message.from_user.id, text.ENTER_MESSAGE)


@adminRouter.message(SendMessageToUser.text)
async def sendTextToUser(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    try:
        await bot.send_message(data.get('userId'), message.text)
        await message.answer(text.MESSAGE_SENT, reply_markup=adminKeyboardsMarkup)
    except TelegramBadRequest:
        logger.error("An error occured!")
        await message.answer(text.USER_BLOCKED, reply_markup=adminKeyboardsMarkup)
    except ValidationError as e:
        logger.error(e)
        await message.answer(text.ONLY_ACCEPTS_TEXT)

# Send Message command


@adminRouter.callback_query(IsAdmin(), F.data == "send_message_to_users")
async def initiateMessageSending(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("")
    await state.set_state(SendMessageToUsers.audition)
    return await bot.send_message(callback.from_user.id, text.SELECT_AUDITION,
                                  reply_markup=selectAuditionMarkup)


@adminRouter.message(SendMessageToUsers.audition)
async def setAudition(message: types.Message, state: FSMContext):
    await state.update_data(audition=message.text)
    await state.set_state(SendMessageToUsers.messageType)
    return await bot.send_message(message.from_user.id, text.ENTER_TYPE_MESSAGE,
                                  reply_markup=sendMessageMarkup)


@adminRouter.message(SendMessageToUsers.messageType)
async def selectMessageType(message: types.Message, state: FSMContext):
    await state.update_data(messageType=message.text)

    if message.text == "Inline bilan":
        await state.set_state(SendMessageToUsers.buttons)
        await bot.send_message(message.from_user.id, text.INLINE_BUTTONS_GUIDE)
        return

    await state.set_state(SendMessageToUsers.message)
    await bot.send_message(message.from_user.id, text.SELECT_MESSAGE_TYPE)


@adminRouter.message(SendMessageToUsers.buttons)
async def setInlineButtons(message: types.Message, state: FSMContext):
    await state.update_data(buttons=message.text)
    await state.set_state(SendMessageToUsers.message)
    return await message.answer(text.SELECT_MESSAGE_TYPE)


@adminRouter.message(SendMessageToUsers.message)
async def sendMessageToUsers(message: types.Message, state: FSMContext):
    data = await state.get_data()
    audition = data.get("audition")

    if audition == "all":
        users = await UserManager.all()
    else:
        users = await UserManager.getAuditionUser(audition)

    sendAny = SendAny(message=message)

    if data.get("messageType") == "Inline bilan":
        inlineButtons = extractInlineButtonsFromText(data.get("buttons"))
        reportData = await sendAny.sendAnyMessages(
            users=users, reply_markup=getInlineMarkup(inlineButtons))
    else:
        reportData = await sendAny.sendAnyMessages(users)

    await sendError(text.SENT_USER_REPORT_TEXT.format(
        receivedUsersCount=reportData.get("receivedUsersCount"),
        blockedUsersCount=reportData.get("blockedUsersCount"))
    )

    await state.clear()
    return await message.answer(text.MESSAGE_SENT, reply_markup=backMenuMarkup())
