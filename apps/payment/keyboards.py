from aiogram.utils import keyboardfrom bot import _, __def balanceMenuMarkup():    balanceMenuBuilder = keyboard.InlineKeyboardBuilder()    balanceMenuBuilder.button(text=_("💵 Xisobni to'ldirish"), callback_data="popup_balance")    balanceMenuBuilder.button(text=_("🆓 Bepul qo'lga kiritish"), callback_data="referral")    balanceMenuBuilder.adjust(1, 1)    return keyboard.InlineKeyboardMarkup(inline_keyboard=balanceMenuBuilder.export())