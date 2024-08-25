from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

START_WELCOME = __("""👋 Salom fren, bot bilan pul ishlab topishga tayyormisiz?

Bot imkoniyatlari:
1. Barcha akkauntlarni birgina botdan boshqarish 
2. Kunlik yeg'ilgan blumlarni avtomatik olish
3. O'yinlarni avtomatik o'ynash
4. Xar bir akkaunt uchun shaxsiy proksi 🔒

ℹ️ Proksi ma'lumotlarini akkaunt bo'limida ko'rishingiz mumkin

💰 Botdan qancha soqqa ko'tarish mumkinligini /help kommandasi orqali bilib oling""")

SELECT_LANGUAGE = __("""Muloqot tilini tanlang
Выберите язык
Choose language""")

THANKS_FOR_CHOOSING = __("""🎉 Bizni tanlaganiz uchun rahmat
Bonus sifatida 1-akkaunt uchun 3 kunlik tekin obuna taqdim etiladi""")

# FAQ
BOT_USAGE_FAQ = __("""<b>Botni qanday ishlataman?</b>
Botni ishlatish uchun Telegram akkauntingizni botga ulashingiz kerak. Bot sizning akkauntingizga kirib, 
blumni avtomatik ravishda ishlaydi.""")

BOT_OPPORTUNITY = __("""<b>Nega blum topishni avtomatlashtirishim kerak?</b>
Bu juda qulay! Siz barcha akkauntlaringizdan bir buyruq orqali blumni avtomatik farm qilishingiz mumkin. 
Bot kunlik blumni, do'stlar bo'limidan blumni yig'adi va o'yin o'ynab vaqtingizni tejaydi. Eng katta imkoniyati  esa 
o'yinlarni aniqlik bilan o'ynashidir.""")

PRICE_BLUM = __("""<b>Bot bilan qancha pul ishlashim mumkin?</b>

Hozircha aniq emas, lekin blum asoschisining aytishicha, uning narxi boshqa coinlardan yuqori bo'ladi. <a href='https://www.youtube.com/@smerkiscrypto/videos'>Manba</a>

Keling bot bilan oyiga qancha blum ishlashingizni hisoblab uni notcoin narxida chiqarib ko'ramiz:

Bot bilan siz kuniga taxminan 517 ta blum ishlab topsangiz, 
Oyiga: 15,510 blum ≈ $232.65
10 ta akkaunt bilan oyiga $2326 ishlab topsa bo'ladi. 

Afsuski notcoin farm allaqachon yopilgan, lekin bu imkoniyat blum o'yinida xali xam  mavjud. 
Bu imkoniyatni qo'ldan boy bermaysiz degan umidamiz 😇""")

CRYPTO_FAQ = __("""
<b>Qanday qilib kripto olishim mumkin?</b>
Bu juda oson. Telegramning @wallet botidagi p2p marketdan xavfsiz va tez kripto sotib olishingiz mumkin.
<a href='https://www.youtube.com/watch?v=TuTTsS_EJb8&ab_channel=PULMAKER'>Video qo'llanma</a>

⚠️ Iltimos faqatgina p2p market va rasmiy birjalardan foydalaning boshqa xech qayerda savdo qilmang!""")

HELP_COMMAND = __("""Qo'llanmaga xush kelibsiz fren,

O'zingiz qiziqtirgan mavzuni tanlang: """)

# Accounts
ACCOUNTS_TEXT = __("""Ulangan akkauntlar soni - {accountsCount}""")

DISCLAIMER_OF_ADDING_ACCOUNT = __("""⚠️ Telegram aynan shu akkauntni ulashga ruxsat bermaydi! Boshqa akkauntingizni 
ulang.

Agar boshqa akkauntingiz bo'lmasa, bizdan arzon narxda sotib olishingiz mumkin: @aerkinov1.
""")

ENTER_PHONE_NUMBER = __("""<b>Ulamoqchi bo'lgan telefon raqamingizni kiriting:</b>

Telefon raqam formati: +99890xxxxxxx""")

