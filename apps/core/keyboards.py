from aiogram.filters.callback_data import CallbackData
from aiogram.utils import keyboard
from bot import _, __


def backMenuMarkup():
    backMenuBuilder = keyboard.ReplyKeyboardBuilder()
    backMenuBuilder.button(text=_("⬅️ Bosh sahifa"))
    return keyboard.ReplyKeyboardMarkup(keyboard=backMenuBuilder.export(),
                                        resize_keyboard=True)


def cancelMenuMarkup():
    cancelMenuBuilder = keyboard.ReplyKeyboardBuilder()
    cancelMenuBuilder.button(text=_("❌ Bekor qilish"))
    cancelMenuBuilder.adjust(1, 1)
    return keyboard.ReplyKeyboardMarkup(keyboard=cancelMenuBuilder.export(),
                                        resize_keyboard=True,
                                        one_time_keyboard=True)


def startMenuMarkup():
    startMenuBuilder = keyboard.ReplyKeyboardBuilder()
    startMenuBuilder.button(text=_("👾 Blum ishlash"))
    startMenuBuilder.button(text=_("👥 Akkauntlar"))
    startMenuBuilder.button(text=_("💰 Balans"))
    startMenuBuilder.button(text=_("🌐 Tilni o'zgartirish"))
    startMenuBuilder.button(text=_("🚫 Farmingni to'xtatish"))
    startMenuBuilder.adjust(1, 2, 1)
    return keyboard.ReplyKeyboardMarkup(keyboard=startMenuBuilder.export(),
                                        resize_keyboard=True,
                                        one_time_keyboard=True)


languageMenuBuilder = keyboard.ReplyKeyboardBuilder()
languageMenuBuilder.button(text="🇺🇿 O'zbekcha")
languageMenuBuilder.button(text="🇷🇺 Русский")
languageMenuBuilder.button(text="🇬🇧 English")
languageMenuBuilder.adjust(1, 1)
languageMenuMarkup = keyboard.ReplyKeyboardMarkup(keyboard=languageMenuBuilder.export(),
                                                  resize_keyboard=True,
                                                  one_time_keyboard=True)


def helperMenuMarkup():
    helperMenuBuilder = keyboard.ReplyKeyboardBuilder()
    helperMenuBuilder.button(text=_("🤔 Botni qanday ishlataman?"))
    helperMenuBuilder.button(text=_("🪄 Bot imkoniyatlari"))
    helperMenuBuilder.button(text=_("💸 Bot bilan qancha ishlashim mumkin?"))
    helperMenuBuilder.button(text=_("🎱 Kriptoni qayerdan olaman?"))
    helperMenuBuilder.button(text=_("⬅️ Bosh sahifa"))
    helperMenuBuilder.adjust(2, 2, 1)
    return keyboard.ReplyKeyboardMarkup(keyboard=helperMenuBuilder.export(),
                                        resize_keyboard=True,
                                        one_time_keyboard=True)