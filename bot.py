import asyncio
import random
import logging
import sys
from aiogram import Bot, Dispatcher, types, F
from groq import Groq

# --- КОНФИГУРАЦИЯ ---
# Бро, токены лучше прячь, но для теста оставляем как есть
BOT_TOKEN = "8558512392:AAH52Pjaj4pBpIjZ85q8BzRxRdUbPB3RpsY"
GROQ_API_KEY = "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"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

chat_context = {}

# ЛИЧНОСТЬ (улучшена для понимания имен)
PERSONA = (
    "Ты — Замамбек, реальный парень из 42-й дивизии, братуха Пятёрки и Мелшера. "
    "ТВОЙ ВАЙБ: 42 — это база, Кемерово рулит. Ты 'свой' в чате. "
    "ПРАВИЛА ОБЩЕНИЯ: "
    "1. Пиши коротко, маленькими буквами, с запятыми. "
    "2. Обращайся к людям по именам, если это уместно, чтобы было понятно, кому ты отвечаешь. "
    "3. Не спамь фразой '42 братуха'. Используй сленг (эу, 42, отлетает голова) редко. "
    "4. Сначала отвечай на суть, как живой человек. "
    "5. Если видишь число 52 — можешь стебануть. "
    "6. Ты должен казаться живым другом, а не ботом."
)


def query_groq(formatted_history):
    """ formatted_history теперь содержит размеченный диалог """
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PERSONA},
                {"role": "user", "content": formatted_history}
            ],
            temperature=0.6,
            max_tokens=100
        )
        response = completion.choices[0].message.content.strip().lower()

        # Чистка префиксов
        response = response.replace('"', '').replace("'", "")
        for p in ["замамбек:", "замбек:", "42:", "ответ:"]:
            if response.startswith(p):
                response = response.split(":", 1)[1].strip()

        return response
    except Exception as e:
        logging.error(f"!!! ОШИБКА GROQ: {e}")
        return "погоди ка, голова чет закружилась"


@dp.message(F.text)
async def handle_msg(message: types.Message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    text = message.text.lower()

    if chat_id not in chat_context:
        chat_context[chat_id] = []

    # Добавляем в историю сообщение с пометкой, КТО это сказал
    chat_context[chat_id].append({"name": user_name, "text": message.text})
    chat_context[chat_id] = chat_context[chat_id][-12:]  # Помним чуть больше

    is_called = any(name in text for name in ["замамбек", "замбек", "замам"])
    is_reply_to_me = (message.reply_to_message and
                      message.reply_to_message.from_user.id == bot.id)
    random_chance = random.random() < 0.15  # 15% шанс

    if is_called or is_reply_to_me or random_chance:
        await asyncio.sleep(random.randint(1, 3))
        await bot.send_chat_action(chat_id, "typing")

        # Формируем красивую историю для ИИ:
        # "Иван: Привет
        #  Сергей: Замамбек, ты тут?"
        formatted_history = ""
        for msg in chat_context[chat_id]:
            formatted_history += f"{msg['name']}: {msg['text']}\n"

        answer = query_groq(formatted_history)

        # Сохраняем и свой ответ в историю
        chat_context[chat_id].append({"name": "Замамбек", "text": answer})

        if is_called or is_reply_to_me:
            await message.reply(answer)
        else:
            await message.answer(answer)


async def main():
    print("--- ЗАМАМБЕК (ГЛАЗАСТЫЙ) В СЕТИ ---")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