ENTER_VERIFICATION_CODE = __("""Telegramingizga kelgan tasdiqlash kodini kiriting: """)
ENTER_2FA_PASSWORD = __("""🔒 2-bosqichli parolingizni kiriting: """)
SMS_SENDING = __("Telegram kod yuborilmoqda....")
SUCCESSFUL_ADDED_ACCOUNT = __("""Akkauntingiz muvaffiqiyatli qo'shildi 🎉. 

Akkaunt haqida to'liq ma'lumot uchun 👥 Akkauntlar bo'limiga o'ting""")
ALREADY_ADDED = __("Bu akkaunt allaqachon qo'shilgan!")
USER_REGISTERED_EVENT_TEMPLATE = __("""#new\nid: {id}\ntelegramId: {telegramId}
\nusername: @{username}\nlanguage: {languageCode}\nname: {firstName}""")
ENTER_PLAY_PASSES = __("""O'yin o'ynash uchun ruxsat etilgan biletlar sonini kiriting: 

Maksimum biletlar soni: {allPlayPasses}""")

NOT_LINK_OWN_ACCOUNT = __("""⚠️ Agar o'zingizning akkauntingizni ulashga uringan bo'lsangiz, Telegram ruxsat bermaydi. 
Iltimos, boshqa akkauntingizni ulang yoki bizdan sotib oling: @aerkinov1.""")

FREE_TYPE = __("Tekin")
PREMIUM_TYPE = __("Pullik")

ACTIVE_STATUS = __("aktiv")
INACTIVE_STATUS = __("🔴 inaktiv")

PROFILE_INFO = __("""👤 <b>Akkaunt xaqida ma'lumotlar:</b>
Sessiya nomi: <b>{sessionName}</b>
Balans: <b>{availableBalance} blum</b>
O'yin uchun mavjud biletlar: <b>{allPlayPasses}</b> 🎟
O'ynash uchun ruxsat etilgan biletlar: <b>{availablePlayPasses}</b> 🎟

⭐️ {type} obuna {subscriptionStatus} xolatda, keyingi to'lov {currentPeriodEnd}
""")

ACCOUNT_PROXY_DETAIL = __("""👤 Akkauntning proksi ma'lumotlari:

- Type: {type}
- Host: {host}
- Port: {port}
- Username: {username}
- Password: {password}

""")

PROXY_NOT_AVAILABLE = __("Proksi ma'lumotlari vaqtinchalik mavjud emas!")

ACCOUNT_REGISTERED = """#register_account\nuserTelegramId: {userTelegramId}\naccountTelegramId: {accountTelegramId}\nsessionName: {sessionName}\nstatus: {status}

{proxyInfo}"""


# Blum
SELECT_ALL = __("Barchasini tanlash")
STARTED_FARMING = __("""Akkaunt: {sessionName}

🟢 Jarayon boshlandi...""")
COULD_NOT_PLAY_GAMES = __("""\n\n🔴 O'yinni o'ynab bo'lmadi! O'yin uchun mavjud biletlar soni: {playPasses}""")
DAILY_REWARD_CLAIM = __("""\n\n🟢 Kunlik blum olindi""")
NO_DAILY_REWARD = __("""\n\n🔴 Kunlik blum olib bo'lingan!""")
CLAIMED_FRIENDS_REWARD =__("\n\n🟢 Do'stlar bo'limidan {amount} blum olindi")
NO_REWARD_FRIENDS = __("""\n\n🔴 Do'stlar uchun blum mavjud emas!""")
NO_ACTIVE_FARMS = __("🔍 Aktiv farming topilmadi")
FARM_STOPPED = __("🔴 Farming toxtadi")
PLAYING_GAME = __("""\n\n🟢 O'yin o'ynalmoqda...""")
SUCCESSFULLY_PLAYED_GAMES = __("""\n\n🟢 O'yin muvaffiqiyatli o'ynaldi! Berilgan mukofot: {points}""")
PLAYING_NOT_AVAILABLE = __("""\n\n🟡 Ushbu akkaunt uchun o'yin uchun ruxsat etilgan biletlar mavjud emas!""")
FINISHED_FARM = __("""\n\n🟢 Farming tugadi.\n
👤 Akkauntlar bo'limida bot sizning o'rningizda nechta o'yin o'ynashini o'zgartishingiz mumkin

🎟 O'yin uchun mavjud biletlar: {playPasses}
🎟 O'yin uchun ruxsat etilgan biletlar: {availablePlayPasses}

👾 Balans - {availableBalance} blum""")

