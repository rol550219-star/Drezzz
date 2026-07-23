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
        await update.message.reply_text("сделай реплей на комментарий и напиши /tr!")
        return

    keyboard = []
    row = []
    for code, (label, _) in LANGUAGES.items():
        row.append(InlineKeyboardButton(label, callback_data=f"tr_{code}"))
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Виводимо меню вибору мови у відповідь на команду /tr
    await update.message.reply_text(
        "Выбери язык для перевода:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not query.data.startswith("tr_"):
        return

    code = query.data.split("_")[1]
    if code not in LANGUAGES:
        return

    # ОТУТ ГОЛОВНА ЗМІНА: беремо текст з повідомлення, НА ЯКЕ зробили реплай
    original_message = query.message.reply_to_message.reply_to_message
    
    if not original_message or not original_message.text:
        await query.edit_message_text("Ошибка")
        return

    target_lang = LANGUAGES[code][1]
    lang_label = LANGUAGES[code][0]

    try:
        translated = GoogleTranslator(source='auto', target=target_lang).translate(original_message.text)
        await query.edit_message_text(
            f"🌐 <b>Переклад ({lang_label}):</b>\n{translated}",
            parse_mode="HTML"
        )
    except Exception as e:
        await query.edit_message_text(f"Помилка при перекладі: {e}")

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

        print("Бот-переводчик с кнопками успешно запущен!")
        application.run_polling()
        
