from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from telethon.sync import TelegramClient
from telethon.tl.types import InputMessagesFilterDocument

# Telegram bot tokeni
BOT_TOKEN = "8169173541:AAHbLXbACHd5hfY9UH0raRaBcJ3-RITsYOA"
API_ID = "27594926"
API_HASH = "5a9fc2f39b5cb02cd33c3bdebae9950c"
CHANNEL_USERNAME = "@kinoborbaza"  # Ma'lumotlar saqlanadigan kanal
ADMIN_ID = 1438885542  # Admin ID (faqat admin boshqarishi uchun)

# Telethon mijozini sozlash
telethon_client = TelegramClient("bot_session", API_ID, API_HASH)
telethon_client.start()

# Obunani majburiy qilish uchun kanallar ro‘yxati
required_channels = ["@MajburiyKanal1", "@MajburiyKanal2"]

# Foydalanuvchi ma'lumotlari saqlanadigan fayl
users_file = "users.txt"


# --- FUNKSIYALAR ---

# Foydalanuvchi ro‘yxatini yangilash
def save_user(user_id):
    try:
        with open(users_file, "a+") as f:
            f.seek(0)
            users = f.read().splitlines()
            if str(user_id) not in users:
                f.write(f"{user_id}\n")
    except Exception as e:
        print(f"Foydalanuvchi saqlashda xato: {e}")


# Obuna tekshirish
def check_subscription(user_id):
    for channel in required_channels:
        member = telethon_client.get_participants(channel, search=user_id)
        if not member:
            return False
    return True


# /start komandasi
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    save_user(user_id)

    if not check_subscription(user_id):
        update.message.reply_text(
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n"
            + "\n".join(required_channels)
        )
        return

    update.message.reply_text("Assalomu alaykum! Kino bor botimizga Kodni yuboring, va bot kinoni tashlabberadi.")


# Foydalanuvchi xabar yuborganda
def handle_message(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if not check_subscription(user_id):
        update.message.reply_text(
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n"
            + "\n".join(required_channels)
        )
        return

    user_message = update.message.text
    try:
        # Kanal ichidan faylni qidirish
        messages = telethon_client.iter_messages(
            CHANNEL_USERNAME, search=user_message, filter=InputMessagesFilterDocument
        )
        for message in messages:
            if message.file:
                context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=message.file.media
                )
                return
        update.message.reply_text("Kino topilmadi!")
    except Exception as e:
        update.message.reply_text("Xato yuz berdi! ❌")
        print(e)


# Admin uchun statistika
def stats(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        with open(users_file, "r") as f:
            users = f.readlines()
        update.message.reply_text(f"Bot foydalanuvchilari soni: {len(users)}")
    except FileNotFoundError:
        update.message.reply_text("Hozircha foydalanuvchilar yo'q.")


# Admin uchun reklama yuborish
def send_ads(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    message = " ".join(context.args)
    try:
        with open(users_file, "r") as f:
            users = f.readlines()

        for user_id in users:
            context.bot.send_message(chat_id=int(user_id.strip()), text=message)

        update.message.reply_text("Reklama barcha foydalanuvchilarga yuborildi!")
    except Exception as e:
        update.message.reply_text("Xato yuz berdi! ❌")
        print(e)


# Admin uchun majburiy kanalni sozlash
def add_channel(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        return

    channel = context.args[0]
    required_channels.append(channel)
    update.message.reply_text(f"Majburiy obuna uchun kanal qo‘shildi: {channel}")


# --- MAIN ---

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Foydalanuvchi buyruqlari
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Admin buyruqlari
    dp.add_handler(CommandHandler("stats", stats))
    dp.add_handler(CommandHandler("send_ads", send_ads, pass_args=True))
    dp.add_handler(CommandHandler("add_channel", add_channel, pass_args=True))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()