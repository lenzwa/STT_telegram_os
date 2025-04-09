from dotenv import load_dotenv
import os
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import json
import shutil
import cogs.STT
import time
from datetime import datetime
from openai import OpenAI
from collections import defaultdict, deque

load_dotenv()
TOKEN = os.environ.get("TG_TOKEN")
client = OpenAI(api_key=os.environ.get("CHATGPT"))

# Глобальная память для истории сообщений (до 10 последних) и пресетов
user_history = defaultdict(lambda: deque(maxlen=10))
# Если юзер не выбрал пресет, будет использоваться пресет "Учитель" по умолчанию
user_presets = defaultdict(
    lambda: "Ты крутой профессиональный учитель всех языков мира, "
              "который отвечает в стиле Gen-Z, общайся максимально как подросток "
              "и всегда добавляй примеры к ответу, чтобы дать точный и хороший ответ."
)


def resolve_context(user_id, text):
    """
    Если в тексте встречается фраза 'это же', заменяем её на последний запрос пользователя.
    """
    if "это же" in text.lower():
        history = user_history[user_id]
        if history:
            last_query = history[-1]
            return text.replace("это же", last_query)
    return text


class StartTelegram:
    def __init__(self) -> None:
        pass

    def runbot():

        def makeDir():
            voice_dir = os.path.join(os.getcwd(), "voice")
            os.makedirs(voice_dir, exist_ok=True)

        def removeDir():
            voice_dir = os.path.join(os.getcwd(), "voice")
            shutil.rmtree(voice_dir, ignore_errors=True)

        application = Application.builder().token(TOKEN).build()

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                "Привет! Я помощник компании Simble, задавай вопрос 😉\n"
                "Для выбора стиля ответов используй команду /setpreset"
            )

        async def set_preset(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Команда для выбора пресета. Выводит инлайн-клавиатуру с вариантами."""
            keyboard = [
                [InlineKeyboardButton("Учитель", callback_data="preset_teacher")],
                [InlineKeyboardButton("Ассистент", callback_data="preset_assistant")],
                [InlineKeyboardButton("Юмор", callback_data="preset_comedy")],
                [InlineKeyboardButton("Альт", callback_data="preset_alt")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("Выбери, как тебе отвечать:", reply_markup=reply_markup)

        async def preset_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
            """Обработка выбора пресета через callback-запрос."""
            query = update.callback_query
            await query.answer()  # уведомляем о принятии запроса
            data = query.data

            if data == "preset_teacher":
                preset = ("Ты крутой профессиональный учитель всех языков мира, "
                          "который отвечает в стиле Gen-Z, общайся максимально как подросток "
                          "и всегда добавляй примеры к ответу, чтобы дать точный и хороший ответ.")
            elif data == "preset_assistant":
                preset = "Ты учитель, серьезный и настроенный на результаты ученика, ты максимально хочешь просто разжевать тему ученику и показать на примере"
            elif data == "preset_comedy":
                preset = "Ты компетентный и ооочень смешной учитель , но очень комичный и любишь шутить  и иногда смеятся, иногда у тебя появляется сарказм и саркастичные высказывания"
            elif data == "preset_alt":
                preset = "Челик, ты типа учитель но дрейн и альтушка, ты разговариваешь максимально как альтушка и любишь говорить: целую тебя красоточка"
            else:
                preset = user_presets[query.from_user.id]

            user_presets[query.from_user.id] = preset
            preset_name = data.replace("preset_", "").capitalize()
            await query.edit_message_text(text=f"Выбран пресет: {preset_name}")

        async def data(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text("Данные сгружены 🧠")

        async def voiceHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            voice_dir = os.path.join(os.getcwd(), "voice")
            os.makedirs(voice_dir, exist_ok=True)

            new_file = await context.bot.get_file(update.message.voice.file_id)
            voice_files = os.listdir(voice_dir)
            voice_index = len(voice_files)
            voice_filename = f"voice_{voice_index}.ogg"
            voice_path = os.path.join(voice_dir, voice_filename)
            await new_file.download_to_drive(voice_path)
            await update.message.reply_text("🎙️ Voice note saved!")

            # Распознавание речи (Whisper)
            original_text = cogs.STT.SpeechToText(voice_filename).transcribe_audio()
            # Обновляем историю запросов
            user_history[update.effective_user.id].append(original_text)
            # Если есть фраза "это же", заменяем её на предыдущий запрос
            resolved_text = resolve_context(update.effective_user.id, original_text)
            await update.message.reply_text(f"Вы сказали: {resolved_text}")

            # Функция для запроса к GPT с выбранным системным пресетом
            def ask_gpt(text):
                system_message = user_presets[update.effective_user.id]
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": text}
                    ]
                )
                return response.choices[0].message.content

            answer = ask_gpt(resolved_text)

            # Функция для конвертации текста в аудио (Text-to-Speech, TTS)
            def text_to_speech(text, filename="response.mp3"):
                response = client.audio.speech.create(
                    model="tts-1",
                    voice="nova",  # Другие варианты: alloy, echo, fable, onyx, shimmer
                    input=text
                )
                with open(filename, "wb") as f:
                    f.write(response.content)

            await update.message.reply_text(f"🤖 GPT: {answer}")
            audio_path = os.path.join(voice_dir, "response.mp3")
            text_to_speech(answer, audio_path)
            with open(audio_path, "rb") as voice:
                await context.bot.send_voice(chat_id=update.effective_chat.id, voice=voice)
            time.sleep(5)

        async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
            now = datetime.now()
            stop_msg = (
                f"Бот выключился в:\n"
                f"Время: {now.hour}:{now.minute}\n"
                f"Дата: {now.day}.{now.month}.{now.year}"
            )
            await update.message.reply_text(stop_msg)
            context.application.stop_running()

        def main():
            makeDir()
            print("🚀 Started bot...")
            # Команды бота:
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("setpreset", set_preset))
            application.add_handler(CallbackQueryHandler(preset_callback, pattern=r"^preset_"))
            application.add_handler(CommandHandler("data", data))
            application.add_handler(CommandHandler("stop", stop))
            application.add_handler(MessageHandler(filters.VOICE, voiceHandler))
            application.run_polling()
            removeDir()

        main()
