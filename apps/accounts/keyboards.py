from typing import List

from aiogram.filters.callback_data import CallbackData
from aiogram.utils import keyboard

from apps.accounts.models import Account, BlumAccount
from bot import _, __


class AccountCallback(CallbackData, prefix="accounts"):
    accountId: int
    name: str


async def accountsMarkup(accounts: List[Account]):
    accountsBuilder = keyboard.InlineKeyboardBuilder()

    for account in accounts:
        blumAccount = await BlumAccount.getByAccountId(account.id)
        balance = "null" if blumAccount is None else blumAccount.availableBalance
        accountsBuilder.button(text=_("{sessionName} | {balance}").format(sessionName=account.sessionName,
                                                                          balance=balance),
                               callback_data=AccountCallback(accountId=account.id,
                                                             name="account_details"))

    accountsBuilder.button(text=_("➕ Akkaunt qo'shish"), callback_data="add_account")
    accountsBuilder.adjust(1, 1)
    return keyboard.InlineKeyboardMarkup(inline_keyboard=accountsBuilder.export())


def accountsListMarkup(accounts: List[Account]):
    accountsBuilder = keyboard.ReplyKeyboardBuilder()

    for account in accounts:
        accountsBuilder.button(text=account.sessionName)

    accountsBuilder.button(text=_("Barchasini tanlash"))
    accountsBuilder.button(text=_("⬅️ Bosh sahifa"))
    accountsBuilder.adjust(1, 1)
    return keyboard.ReplyKeyboardMarkup(keyboard=accountsBuilder.export(), resize_keyboard=True)


def accountParamsMarkup(accountId: int):
    paramsAccountBuilder = keyboard.InlineKeyboardBuilder()
    paramsAccountBuilder.button(text=_("🎟️ O'yin biletlari sonini o'zgartirish"),
                                callback_data=AccountCallback(accountId=accountId, name="play_pass_change"))
    paramsAccountBuilder.button(text=_("🌐 Proksi ma'lumotlari"),
                                callback_data=AccountCallback(accountId=accountId, name="proxy_info"))
    paramsAccountBuilder.button(text=_("🔰 Obunani yangilash"),
                                callback_data=AccountCallback(accountId=accountId, name="update_subscription"))
    paramsAccountBuilder.adjust(1, 1)
    return keyboard.InlineKeyboardMarkup(inline_keyboard=paramsAccountBuilder.export())
