import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# --- 1. KONFIGURASI API ---
# Kode ini mengambil kunci dari 'Environment Variables' di server nanti
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Setup Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
# Menggunakan Gemini 1.5 Flash (Gratis, Cepat, Bisa Baca PDF/Gambar)
model = genai.GenerativeModel("gemini-1.5-flash")

# Setup Logging (untuk melihat jika ada error)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message
    chat_id = user_msg.chat_id
    
    try:
        # A. JIKA PESAN BERUPA TEKS
        if user_msg.text:
            response = model.generate_content(user_msg.text)
            await user_msg.reply_text(response.text)

        # B. JIKA PESAN BERUPA GAMBAR
        elif user_msg.photo:
            await user_msg.reply_text("Sedang menganalisis gambar... 🖼️")
            photo_file = await user_msg.photo[-1].get_file()
            path = f"{chat_id}_img.jpg"
            await photo_file.download_to_drive(path)
            
            sample_file = genai.upload_file(path=path)
            response = model.generate_content([sample_file, "Jelaskan gambar ini"])
            await user_msg.reply_text(response.text)
            os.remove(path)

        # C. JIKA PESAN BERUPA PDF
        elif user_msg.document and user_msg.document.mime_type == 'application/pdf':
            await user_msg.reply_text("Sedang membaca dokumen PDF... 📄")
            pdf_file = await user_msg.document.get_file()
            path = f"{chat_id}_doc.pdf"
            await pdf_file.download_to_drive(path)
            
            sample_pdf = genai.upload_file(path=path, mime_type="application/pdf")
            response = model.generate_content([sample_pdf, "Ringkas isi PDF ini"])
            await user_msg.reply_text(response.text)
            os.remove(path)

    except Exception as e:
        await user_msg.reply_text(f"Waduh, ada error nih: {str(e)}")

if __name__ == '__main__':
    # Membangun aplikasi bot
    if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
        print("Error: TOKEN atau API KEY belum diisi di Environment Variables!")
    else:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        app.add_handler(MessageHandler(filters.ALL, handle_message))
        print("Bot Gemini sudah aktif! Silahkan chat di Telegram.")
        app.run_polling()
