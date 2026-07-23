import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
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
    "en": "english",
    "uk": "ukrainian",
    "ru": "russian",
    "pl": "polish",
    "de": "german",
    "es": "spanish",
    "fr": "french",
    "kk": "kazakh",
    "uz": "uzbek"
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот-переводчик.\n"
        "Сделай реплай на сообщение другого человека и напиши код языка (например: `ru`, `en`, `kk`, `uz`, `uk`), чтобы перевести его.",
        parse_mode="Markdown"
    )

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # Проверяем, есть ли реплай на сообщение другого человека
    if not message.reply_to_message or not message.reply_to_message.text:
        return

    # Получаем текст команды (например, 'ru' из сообщения или '/ru')
    text_input = message.text.strip().lower().lstrip('/')

    if text_input not in LANGUAGES:
        return  # Если это не код языка, ничего не делаем

    # Текст того сообщения, НА КОТОРОЕ сделали реплай
    original_text = message.reply_to_message.text
    target_lang = LANGUAGES[text_input]

    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(original_text)
        await message.reply_text(
            f"🌐 <b>Перевод ({text_input.upper()}):</b>\n{translated}",
            parse_mode="HTML"
        )
    except Exception as e:
        await message.reply_text(f"Ошибка при переводе: {e}")

if __name__ == '__main__':
    if not TOKEN:
        print("Ошибка: BOT_TOKEN не найден!")
    else:
        t = Thread(target=run_web_server)
        t.daemon = True
        t.start()

        application = Application.builder().token(TOKEN).build()

        application.add_handler(CommandHandler("start", start))
        # Перехватываем любые сообщения, состоящие из двух букв (коды языков вроде ru, en, kk, uz)
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^/?[a-zA-Z]{2}$"), translate_message))

        print("Бот-переводчик запущен и работает идеально!")
        application.run_polling()
    
