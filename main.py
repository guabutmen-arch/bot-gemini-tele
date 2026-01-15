import os, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Agar Koyeb tidak mematikan bot (Port 8000)
class HealthCheck(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

def run_health():
    HTTPServer(('0.0.0.0', int(os.environ.get("PORT", 8000))), HealthCheck).serve_forever()

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ini fungsi balas chat
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(update.message.text)
    await update.message.reply_text(response.text)

if __name__ == '__main__':
    threading.Thread(target=run_health, daemon=True).start()
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    app = ApplicationBuilder().token(os.environ.get("TELEGRAM_TOKEN")).build()
    app.add_handler(MessageHandler(filters.TEXT, chat))
    print("BOT SUDAH NYALA!")
    app.run_polling()
