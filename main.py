import telebot
import google.generativeai as genai
import os
import PyPDF2
from pptx import Presentation
from pdf2image import convert_from_path
from PIL import Image

# Şifreleri doğrudan koda yazmıyoruz, Railway Variables bölümünden çekiyoruz
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# Hızlı ve vizyon yeteneği olan modeli seçiyoruz
model = genai.GenerativeModel('gemini-1.5-flash')

# Bota /start yazıldığında verilecek cevap
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Selam Haşmetli Taha! Haziran'daki mezuniyetine ve KPSS hedeflerine giden yolda kişisel tıp ve acil yardım asistanın emrinde. Sınav notu çıkarmam için bana PDF veya PPTX (slayt) gönder.")

# PDF veya PPTX geldiğinde çalışacak ana kod
@bot.message_handler(content_types=['document'])
def handle_docs(message):
    try:
        file_name = message.document.file_name
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Yapay Zekaya Verilen Kalıcı Uzmanlık Talimatı
        saglik_talimati = "Sen uzman bir paramedik eğitmeni ve KPSS tıbbi bilimler uzmanısın. Gönderilen bu içerikten anatomi, fizyoloji ve acil bakım gibi konularda sınavda çıkabilecek en kritik noktaları, terimleri ve hap bilgileri maddeler halinde çıkar. Karşındaki öğrencinin hedefi atanmak için 95 üstü puan almak, özetlerini bu ciddiyetle hazırla!"

        # EĞER DOSYA PPTX (SLAYT) İSE:
        if file_name.endswith('.pptx'):
            bot.reply_to(message, "Slayt geldi kanka! Hemen okuyup paramedik notlarını çıkarıyorum...")
            gecici_dosya = "gecici_sunum.pptx"
            with open(gecici_dosya, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            # Slayt içindeki yazıları çekiyoruz
            prs = Presentation(gecici_dosya)
            metin = ""
            for slide in prs.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text"):
                        metin += shape.text + "\n"
                        
            # Yapay zekaya özetletiyoruz
            response = model.generate_content(f"{saglik_talimati}\n\nİçerik: {metin[:15000]}")
            bot.reply_to(message, response.text)
            os.remove(gecici_dosya)

        # EĞER DOSYA PDF İSE:
        elif file_name.endswith('.pdf'):
            bot.reply_to(message, "PDF alındı kanka! Belgeyi inceliyorum...")
            gecici_dosya = "gecici_belge.pdf"
            with open(gecici_dosya, 'wb') as new_file:
                new_file.write(downloaded_file)
            
            # 1inci Aşama: Normal metin olarak okumayı dene
            metin = ""
            with open(gecici_dosya, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        metin += extracted + "\n"
            
            # 2nci Aşama: Eğer okunan metin çok kısaysa (Taranmış belge veya fotoğrafsa)
            if len(metin.strip()) < 50:
                bot.reply_to(message, "Bu PDF resim formatında kanka, görüntü işleme (OCR) ile okuyup not çıkarıyorum...")
