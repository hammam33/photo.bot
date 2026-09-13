import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent, Task, Crew, Process

# إعداد تسجبل البيانات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# إعداد نموذج Gemini Flash
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    verbose=True,
    temperature=0.7,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# تعاريف وكلاء الشركة (Agents)
orchestrator = Agent(
    role="Chief Operating Officer",
    goal="فهم كافة تفاصيل المشروع وتوجيه وإدارة فريق الإنتاج الرقمي.",
    backstory="أنت مدير عمليات ينظم عمل الأيجلنتس ويناقش العميل في المتطلبات للوصول لأفضل نتيجة.",
    llm=llm,
    allow_delegation=True
)

strategist = Agent(
    role="Business Strategist",
    goal="تحليل السوق وتحديد الجمهور المستهدف والزوايا التنافسية.",
    backstory="خبير استراتيجي يحلل المنافسين ودوافع المستهلك بدقة.",
    llm=llm
)

copywriter = Agent(
    role="Creative Copywriter",
    goal="صياغة النصوص الإعلانية والسكريبتات السينمائية.",
    backstory="كاتب إبداعي متخصص في تحويل الأفكار إلى رسائل تسويقية جذابة ومؤثرة.",
    llm=llm
)

art_director = Agent(
    role="Art Director & Prompt Engineer",
    goal="تحديد المفهوم البصري وكتابة أوامر توليد الصور والفيديوهات.",
    backstory="مخرج فني خبير بالإضاءة، الألوان، والتصوير السينمائي.",
    llm=llm
)

# أوامر وبوت تيليجرام
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أهلاً بك! أنا مدير العمليات التنفيذي (COO). أرسل لي تفاصيل مشروعك الجديد لنبدأ العمل مع الفريق فوراً!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    project_brief = update.message.text
    await update.message.reply_text("تم الاستلام! يدرس الفريق المشروع ويجري النقاش بين الوكلاء الآن... (قد يستغرق ذلك دقيقة)")

    try:
        task1 = Task(description=f"تحليل المشروع ودراسة السوق: {project_brief}", expected_output="تقرير أبحاث واستراتيجية", agent=strategist)
        task2 = Task(description="كتابة نصوص إعلانية وسكريبت سينمائي للحملة بناءً على التحليل", expected_output="نصوص إعلانية وسكريبت", agent=copywriter)
        task3 = Task(description="تحديد الهوية البصرية ورسم أوامر التوليد السينمائي (Prompts)", expected_output="دليل المفهوم البصري والـ Prompts", agent=art_director)
        task4 = Task(description="مراجعة وتنسيق كافة نتائج الوكلاء في تقرير تنفيذي شامل ومُنظم", expected_output="التقرير التنسيقي النهائي", agent=orchestrator)

        agency_crew = Crew(
            agents=[orchestrator, strategist, copywriter, art_director],
            tasks=[task1, task2, task3, task4],
            process=Process.sequential
        )
        
        result = agency_crew.kickoff()
        output = str(result)

        # مراعاة حد الرسائل في تيليجرام
        if len(output) > 4000:
            for i in range(0, len(output), 4000):
                await update.message.reply_text(output[i:i+4000])
        else:
            await update.message.reply_text(output)
            
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء تنفيذ الطلب: {e}")

if __name__ == '__main__':
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable is missing!")
        exit(1)

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot is running...")
    app.run_polling()
