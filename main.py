import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types, F
from groq import Groq

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "8558512392:AAH52Pjaj4pBpIjZ85q8BzRxRdUbPB3RpsY"
GROQ_API_KEY = "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"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
client = Groq(api_key=GROQ_API_KEY)

logging.basicConfig(level=logging.INFO)

chat_context = {}

# ОБНОВЛЕННАЯ ЛИЧНОСТЬ
PERSONA = (
    "Ты — Замамбек, реальный парень 25 лет. "
    "ПРАВИЛА ОТВЕТА: "
    "1. Пиши максимально коротко (одна короткая фраза или одно предложение). "
    "2. Никогда не пиши свое имя 'замамбек:' перед ответом. "
    "3. Пиши только маленькими буквами, ставь запятые, где нужно. "
    "4. Твой стиль: ироничный, дерзкий, уверенный. "
    "5. Ты человек. На обвинения в том, что ты бот, отвечай коротко и хлестко."
)


def query_groq(prompt_history):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PERSONA},
                {"role": "user", "content": prompt_history}
            ],
            temperature=0.6,  # Еще чуть ниже, чтобы был четче
            max_tokens=100
        )
        response = completion.choices[0].message.content.strip().lower()

        # Очистка: убираем кавычки и возможные префиксы "замамбек:"
        response = response.replace('"', '').replace("'", "")
        if response.startswith("замамбек:"):
            response = response.replace("замамбек:", "").strip()
        if response.startswith("замбек:"):
            response = response.replace("замбек:", "").strip()

        return response
    except Exception as e:
        print(f"!!! ОШИБКА GROQ: {e}")
        return "интернет чет моросит"


@dp.message(F.text)
async def handle_msg(message: types.Message):
    chat_id = message.chat.id
    user_name = message.from_user.first_name
    text = message.text.lower()

    if chat_id not in chat_context:
        chat_context[chat_id] = []

    chat_context[chat_id].append(f"{user_name}: {message.text}")
    chat_context[chat_id] = chat_context[chat_id][-10:]

    is_called = any(name in text for name in ["замамбек", "замбек", "замам"])
    is_reply_to_me = (message.reply_to_message and
                      message.reply_to_message.from_user.id == bot.id)
    random_chance = random.random() < 0.12

    if is_called or is_reply_to_me or random_chance:
        # Имитация чтения короткого сообщения
        await asyncio.sleep(random.randint(1, 3))
        await bot.send_chat_action(chat_id, "typing")

        full_history = "\n".join(chat_context[chat_id])
        answer = query_groq(full_history)

        chat_context[chat_id].append(f"Замамбек: {answer}")

        if is_called or is_reply_to_me:
            await message.reply(answer)
        else:
            await message.answer(answer)


async def main():
    print("--- ЗАМАМБЕК В СЕТИ (БЕЗ ЛИШНИХ СЛОВ) ---")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
