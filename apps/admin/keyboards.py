from uuid import UUID

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


adminKeyboardsBuilder = InlineKeyboardBuilder()
adminKeyboardsBuilder.button(text="➡️ Xabar yuborish", callback_data="send_message_to_users")
adminKeyboardsBuilder.button(text="➡️ Userga xabar yuborish", callback_data="send_message_to_user")
adminKeyboardsBuilder.adjust(1, 1)
adminKeyboardsMarkup = InlineKeyboardMarkup(inline_keyboard=adminKeyboardsBuilder.export())

cancelKeyboardsBuilder = ReplyKeyboardBuilder()
cancelKeyboardsBuilder.button(text="/cancel")
cancelKeyboardsMarkup = ReplyKeyboardMarkup(keyboard=cancelKeyboardsBuilder.export(),
                                            resize_keyboard=True, one_time_keyboard=True)

sendMessageBuilder = ReplyKeyboardBuilder()
sendMessageBuilder.button(text="Inline bilan")
sendMessageBuilder.button(text="Oddiy post")
sendMessageBuilder.button(text="⬅️ Bosh sahifa")
sendMessageBuilder.adjust(2, 1)

sendMessageMarkup = ReplyKeyboardMarkup(keyboard=sendMessageBuilder.export(), resize_keyboard=True,
                                        one_time_keyboard=True)


def getInlineMarkup(inline_keyboards):
    inlineBuilder = InlineKeyboardBuilder()

    for kb in inline_keyboards:
        inlineBuilder.button(text=str(kb["name"]),
                             url=str(kb["callback_url"]))
    
    return InlineKeyboardMarkup(inline_keyboard=inlineBuilder.export())
