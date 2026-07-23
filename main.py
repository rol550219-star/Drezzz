import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from deep_translator import GoogleTranslator

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Словарь доступных языков
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

async def translate_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.text:
        await update.message.reply_text("Сделай реплай на сообщение и напиши /tr!")
        return

    original_text = update.message.reply_to_message.text
    safe_text = original_text[:30].replace("_", " ")

    keyboard = []
    row = []
    for code, (label, _) in LANGUAGES.items():
        callback_data = f"tr_{code}_{safe_text}"
        row.append(InlineKeyboardButton(label, callback_data=callback_data))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Выбери язык для перевода:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data_parts = query.data.split("_", 2)
    if len(data_parts) < 2 or data_parts[0] != "tr":
        return

    code = data_parts[1]
    if code not in LANGUAGES:
        return

    bot_message = query.message
    if bot_message.reply_to_message and bot_message.reply_to_message.reply_to_message:
        original_text = bot_message.reply_to_message.reply_to_message.text
    else:
        original_text = data_parts[2] if len(data_parts) > 2 else ""

    if not original_text:
        await query.edit_message_text("Ошибка: текст для перевода не найден.")
        return

    target_lang = LANGUAGES[code][1]
    lang_label = LANGUAGES[code][0]

    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        
        # Пытаемся определить язык
        detected_lang = None
        try:
            detected_lang = translator.detect(original_text)
        except Exception:
            pass

        # Если язык совпадает с целевым — выводим предупреждение
        if detected_lang and (detected_lang.lower() == code.lower() or detected_lang.lower() == target_lang.lower()):
            await query.edit_message_text(f"⚠️ Этот текст уже написан на языке: {lang_label}")
            return

        translated = translator.translate(original_text)
        
        if not translated or translated.strip().lower() == original_text.strip().lower():
            await query.edit_message_text(f"⚠️ Этот текст уже на языке {lang_label}!")
            return

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
        t = Thread(target=run_web_server)
        t.daemon = True
        t.start()

        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("tr", translate_menu))
        application.add_handler(CallbackQueryHandler(button_handler))

        print("Бот-переводчик успешно запущен!")
        application.run_polling()
        
