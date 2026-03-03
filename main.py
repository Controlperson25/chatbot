import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiohttp import web

# ================= НАСТРОЙКИ =================
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("❌ TOKEN не найден в переменных окружения!")

GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID")
if not GROUP_CHAT_ID:
    raise ValueError("❌ GROUP_CHAT_ID не найден в переменных окружения!")
GROUP_CHAT_ID = int(GROUP_CHAT_ID)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ================= СОСТОЯНИЯ =================
class Survey(StatesGroup):
    language = State()
    faculty = State()
    course = State()
    age = State()
    problem = State()
    more_info_decision = State()
    more_info_text = State()
    help_type = State()
    meeting_person = State()
    contact_method = State()
    contact_info = State()

# ================= ТЕКСТЫ НА ДВУХ ЯЗЫКАХ =================
texts = {
    "ru": {
        "choose_lang": "Выберите язык / Tilni tanlang",
        "choose_faculty": "Выберите Ваш факультет",
        "faculties": ["Уголовное правосудие", "Международное право и сравнительное правосудие", "Публичное право", "Частное право", "Государственное управление", "Магистратура"],
        "choose_course": "Выберите Ваш курс",
        "courses": ["1 курс", "2 курс", "3 курс", "4 курс"],
        "choose_age": "Укажите Ваш возраст",
        "ages": ["17-18", "19-20", "21-22", "23-24", "25+"],
        "problem": "В чём Ваша проблема?",
        "problems": ["Сталкинг (приставание)", "Харрасмент", "Другое"],
        "more_info": "Хотите ещё о чём-нибудь сообщить?",
        "more_info_prompt": "Пожалуйста, напишите дополнительную информацию:",
        "yes_no": ["Да", "Нет"],
        "help_type": "Какой вид помощи Вам требуется?",
        "help_options": ["Личная встреча", "Онлайн консультация"],
        "meeting_person": "С кем хотите встретиться?",
        "persons": ["с Ректором", "с 1-ым Проректором", "с Психологом", "с Хайдаровой Умидой Пулатовной"],
        "contact_method": "Как с Вами связаться?",
        "contact_options": ["Номер телефона", "Электронная почта", "Через Telegram или Instagram"],
        "contact_input": "Пожалуйста, введите ваши контактные данные:",
        "thank_you": "✅ Ваше обращение принято.\nВ ближайшее время мы свяжемся с Вами для оказания помощи."
    },
    "uz": {
        "choose_lang": "Tilni tanlang / Выберите язык",
        "choose_faculty": "Fakultetingizni tanlang",
        "faculties": ["Jinoyat adliyati", "Xalqaro huquq va qiyosiy adliyat", "Ommaviy huquq", "Xususiy huquq", "Davlat boshqaruvi", "Magistratura"],
        "choose_course": "Kursingizni tanlang",
        "courses": ["1-kurs", "2-kurs", "3-kurs", "4-kurs"],
        "choose_age": "Yoshingizni belgilang",
        "ages": ["17-18 yosh", "19-20 yosh", "21-22 yosh", "23-24 yosh", "25+ yosh"],
        "problem": "Muammoingiz nima?",
        "problems": ["Stalking (ta'qib qilish)", "Harassment (bezovta qilish)", "Boshqa"],
        "more_info": "Yana biror narsa haqida xabar bermoqchimisiz?",
        "more_info_prompt": "Iltimos, qo'shimcha ma'lumotni kiriting:",
        "yes_no": ["Ha", "Yo'q"],
        "help_type": "Sizga qanday yordam kerak?",
        "help_options": ["Shaxsiy uchrashuv", "Onlayn maslahat"],
        "meeting_person": "Kim bilan uchrashmoqchisiz?",
        "persons": ["Rektor bilan", "1-prorektor bilan", "Psixolog bilan", "Xaydarova Umida Pulatovna bilan"],
        "contact_method": "Siz bilan qanday aloqa qilaylik?",
        "contact_options": ["Telefon raqami", "Elektron pochta", "Telegram yoki Instagram orqali"],
        "contact_input": "Iltimos, kontakt ma'lumotlaringizni kiriting:",
        "thank_you": "✅ Sizning murojaatingiz qabul qilindi.\nYaqin vaqtda siz bilan bog'lanamiz va yordam ko'rsatamiz."
    }
}

