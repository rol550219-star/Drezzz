import os
from deep_translator import GoogleTranslator
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("TOKEN")

current_language = "ru"

languages = {
    "ru": "🇷🇺 Русский",
    "uk": "🇺🇦 Українська",
    "en": "🇬🇧 English",
    "de": "🇩🇪 Deutsch",
    "fr": "🇫🇷 Français",
    "es": "🇪🇸 Español",
    "pl": "🇵🇱 Polski",
    "it": "🇮🇹 Italiano",
    "tr": "🇹🇷 Türkçe",
    "ko": "🇰🇷 한국어",
    "ar": "🇸🇦 العربية",
    "hi": "🇮🇳 हिन्दी",
    "pt": "🇵🇹 Português",
    "zh-CN": "🇨🇳 中文",
    "ja": "🇯🇵 日本語",
    "kk": "🇰🇿 Қазақша",
    "uz": "🇺🇿 Oʻzbekcha",
}
async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    row = []

    for code, name in languages.items():
        row.append(
            InlineKeyboardButton(
                name,
                callback_data=code
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    await update.message.reply_text(
        "🌐 Выберите язык перевода:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_language

    query = update.callback_query

    await query.answer()

    current_language = query.data

    await query.edit_message_text(
        f"✅ Язык выбран: {languages[current_language]}"
    )
  async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    row = []

    for code, name in languages.items():
        row.append(
            InlineKeyboardButton(
                name,
                callback_data=code
            )
        )

        if len(row) == 2:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    await update.message.reply_text(
        "🌐 Выберите язык перевода:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_language

    query = update.callback_query

    await query.answer()

    current_language = query.data

    await query.edit_message_text(
        f"✅ Язык выбран: {languages[current_language]}"
    )async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_language

    if update.message is None:
        return

    text = update.message.text

    if not text:
        return

    # Не перекладаємо команди
    if text.startswith("/"):
        return

    try:
        translated = GoogleTranslator(
            source="auto",
            target=current_language
        ).translate(text)

        if translated != text:
            await update.message.reply_text(
                f"🌐 {translated}"
            )

    except Exception as e:
        print(e)
      app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("language", language))
app.add_handler(CallbackQueryHandler(select_language))
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        translate_message
    )
)

print("Бот запущен!")

app.run_polling()
