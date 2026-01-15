import os, threading, logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Log agar terlihat di Koyeb
logging.basicConfig(level=logging.INFO)

class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"Bot OK")

def run_health():
    port = int(os.environ.get("PORT", 8000))
    HTTPServer(('0.0.0.0', port), HealthCheck).serve_forever()

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    try:
        # Gunakan 'models/gemini-pro' atau 'gemini-1.5-flash-latest' untuk stabilitas
        model = genai.GenerativeModel("gemini-pro") 
        response = model.generate_content(update.message.text)
        await update.message.reply_text(response.text)
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        # Coba cadangan jika gemini-pro gagal
        try:
            model = genai.GenerativeModel("gemini-1.5-flash-latest")
            response = model.generate_content(update.message.text)
            await update.message.reply_text(response.text)
        except:
            await update.message.reply_text("Maaf, server AI sedang sibuk.")

if __name__ == '__main__':
    threading.Thread(target=run_health, daemon=True).start()
    
    # Konfigurasi
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    token = os.environ.get("TELEGRAM_TOKEN")
    
    # Bangun Bot
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), chat))
    
    logging.info("BOT SUDAH AKTIF!")
    # drop_pending_updates=True untuk mengatasi error 'Conflict'
    app.run_polling(drop_pending_updates=True)