TIMER_FARMING_CLAIMED = __("""\n\n🟢 Farmingdan blum olindi""")
IN_PROGRESS_FARMING = __("""\n\n🟢 Blum yig'ilmoqda. Qolgan vaqt: {sleepDuration} soat""")
FARMING_STARTED = __("""\n\n🟢 Farming boshlandi...""")
WAIT_UNTIL_NEXT_GAME = __("""\n\n🟡 Keyingi o'yin o'ynalishdan oldin 5 sekund kutamiz...""")
LONG_INTERVAL_GAME = __("""\n\n🟡 Xar 5ta o'yindan keyin 30 sekund kutamiz...""")
WAIT_A_MOMENT = __("""Biroz kuting...""")
LOADING_ACCOUNT_INFORMATION = __("""⏳ Akkaunt ma'lumotlari olinmoqda...""")

SUCCESSFULLY_CHANGED_PLAY_PASS = __("""🎟 Ruxsat etilgan biletlar soni - {newPlayPass} taga o'zgardi""")
BOT_COULD_PLAY = __("""\n⚠️ Bot sizning o'rningizda nechta o'yin o'ynashini o'zgartishingiz mumkin""")
NOT_ENOUGH_PLAY_PASS = __("""Sizda o'yin uchun biletlar mavjud emas - {playPasses}. Maksimum biletlar soni: {allPlayPasses}""")

WRONG_ACCOUNT = __("""Notog'ri akkaunt tanlandi!""")
SELECT_FARM_ACCOUNT = __("""Qaysi akkauntlarni farm qilamiz ⚡️""")
INACTIVE_SESSION = __("""☹️ Akkaunt inaktiv xolatda

⚠️ Siz cpython sessiyasini telegramning sessiyasilar bo'limidan o'chirib yuborgansiz.
Akkauntni ishlatish uchun qayta qo'shing!""")

WRONG_PASSWORD = __("""Parol notog'ri""")

ACCOUNT_AVAILABLE_TO_FARM = __("""{sessionName} akkauntingiz farming uchun mavjud""")

# Bonus
INSTRUCTION_TO_GET_FREE_TG = __("Test uchun telegram akkaunt olish uchun bizga yozing - @aerkinov1")
ENTER_TYPE_OF_METHOD = __("To'lov turini tanlang: ")
ENTER_STARS_AMOUNT = __("""🌟 To'lov summasini stars valyutasida kiriting:

Stars narxlarini telegram sozlamalardan ko'rishingiz mumkin""")
# Balance
BALANCE = __("""💵 Balans: {balance}$

🌟 Stars: {stars}

⚡️ 1 akkaunt uchun 3 kunlik tekin obuna beriladi
👤 Har bir akkauntni ulash oyiga: 1.99$ yoki 100 stars

Qabul qilinadigan to'lov turlari: 
- 💳 visa/mastercard
- 🪙 crypto
- 🌟 telegram stars

💡 Kripto haqida bilmasangiz qo'llanma - /help""")

REFERRAL_INFO = __("""Sizning referalingiz: https://t.me/{botUsername}?start={referralId}

Referallar soni: {referralsCount}

Ushbu referal orqali do'stingizni taklif eting va u balansiga pul to'ldirishi bilan {referralPrice}$ qo'lga kiriting!""")

