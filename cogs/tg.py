from dotenv import load_dotenv
import os
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    Updater,
)
from telegram import Update
import json
import shutil
import cogs.STT
from cogs.MatchCommands import Option
import time
from datetime import datetime

load_dotenv()
TOKEN = os.environ.get("TG_TOKEN")


class StartTelegram:
    def __init__(self) -> None:
        pass

    def runbot():

        def makeDir():
            os.mkdir(os.getcwd() + "\\voice")

        def removeDir():
            shutil.rmtree(os.getcwd() + "\\voice")

        application = Application.builder().token(TOKEN).build()

        async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

            await update.message.reply_text(
                "Привет я помощник компании simble , задавай вопрос"
            )

        async def data(update, context: ContextTypes.DEFAULT_TYPE):

            await update.message.reply_text("Данные сгружены")

        async def voiceHandler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            new_file = await context.bot.get_file(update.message.voice.file_id)
            await new_file.download_to_drive(
                os.getcwd()
                + f"\\voice\\voice_{len(os.listdir(os.getcwd()+'\\voice'))}.ogg"
            )

            await update.message.reply_text("Voice note saved")
            text = cogs.STT.SpeechToText(
                os.listdir(os.getcwd() + "\\voice")[
                    (
                        len(os.listdir(os.getcwd() + "\\voice")) - 1
                        if len(os.listdir(os.getcwd() + "\\voice")) != 0
                        else len(os.listdir(os.getcwd() + "\\voice"))[0]
                    )
                ]
            ).transcribe_audio()

            await update.message.reply_text(f"Вы сказали примерно: {text}")
            time.sleep(5)
            Option(text=text)

        async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await update.message.reply_text(
                f"Бот выключился в: \nВремя : {datetime.now().hour}:{datetime.now().minute}\nДата : {str(datetime.now().day)+'.' +str(datetime.now().month)+'.' +str(datetime.now().year)}"
            )
            context.application.stop_running()

        def main():
            makeDir()
            print("Started bot..")
            application.add_handler(CommandHandler("start", start))
            application.add_handler(CommandHandler("data", data))
            application.add_handler(CommandHandler("stop", stop))
            application.add_handler(MessageHandler(filters.VOICE, voiceHandler))
            application.run_polling()
            removeDir()

        main()
