import os
import threading
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Setup Logging
logging.basicConfig(level=logging.INFO)

# Server Penjaga Port 8000 untuk Koyeb
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot OK")

def run_health():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

# Inisialisasi Gemini Client menggunakan variabel lingkungan GEMINI_API_KEY
client = genai.Client()

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    try:
        # Menggunakan model terbaru sesuai panduanmu
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=update.message.text
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        await update.message.reply_text(f"Pesan dari Google: {str(e)}")

if __name__ == '__main__':
    # Jalankan server kesehatan
    threading.Thread(target=run_health, daemon=True).start()
    
    # Jalankan Bot Telegram
    token = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    logging.info("BOT AKTIF DENGAN SDK BARU!")
    app.run_polling(drop_pending_updates=True)
