import os
import threading
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(level=logging.INFO)

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot OK")

def run_health():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

# Inisialisasi Gemini Client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    try:
        # GANTI KE 1.5-FLASH (KUOTA LEBIH BANYAK)
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=update.message.text
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        # Jika error kuota muncul lagi, bot akan memberitahu
        if "429" in str(e):
            await update.message.reply_text("Duh, kuota gratis Google lagi habis. Coba lagi 1 menit lagi ya!")
        else:
            await update.message.reply_text(f"Ada kendala: {str(e)}")

if __name__ == '__main__':
    threading.Thread(target=run_health, daemon=True).start()
    token = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    logging.info("BOT AKTIF!")
    app.run_polling(drop_pending_updates=True)
