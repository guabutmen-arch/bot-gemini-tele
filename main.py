import os
import logging
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler

logging.basicConfig(level=logging.INFO)

# Server untuk Koyeb agar tetap Healthy
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

def run_health():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

# Inisialisasi Gemini
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Siap! Bot AI sudah aktif. Silakan tanya apa saja.")

async def handle_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.text: return
    try:
        # Menggunakan model paling stabil
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=update.message.text
        )
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
    
    print("BOT JALAN...")
    app.run_polling(drop_pending_updates=True)
