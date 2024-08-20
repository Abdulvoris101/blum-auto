from aiogram.utils.i18n import lazy_gettext as __
from aiogram.utils.i18n import gettext as _

START_WELCOME = __("""👋 Salom fren, bot bilan pul ishlab topishga tayyormisiz?

Bot imkoniyatlari:
1. Telegram akkauntlarni birgina botdan boshqarish 
2. Kunlik yeg'ilgan blumlarni avtomatik olish
4. Do'stlar bo'limidagi yeg'ilgan blumlarni avtomatik olish
5. O'yinlarni avtomatik o'ynash

🔒 Xar bir akkaunt uchun shaxsiy proksi ishlatilinadi, blum bilan siz xech qanday muammoga duch kelmaysiz.
Proksi ma'lumotlarini akkaunt bo'limida ko'rishingiz mumkin

💰 Botdan qancha soqqa ko'tarish mumkinligini /help kommandasi orqali bilib oling""")

SELECT_LANGUAGE = __("""Muloqot tilini tanlang
Выберите язык
Choose language""")

THANKS_FOR_CHOOSING = __("""🎉 Bizni tanlaganiz uchun rahmat
Bonus sifatida sizga tekin obuna taqdim etildi""")

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

ENTER_PHONE_NUMBER = __("""<b>Ulamoqchi bo'lgan telefon raqamingizni kiriting:</b> """)
ENTER_VERIFICATION_CODE = __("""Telegramingizga kelgan tasdiqlash kodini kiriting: """)
ENTER_PASSWORD = __("""🔒 2-bosqichli parolingizni kiriting: """)
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

ACCOUNT_REGISTERED = """#register_account\nuserTelegramId: {userTelegramId}\naccountTelegramId: {accountTelegramId}\nsessionName: {sessionName}\nstatus: {status}

⚠️ Account need proxy to assign"""


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
SUCCESSFULLY_PLAYED_GAMES = __("""\n\n🟢 O'yin muvaffiqiyatli o'ynaldi! Berilgan mukofot: {points}""")
PLAYING_NOT_AVAILABLE = __("""\n\n🟡 Ushbu akkaunt uchun o'yin uchun ruxsat etilgan biletlar mavjud emas!""")
FINISHED_FARM = __("\n\n🟢 Farming tugadi.\n\n💲Balans - {availableBalance} blum\n🎟O'yin uchun mavjud biletlar: {playPasses}\n")
TIMER_FARMING_CLAIMED = __("""\n\n🟢 Farmingdan blum olindi""")
IN_PROGRESS_FARMING = __("""\n\n🟢 Blum yig'ilmoqda. Qolgan vaqt: {sleepDuration} soat""")
FARMING_STARTED = __("""\n\n🟢 Farming boshlandi...""")
WAIT_UNTIL_NEXT_GAME = __("""\n\n🟡 Keyingi o'yin o'ynalishdan oldin 5 sekund kutamiz...""")
LONG_INTERVAL_GAME = __("""\n\n🟡 Xar 5ta o'yindan keyin 30 sekund kutamiz...""")
WAIT_A_MOMENT = __("""Biroz kuting...""")

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

# Balance
BALANCE = __("""💵 Balans: {balance}$

👤 Har bir akkauntni ulash oyiga: 1.99$ ≈ 25,000 so'm

✨ 1-akkaunt uchun 3 kunlik tekin obuna taqdim etiladi

⚠️ Xavfsizlik uchun to'lov faqat kripto orqali qabul qilinadi!
💡 Kripto haqida bilmasangiz qo'llanma - /help""")

REFERRAL_INFO = __("""Sizning referalingiz: https://t.me/{botUsername}?start={referralId}

Referallar soni: {referralsCount}

Ushbu referal orqali xar bir taklif etilgan do'stingiz uchun {referralPrice}$ qo'lga kiriting!""")

INVOICE_DETAILS = __(""" To'lov tafsilotlari:

Summa: {amount}$
To'lov havolasi: {invoiceUrl}

To'lovni amalga oshirgandan so'ng taxminan 1-2 minut atrofida balansingizga pul kelib qo'shiladi

Kelajak puli kripto-ni bilmasangiz qo'llanmani ko'rib chiqing - /help
Toʻlov jarayonida biror muammoga duch kelsangiz yoki savollaringiz boʻlsa, bizga murojat qiling - @aerkinov1
""")
SUCCESSFULLY_PAYED = __("""{amount}$ balansingizga kelib qo'shildi, bizni tanlaganingiz uchun rahmat fren 😊""")
ENTER_AMOUNT = __("""To'lov summasini kiriting: """)

INCORRECT_LANGUAGE_CODE = __("""Notog'ri tilni kiritingiz, Iltimos menyudagi tillardan birini kiriting!""")


CONGRATS_GAVE_REQUESTS = __("""Do'stingizni taklif etganingiz uchun sizga {referralPrice}$ taqdim 
etildi 🎉.""")

NOT_REGISTERED = __("Botdan foydalanish uchun - /start")
INCORRECT_AMOUNT = __("Notog'ri summa kiritilindi")
MINIMAL_AMOUNT = __("Xisobni to'ldirish uchun minimal summa: 1.49$")
SUBSCRIPTION_ALREADY_ACTIVATED = __("Obuna allaqachon faollashtirilgan ✅\n\n")
NOT_ENOUGH_BALANCE = __("""Akkaunt qo'shish yoki yangilash uchun balansingizda mablag' mavjud emas ❌

Akkaunt ulash narxi oyiga - {price}$""")

# Subscription
SUBSCRIPTION_UPDATED = __("""Tabriklaymiz akkauntingiz obunasi yangilandi 🥳

Bizni tanlaganiz uchun tashakkur 🌟""")

SUBSCRIPTION_UPDATED_SCHEDULE = __("""Salom Qadrli Foydalanuvchi 👋, 

{sessionName} akkauntingiz obunasi yangilandi

Bizni tanlaganiz uchun tashakkur 🌟""")

SUBSCRIPTION_END = __("""🚀 Obunani yangilash vaqti keldi!

Salom Qadrli Foydalanuvchi 👋,

{sessionName} akkauntingiz obuna muddati tugadi! Obunani davom ettirish uchun balansingizni {needAmount}$ ga 
to'ldiring

Bizni tanlaganiz uchun tashakkur 🌟
""")

SUBSCRIPTION_INACTIVE = __("""{sessionName} akkaunt uchun obuna mudati tugagan yoki mavjud emas! 🙁

🔄 Obunani qayta aktivlashtirish uchun akkauntlar bo'limiga o'ting""")

# WARNINGS
BLUM_NOT_LAUNCHED = __("""Akkauntingizda blum ishga tushirilmagan, @BlumCryptoBot botga kirib ro'yxatdan o'ting""")
# Errors
PAYMENT_ERROR = __("""To'lov tizimida xatolik, iltimos keyinroq urinib ko'ring""")
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
