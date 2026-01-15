import os
import logging
import threading
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)

# Server Penjaga Port 8000 (Wajib untuk Koyeb)
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot Gemini 3 Aktif")

def run_health():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

# Konfigurasi API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Bot Gemini 3 Flash sudah aktif. Silakan tanya apa saja!")

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: return
    try:
        # MENGGUNAKAN MODEL DARI SCREENSHOT KAMU
        model = genai.GenerativeModel('gemini-3-flash-preview')
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Error: {e}")
        await update.message.reply_text(f"Ada kendala: {str(e)}")

if __name__ == '__main__':
    threading.Thread(target=run_health, daemon=True).start()
    token = os.environ.get("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_chat))
    
    print("BOT JALAN DENGAN GEMINI 3 FLASH...")
    app.run_polling(drop_pending_updates=True)