# ================= ВЕБ-СЕРВЕР ДЛЯ RENDER (чтобы не засыпал) =================
async def health_check(request):
    """Эндпоинт для проверки работоспособности бота (для UptimeRobot)"""
    return web.Response(text="✅ Bot is running! Бот работает!")

async def start_web_server():
    """Запуск веб-сервера на порту, который предоставляет Render"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    # Render предоставляет порт через переменную PORT
    port = int(os.getenv('PORT', 8080))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"🌐 Веб-сервер запущен на порту {port}")

# ================= КЛАВИАТУРА =================
def get_keyboard(items: list, prefix: str) -> InlineKeyboardMarkup:
    kb = [[InlineKeyboardButton(text=item, callback_data=f"{prefix}_{item}")] for item in items]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# ================= /start =================
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(Survey.language)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")],
        [InlineKeyboardButton(text="O'zbekcha", callback_data="lang_uz")]
    ])
    await message.answer(
        "🇷🇺 Русский / 🇺🇿 O'zbekcha\n\nВыберите язык / Tilni tanlang",
        reply_markup=kb
    )

# ================= ЯЗЫК =================
@dp.callback_query(F.data.startswith("lang_"))
async def process_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await state.update_data(language=lang)
    await state.set_state(Survey.faculty)
    await callback.answer()
    await callback.message.edit_text(
        texts[lang]["choose_faculty"],
        reply_markup=get_keyboard(texts[lang]["faculties"], "faculty")
    )

# ================= ФАКУЛЬТЕТ =================
@dp.callback_query(F.data.startswith("faculty_"))
async def process_faculty(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    faculty = callback.data.split("_", 1)[1]
    await state.update_data(faculty=faculty)
    await state.set_state(Survey.course)
    await callback.answer()
    await callback.message.edit_text(
        texts[lang]["choose_course"],
        reply_markup=get_keyboard(texts[lang]["courses"], "course")
    )

# ================= КУРС =================
@dp.callback_query(F.data.startswith("course_"))
async def process_course(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    course = callback.data.split("_", 1)[1]
    await state.update_data(course=course)
    await state.set_state(Survey.age)
    await callback.answer()
    await callback.message.edit_text(
        texts[lang]["choose_age"],
        reply_markup=get_keyboard(texts[lang]["ages"], "age")
    )

# ================= ВОЗРАСТ =================
@dp.callback_query(F.data.startswith("age_"))
async def process_age(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    age = callback.data.split("_", 1)[1]
    await state.update_data(age=age)
    await state.set_state(Survey.problem)
    await callback.answer()
    await callback.message.edit_text(
        texts[lang]["problem"],
        reply_markup=get_keyboard(texts[lang]["problems"], "problem")
    )

# ================= ПРОБЛЕМА =================
@dp.callback_query(F.data.startswith("problem_"))
async def process_problem(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    problem = callback.data.split("_", 1)[1]
    await state.update_data(problem=problem)
    await state.set_state(Survey.more_info_decision)
    await callback.answer()
    await callback.message.edit_text(
        texts[lang]["more_info"],
        reply_markup=get_keyboard(texts[lang]["yes_no"], "more")
    )

# ================= ДОП. ИНФОРМАЦИЯ (Да/Нет) =================
@dp.callback_query(F.data.startswith("more_"))
async def process_more_decision(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    decision = callback.data.split("_", 1)[1]
    await state.update_data(more_info_decision=decision)
    await callback.answer()

    if decision == texts[lang]["yes_no"][0]:  # Да / Ha
        await state.set_state(Survey.more_info_text)
        await callback.message.edit_text(texts[lang]["more_info_prompt"])
    else:
        await state.update_data(more_info="—")
        await state.set_state(Survey.help_type)
        await callback.message.edit_text(
            texts[lang]["help_type"],
            reply_markup=get_keyboard(texts[lang]["help_options"], "help")
        )

# ================= ТЕКСТ ДОП. ИНФОРМАЦИИ =================
@dp.message(Survey.more_info_text)
async def process_more_text(message: types.Message, state: FSMContext):
    await state.update_data(more_info=message.text)
    data = await state.get_data()
    lang = data["language"]
    await state.set_state(Survey.help_type)
    await message.answer(
        texts[lang]["help_type"],
        reply_markup=get_keyboard(texts[lang]["help_options"], "help")
    )

# ================= ВИД ПОМОЩИ =================
@dp.callback_query(F.data.startswith("help_"))
async def process_help_type(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    help_type = callback.data.split("_", 1)[1]
    await state.update_data(help_type=help_type)
    await callback.answer()

    if help_type == texts[lang]["help_options"][0]:  # Личная встреча / Shaxsiy uchrashuv
        await state.set_state(Survey.meeting_person)
        await callback.message.edit_text(
            texts[lang]["meeting_person"],
            reply_markup=get_keyboard(texts[lang]["persons"], "person")
        )
    else:
        await state.update_data(meeting_person="—")
        await state.set_state(Survey.contact_method)
        await callback.message.edit_text(
            texts[lang]["contact_method"],
            reply_markup=get_keyboard(texts[lang]["contact_options"], "contact")
        )

# ================= КТО ИЗ РУКОВОДСТВА =================
@dp.callback_query(F.data.startswith("person_"))
async def process_meeting_person(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    person = callback.data.split("_", 1)[1]
    await state.update_data(meeting_person=person)
    await state.set_state(Survey.contact_method)
    await callback.answer()
    await callback.message.edit_text(
        texts[lang]["contact_method"],
        reply_markup=get_keyboard(texts[lang]["contact_options"], "contact")
    )

# ================= СПОСОБ СВЯЗИ =================
@dp.callback_query(F.data.startswith("contact_"))
async def process_contact_method(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["language"]
    method = callback.data.split("_", 1)[1]
    await state.update_data(contact_method=method)
    await state.set_state(Survey.contact_info)
    await callback.answer()
    await callback.message.edit_text(texts[lang]["contact_input"])

# ================= ВВОД КОНТАКТНЫХ ДАННЫХ =================
@dp.message(Survey.contact_info)
async def process_contact_info(message: types.Message, state: FSMContext):
    await state.update_data(contact_info=message.text)
    data = await state.get_data()
    lang = data["language"]

    # Собираем итоговую анкету
    more_info = data.get("more_info", "—")
    meeting_person = data.get("meeting_person", "—")

    final_text = f"""🆕 НОВАЯ АНКЕТА / YANGI ANKETA