INVOICE_DETAILS = __("""To'lov tafsilotlari:

Summa: {amount}$
To'lov havolasi: {invoiceUrl}

To'lovni amalga oshirgandan so'ng taxminan 1-2 minut atrofida balansingizga pul kelib qo'shiladi

Toʻlov jarayonida biror muammoga duch kelsangiz yoki savollaringiz boʻlsa, bizga murojat qiling - @aerkinov1
""")

STARS_TITLE = __("Balansni to'ldirish")
STARS_INVOICE_DETAILS = __("""Balansni to'ldirish uchun {stars} 🌟 stars to'lov amalga oshiring""")

SUCCESSFULLY_PAYED = __("""{amount}$ balansingizga kelib qo'shildi, bizni tanlaganingiz uchun rahmat fren 😊""")
ENTER_AMOUNT = __("""To'lov summasini dollar valyutasida kiriting: """)
SUCCESSFULLY_STARS_PAYED = __("""{amount} stars balansingizga kelib qo'shildi, bizni tanlaganingiz uchun rahmat 
fren""")

INCORRECT_LANGUAGE_CODE = __("""Notog'ri tilni kiritingiz, Iltimos menyudagi tillardan birini kiriting!""")


CONGRATS_GAVE_REQUESTS = __("""Do'stingiz balansini to'ldirgani uchun sizga {referralPrice}$ taqdim etildi 🎉.""")

NOT_REGISTERED = __("Botdan foydalanish uchun - /start")
INCORRECT_AMOUNT = __("Notog'ri summa kiritilindi")
MINIMAL_AMOUNT = __("Xisobni to'ldirish uchun minimal summa: 1$")
MINIMAL_AMOUNT_STARS = __("Xisobni to'ldirish uchun minimal summma: 100 stars 🌟")
SUBSCRIPTION_ALREADY_ACTIVATED = __("Obuna allaqachon faollashtirilgan ✅\n\n")
NOT_ENOUGH_BALANCE = __("""Akkaunt qo'shish yoki yangilash uchun balansingizda mablag' mavjud emas ❌

Akkaunt ulash oyiga - {price}$ yoki {stars} stars 🌟""")


# Subscription
SUBSCRIPTION_UPDATED = __("""Tabriklaymiz akkauntingiz obunasi yangilandi 🥳

Bizni tanlaganiz uchun tashakkur 🌟""")

SUBSCRIPTION_UPDATED_SCHEDULE = __("""Salom Qadrli Foydalanuvchi 👋, 

{sessionName} akkauntingiz obunasi yangilandi

Bizni tanlaganiz uchun tashakkur 🌟""")

SUBSCRIPTION_END = __("""🚀 Obunani yangilash vaqti keldi!

Salom Qadrli Foydalanuvchi 👋

{sessionName} akkauntingiz obuna muddati tugadi! Obunani davom ettirish uchun balansingizni {needAmount}$ ga to'ldiring

Bizni tanlaganiz uchun tashakkur 🌟
""")

SUBSCRIPTION_INACTIVE = __("""{sessionName} akkaunt uchun obuna mudati tugagan yoki mavjud emas! 🙁

🔄 Obunani qayta aktivlashtirish uchun akkauntlar bo'limiga o'ting""")

FORBIDDEN_TO_PLAY_GAMES = __("""⭕️ Bepul obunada siz bot orqali 5tadan ortiq o'yin o'ynolmaysiz. Botdan to'liq foydalanib xoxlagancha o'yin o'ynash uchun pullik obunani aktivlashtiring

Pullik obunani aktivlashtirish uchun akkauntlar bo'limiga o'tib akkauntingizni tanlang va obunani yangilash tugmasini bosing!""")

# Admin | not need i18n

INLINE_BUTTONS_GUIDE = """Inline knopkalarni kiriting. 
Misol uchun\n <code>./Test-t.me//texnomasters\n./Test2-t.me//texnomasters</code> """

