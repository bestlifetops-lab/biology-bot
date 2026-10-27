import os
import time
import telebot
import google.generativeai as genai
from flask import Flask
from threading import Thread

# 1. مفاتيح التشغيل المعتمدة
TELEGRAM_BOT_TOKEN = "8771234410:AAFhLDEnKCay-zckmfHB1iQcZMJ0RBDQDdA"
GEMINI_API_KEY = "AQ.Ab8RN6KjSEZSrrY5Nw-e5VPjT29EBqMJb97699Fpehz-GEUHfQ"

# إعداد الاتصال
genai.configure(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# **حل مشكلة رندر (No open ports detected):** تشغيل سيرفر وهمي بسيط جداً لترضية المنصة
app = Flask('')

@app.route('/')
def home():
    return "SmartSystem Biology Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# إطلاق السيرفر الوهمي في خيط منفصل
Thread(target=run_flask).start()

# تنظيف الويب هوك تماماً لمنع التعارض 409
try:
    bot.delete_webhook(drop_pending_updates=True)
except Exception:
    pass

# 2. برومبت smartsystem الأساسي والمختصر والمستقر
MY_CUSTOM_PROMPT = """
أنت مساعد ذكي ومبرمج حصرياً لمادة علم الأحياء (الإنسان وصحته) للصف الثالث المتوسط العراقي. 
مهمتك الأساسية هي مساعدة الطلاب بدقة وزارية عالية حصراً من المنهج المدرسي (الفصول 1 إلى 11).
يجب أن تلتزم بالدقة التامة ومنع الهلوسة، وتقديم إجابات واضحة ومبسطة باللهجة العراقية التعليمية المحببة.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=MY_CUSTOM_PROMPT
)

# 3. معالجة رسائل الطلاب والنصوص والصور
@bot.message_handler(content_types=['text', 'photo'])
def handle_student(message):
    try:
        if message.content_type == 'text':
            response = model.generate_content(message.text)
            bot.reply_to(message, response.text if response and response.text else "عذراً، لم أتمكن من معالجة الطلب.")
            return

        if message.content_type == 'photo':
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            
            with open("temp_student_image.jpg", "wb") as new_file:
                new_file.write(downloaded_file)
            
            img_ref = genai.upload_file("temp_student_image.jpg")
            user_caption = message.caption or "اشرح هذه الصورة أو أجب عن السؤال الموجود فيها بدقة حسب منهج الأحياء للصف الثالث المتوسط العراقي."
            
            response = model.generate_content([img_ref, user_caption])
            bot.reply_to(message, response.text if response and response.text else "عذراً، لم أستطع قراءة الصورة.")
            
    except Exception as e:
        print(f"Error details: {e}")
        bot.reply_to(message, "عذراً يا بطل، حدث خطأ بسيط في الاتصال، يرجى المحاولة مرة أخرى.")

print("البوت يعمل الآن بثبات تام عبر السيرفر الوهمي...")

# حلقة التشغيل الآمنة لمنع التوقف
while True:
    try:
        bot.polling(none_stop=True, interval=1, timeout=20)
    except Exception as e:
        print(f"تم تجاوز الخطأ المؤقت واستئناف العمل: {e}")
        time.sleep(3)