🌐 Язык / Til: {'Русский' if lang == 'ru' else "O'zbekcha"}
🏛 Факультет / Fakultet: {data.get('faculty')}
📚 Курс / Kurs: {data.get('course')}
🎂 Возраст / Yosh: {data.get('age')}
❓ Проблема / Muammo: {data.get('problem')}
📝 Дополнительно: {more_info}
🆘 Вид помощи / Yordam turi: {data.get('help_type')}
👤 Встреча: {meeting_person}
📞 Контакт: {data.get('contact_method')} — {data.get('contact_info')}
"""

    # Отправляем в группу
    try:
        await bot.send_message(GROUP_CHAT_ID, final_text)
        print("✅ Анкета отправлена в группу")
    except Exception as e:
        print(f"❌ Ошибка отправки в группу: {e}")

    # Спасибо пользователю
    await message.answer(texts[lang]["thank_you"])
    await state.clear()

# ================= ЗАПУСК БОТА =================
async def main():
    print("="*50)
    print("🤖 Telegram Bot для обращений студентов")
    print("="*50)
    print(f"✅ TOKEN: {TOKEN[:10]}...")
    print(f"✅ GROUP_CHAT_ID: {GROUP_CHAT_ID}")
    print("="*50)
    
    # Запускаем веб-сервер (чтобы Render не усыплял бота)
    await start_web_server()
    
    # Запускаем бота
    print("🚀 Бот запущен и работает 24/7...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
