import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# إعداد نموذج Gemini Flash
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# تعاريف أدوار الوكلاء
PROMPTS = {
    "strategist": "أنت خبير استراتيجيات تسويق وتحديد الجمهور المستهدف ودراسة المنافسين.",
    "copywriter": "أنت كاتب إبداعي متخصص في صياغة الإعلانات والسكريبتات السينمائية الجذابة.",
    "art_director": "أنت مخرج فني خبير بالإضاءة والألوان وكتابة أوامر توليد الصور والفيديو (Prompts)."
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أنا مدير العمليات التنفيذي (COO). أرسل لي تفاصيل مشروعك الجديد لنبدأ العمل مع الفريق فوراً!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    project_brief = update.message.text
    await update.message.reply_text("تم الاستلام! يدرس الفريق المشروع ويجري النقاش بين الوكلاء الآن... (قد يستغرق ذلك دقيقة)")

    try:
        # 1. تحليل الاستراتيجي
        strat_res = llm.invoke([
            SystemMessage(content=PROMPTS["strategist"]),
            HumanMessage(content=f"قم بإعداد استراتيجية تسويقية وتحديد الجمهور والمزايا التنافسية لـ: {project_brief}")
        ]).content

        # 2. كاتب النصوص
        copy_res = llm.invoke([
            SystemMessage(content=PROMPTS["copywriter"]),
            HumanMessage(content=f"بناءً على التحليل التالي:\n{strat_res}\n\nاكتب نصوصاً إعلانية وسكريبت إعلان سينمائي للمشروع.")
        ]).content

        # 3. المخرج الفني
        art_res = llm.invoke([
            SystemMessage(content=PROMPTS["art_director"]),
            HumanMessage(content=f"بناءً على السكريبت والتحليل:\n{copy_res}\n\nحدد المفهوم البصري وأوامر التوليد (Prompts) الخاصة بالإعلان.")
        ]).content

        # التقرير النهائي المنسق
        final_output = f"📋 **تقرير الوكالة الموحد للمشروع**\n\n" \
                       f"🎯 **1. الاستراتيجية والتحليل:**\n{strat_res}\n\n" \
                       f"✍️ **2. النصوص الإعلانية والسكريبت:**\n{copy_res}\n\n" \
                       f"🎨 **3. المفهوم البصري الـ Prompts:**\n{art_res}"

        # إرسال النتيجة مع مراعاة حد الرسائل
        if len(final_output) > 4000:
            for i in range(0, len(final_output), 4000):
                await update.message.reply_text(final_output[i:i+4000])
        else:
            await update.message.reply_text(final_output)

    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء تنفيذ الطلب: {e}")

if __name__ == '__main__':
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN is missing!")
        exit(1)

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("Bot is running...")
    app.run_polling()