SELECT_MESSAGE_TYPE = "Xabar/Rasm/Video kiriting"
MESSAGE_SENT = "Xabar yuborildi!"
SEND_MESSAGE = "Xabar yuborish!"
ENTER_TYPE_MESSAGE = "Xabar turini kiriting"
WELCOME_ADMIN = "Xush kelibsiz admin!"
ENTER_USER_ID = "User id kiriting"
ENTER_MESSAGE = "Xabarni kiriting"
USER_BLOCKED = "Foydalanuvchi bloklangan!"
ENTER_PASSWORD = "Parolni kiriting"

# WARNINGS
BLUM_NOT_LAUNCHED = __("""Akkauntingizda blum ishga tushirilmagan, @BlumCryptoBot botga kirib ro'yxatdan o'ting""")
# Errors
CANCELED_TEXT = "Bekor qilindi!"

SENT_USER_REPORT_TEXT = """Message sent to {receivedUsersCount} users
Bot was blocked by {blockedUsersCount} users"""


PAYMENT_ERROR = __("""To'lov tizimida xatolik yuz bermoqda, to'lov uchun bizga yozing - @aerkinov1""")
ERROR_TEMPLATE = """"#error\ntelegramId: {telegramId}
message: {message}"""
ORDER_ERROR_TEMPLATE = __("""#error\norderId: {orderId}\nmessage: {message}""")

SERVER_ERROR = __("Nimadir xatolik ketdi. Iltimos qayta urinib ko'ring!")
INVALID_PHONE_NUMBER_FORMAT = __("""Nomerni ushbu formatda kiriting +99890103xxxx!""")
INVALID_PHONE_NUMBER = __("""Notog'ri telefon raqam!""")
INVALID_VERIFICATION_CODE = __("Notog'ri tasdiqlash kodi")
EXPIRED_VERIFICATION_CODE = __("""🔴 Tasdiqlash kodi eskirgan""")
EXPIRED_CODE = __("Tasdiqlash kodi eskirgan. Qayta urinib ko'ring")
TELEGRAM_NOT_LET = __("""⚠️ Agar o'zingizning akkauntingizni ulashga uringan bo'lsangiz, Telegram ruxsat bermaydi. Iltimos, boshqa akkauntingizni ulang yoki bizdan sotib oling: @aerkinov1.""")
SOMETHING_WRONG = __("""Nimadir xato ketdi, Iltimos qayta urinib ko'ring!""")
CAN_NOT_CONNECT_TO_TELEGRAM = __("Telegramga bog'lanib bo'lmadi, qayta urinib ko'ring")
TOO_MANY_REQUESTS = __("""Telegramingizga juda xam ko'p so'rovlar bo'lgani uchun telegram 15 soatlik tannafusga tushdi. 
Iltimos 15 soatdan so'ng qayta urinib ko'ring!""")
NO_ACCOUNTS_TO_FARM = __("""🔴 Blum farming mavjud emas 

Siz xali akkaunt qo'shmagansiz akkaunt qo'shish uchun "👥 Akkauntlar" bo'limiga o'ting""")
SOMETHING_WRONG_ON_BLUM = __("{sessionName} | Akkauntda xatolik, iltimos qayta urinib ko'ring!")
NON_ACCEPTABLE_STRING = __("""Iltimos to'g'ri raqam kiriting""")
BLUM_ERROR = __("""Blumda xatolik iltimos qayta urinib ko'ring!""")
CANCELED = __("Bekor qilindi")
BAD_REQUEST = """Telegram bad request {errorMessage} - user id: {userId}"""
ACCOUNT_NOT_FOUND = """Account not found"""
SESSION_FILE_NOT_EXISTS = """Session file doesn't exists"""
SESSION_EXPIRED = """Session expired - {e}"""
SESSION_ENDED = __("""{sessionName} - sessiya tugatilgan!""")

ONLY_ACCEPTS_TEXT = "Faqatgina text turi qabul qilinadi!"
PROXY_BUY_ERROR = """#proxy
error: {error}
code: {errorCode}"""