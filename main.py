import telebot
import google.generativeai as genai
import os
import PyPDF2
from pptx import Presentation
from pdf2image import convert_from_path
from PIL import Image

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# İŞTE GÜNCELLEDİĞİMİZ SATIR BURASI:
model = genai.GenerativeModel('gemini-1.5-flash-latest')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Selam Haşmetli Taha! Sınav notu çıkarmam için bana PDF veya PPTX (slayt) gönder.")

@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        file_name = message.document.file_name
        
