from aiogram import Router, F, typesfrom aiogram.enums import ContentTypefrom aiogram.fsm.context import FSMContextfrom aiogram.types import LabeledPricefrom apps.common.exceptions import InvalidRequestExceptionfrom apps.common.settings import settingsfrom apps.core.keyboards import cancelMenuMarkup, startMenuMarkupfrom apps.core.models import Userfrom apps.core.scheme import UserSchemefrom apps.payment.api import createInvoicefrom apps.payment.keyboards import balanceMenuMarkup, paymentMethodMenuMarkupfrom apps.payment.managers import SubscriptionManagerfrom apps.payment.models import UserPayment, Orderfrom apps.payment.scheme import OrderCreateScheme, InvoiceStatusfrom bot import botfrom db.states import PopupBalanceState, StarsAmountfrom utils import textfrom aiogram.utils.i18n import lazy_gettext as __from aiogram.utils.i18n import gettext as _from utils.events import sendErrorfrom utils.validator import validateAmount, validateStarsAmountpaymentRouter = Router(name="paymentRouter")@paymentRouter.message(F.text == __("💰 Balans"))async def balanceHandler(message: types.Message):    userPayment = await UserPayment.get(message.from_user.id)    balance = round(userPayment.balance, 2)    stars = userPayment.stars    return await message.answer(text.BALANCE.format(balance=balance, stars=stars),                                disable_web_page_preview=True,                                reply_markup=balanceMenuMarkup())@paymentRouter.callback_query(F.data == "popup_balance")async def popupBalance(callback_data: types.CallbackQuery):    await callback_data.answer("")    await bot.send_message(callback_data.from_user.id, "To'lov turini tanlang: ",                           reply_markup=paymentMethodMenuMarkup())@paymentRouter.callback_query(F.data == "stars_payment")async def enterStarsAmount(callback_data: types.CallbackQuery, state: FSMContext):    await callback_data.answer("")    await state.set_state(StarsAmount.amount)    await bot.send_message(callback_data.from_user.id, "To'lov summasini 🌟 stars valyutasida kiriting")async def successfulStarsPayment(message: types.Message):    user = await User.get(message.from_user.id)    userPayment = await UserPayment.get(message.from_user.id)    paidAmount = message.successful_payment.total_amount    scheme = OrderCreateScheme(telegramId=message.from_user.id, userPaymentId=userPayment.id,                               amount=paidAmount, status=InvoiceStatus.PAID)    order = Order(**scheme.model_dump())    order.cryptoCurrency = 'XTR'    order.invoiceId = message.successful_payment.telegram_payment_charge_id    order.network = 'Telegram'    order.paidAmount = paidAmount    await order.save()    userPayment.stars += paidAmount    await userPayment.save()    await bot.send_message(message.from_user.id, text=text.SUCCESSFULLY_STARS_PAYED.format(        amount=paidAmount))    await SubscriptionManager.updateCanceledSubscriptions(telegramId=user.telegramId)@paymentRouter.message(StarsAmount.amount)async def processStarsAmount(message: types.Message, state: FSMContext):    if message.successful_payment is not None:        await successfulStarsPayment(message)        return    try:        amount = validateStarsAmount(message.text)        await bot.send_invoice(            chat_id=message.from_user.id,            title=text.STARS_TITLE.value,            description=text.STARS_INVOICE_DETAILS.format(stars=amount),            payload="Payment through bot",            provider_token="",            currency="XTR",            prices=[                LabeledPrice(                    label=text.STARS_TITLE.value,                    amount=amount                )            ]        )    except InvalidRequestException as e:        return await message.answer(e.messageText)    await state.clear()@paymentRouter.callback_query(F.data == "crypto_fiat_payment")async def cryptoFiatHandler(callback_data: types.CallbackQuery, state: FSMContext):    await callback_data.answer("")    await state.set_state(PopupBalanceState.amount)    await bot.send_message(callback_data.from_user.id, text.ENTER_AMOUNT.value, reply_markup=cancelMenuMarkup())@paymentRouter.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)async def starsSuccessHandler(message: types.Message):    await successfulStarsPayment(message)@paymentRouter.pre_checkout_query()async def preCheckoutQuery(preCheckoutQuery: types.PreCheckoutQuery):    await bot.answer_pre_checkout_query(preCheckoutQuery.id, ok=True)@paymentRouter.message(PopupBalanceState.amount)async def processAmount(message: types.Message, state: FSMContext):    try:        amount = validateAmount(amount=message.text)        userPayment = await UserPayment.get(message.from_user.id)        user = await User.get(message.from_user.id)        scheme = OrderCreateScheme(telegramId=message.from_user.id, userPaymentId=userPayment.id,                                   amount=amount, status=InvoiceStatus.NEW)        order = Order(**scheme.model_dump())        await order.save()        response = createInvoice(orderId=order.id, amount=amount, lang=user.languageCode)        order.expirationTime = response.data.expiration_time        order.invoiceId = response.data.invoice_id        await order.save()    except InvalidRequestException as e:        await sendError(text.ERROR_TEMPLATE.format(message=e.exceptionText, telegramId=message.from_user.id))        return await message.answer(e.messageText)    await state.clear()    await bot.send_message(message.from_user.id,                           text.INVOICE_DETAILS.format(amount=amount, invoiceUrl=response.data.invoice_url),                           reply_markup=startMenuMarkup())@paymentRouter.callback_query(F.data == "referral")async def referralHandler(callback: types.CallbackQuery):    await callback.answer("")    telegramId = callback.from_user.id    user = await User.get(telegramId)    userScheme = UserScheme(**user.to_dict())    referralsCount = len(userScheme.referralUsers)    return await bot.send_message(telegramId,                                  text.REFERRAL_INFO.format(botUsername=settings.BOT_USERNAME,                                                            referralPrice=settings.REFERRAL_PRICE,                                                            referralsCount=referralsCount,                                                            referralId=telegramId))