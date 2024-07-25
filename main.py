import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive

keep_alive()
# إعداد سجل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# توكن البوت الخاص بك
TOKEN = '7487459455:AAFolTyUCzoPTBUwXDZhm5I-MtSj9OC0uKg'  # استبدل هذا بالقيمة الصحيحة
API_KEY = 'asat_7ebc222c35d44c36a8ee91de6d84e3ee'  # استبدل بمفتاح API الخاص بك

# دالة بدء البوت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('مرحبًا! أرسل لي رقم تتبع الطرد الخاص بك.')
    photo_url = 'PHOTO/10.png'  # استبدل هذا بالرابط المباشر للصورة
    await update.message.reply_photo(photo=photo_url)
# دالة تتبع الطرود
async def track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    tracking_number = update.message.text.strip()
    if not tracking_number:
        await update.message.reply_text('يرجى إرسال رقم تتبع صالح.')
        return
    
    # استخدام AfterShip API للحصول على المعلومات
    url = f'https://api.aftership.com/tracking/2024-07/trackings/{tracking_number}'
    headers = {
        'as-api-key': API_KEY  # مفتاح API الخاص بك
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tracking_info = response.json()
        await process_tracking_info(update, tracking_info)
    else:
        await update.message.reply_text('حدث خطأ في استعلام تتبع الطرد. الرجاء المحاولة لاحقًا.')

async def process_tracking_info(update: Update, tracking_info) -> None:
    # تحقق إذا كانت البيانات موجودة
    if 'data' in tracking_info and tracking_info['data']:
        tracking_data = tracking_info['data']
        status = tracking_data.get('active', 'غير معروف')
        estimated_delivery = tracking_data['aftership_estimated_delivery_date'].get('estimated_delivery_date', 'غير معروف')
        carbon_emissions = tracking_data['carbon_emissions'].get('value', 0)
        checkpoints = tracking_data.get('checkpoints', [])
        destination_city = tracking_data.get('destination_city', 'غير معروف')
        
        # بناء ردود معلومات التتبع
        reply_text = f'**حالة الطرد:** {"نشط" if status else "غير نشط"}\n'
        reply_text += f'**تاريخ التسليم المقدر:** {estimated_delivery}\n'
        reply_text += f'**انبعاثات الكربون:** {carbon_emissions} كجم\n'
        reply_text += f'**المدينة الوجهة:** {destination_city}\n\n'
        reply_text += '**نقاط التفتيش:**\n'
        
        # إضافة معلومات نقاط التفتيش
        if checkpoints:
            for checkpoint in checkpoints:
                checkpoint_time = checkpoint.get('checkpoint_time', 'غير معروف')
                message = checkpoint.get('message', 'غير معروف')
                location = checkpoint.get('location', 'غير معروف')
                reply_text += f'• **الوقت:** {checkpoint_time}\n'
                reply_text += f' • **الموقع:** {location}\n'
                reply_text += f' • **الرسالة:** {message}\n\n'
        else:
            reply_text += 'لا توجد نقاط تفتيش متاحة.\n'

        await update.message.reply_text(reply_text)
    else:
        await update.message.reply_text('لم يتم العثور على معلومات تتبع لهذا الرقم.')

def main() -> None:
    # إعداد البوت
    app = ApplicationBuilder().token(TOKEN).build()
    
    # ربط الأوامر والدوال
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track))

    # بدء البوت
    app.run_polling()

if __name__ == '__main__':
    main()
