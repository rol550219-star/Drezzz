import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

# Словарь доступных языков и названий кнопок
LANGUAGES = {
    "en": ("🇬🇧 English", "english"),
    "uk": ("🇺🇦 Українська", "ukrainian"),
    "ru": ("🇷🇺 Русский", "russian"),
    "pl": ("🇵🇱 Polski", "polish"),
    "de": ("🇩🇪 Deutsch", "german"),
    "es": ("🇪🇸 Español", "spanish"),
    "fr": ("🇫🇷 Français", "french"),
    "kk": ("🇰🇿 Қазақша", "kazakh"),
    "uz": ("🇺🇿 O'zbekcha", "uzbek")
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем клавиатуру с кнопками (по 3 штуки в ряду)
    keyboard = []
    row = []
    for code, (label, _) in LANGUAGES.items():
        # В callback_data зашиваем префикс 'tr_' и код языка (например, 'tr_en')
        row.append(InlineKeyboardButton(label, callback_data=f"tr_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Привет! Я бот-переводчик с кнопками.\n"
        "Сделай реплай (ответ) на нужное сообщение и выбери язык на клавиатуре ниже:",
        reply_markup=reply_markup
    )

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Проверяем, что нажата именно наша кнопка перевода
    if not query.data.startswith("tr_"):
        return

    code = query.data.split("_")[1]
    if code not in LANGUAGES:
        return

    message = query.message.reply_to_message
    if not message or not message.text:
        await query.edit_message_text("Ошибка: исходное сообщение не найдено или оно пустое.")
        return

    target_lang = LANGUAGES[code][1]
    lang_label = LANGUAGES[code][0]

    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(message.text)
        
        # Редактируем сообщение с кнопками на готовый перевод
        await query.edit_message_text(
            f"🌐 <b>Перевод ({lang_label}):</b>\n{translated}",
            parse_mode="HTML"
        )
    except Exception as e:
        await query.edit_message_text(f"Ошибка при переводе: {e}")

if __name__ == '__main__':
    if not TOKEN:
        print("Ошибка: BOT_TOKEN не найден!")
    else:
        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        # Обработчик нажатий на инлайн-кнопки
        application.add_handler(CallbackQueryHandler(button_handler))

        print("Бот-переводчик с кнопками успешно запущен!")
        application.run_polling()
    
