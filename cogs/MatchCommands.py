import re
from langchain.text_splitter import CharacterTextSplitter
import webbrowser
import os
import keyboard
import psutil
import shutil


def kill_process_by_name(process_name):
    # Перебираем все запущенные процессы
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            # Проверяем, совпадает ли имя процесса с 'firefox'
            if proc.info["name"].lower() == process_name:
                proc.terminate()  # Завершаем процесс
                print(f"Процесс Firefox с PID {proc.info['pid']} был завершён.")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


class Option:
    def __init__(self, text: str = "") -> None:
        self.text = text
        deleteComma = (
            text.lower()
            .replace(",", " ")
            .replace("!", " ")
            .replace("?", " ")
            .replace(".", " ")
        )
        commandCheckOnSpace = (
            deleteComma.split(" ")
            if "видео" not in deleteComma
            else deleteComma.split("видео")
        )
        if (
            "ютуб" in commandCheckOnSpace
            or "youtube" in commandCheckOnSpace
            and "открой" in commandCheckOnSpace
            or "ютуб" in commandCheckOnSpace[0]
            and len(deleteComma) <= 20
        ):
            webbrowser.open_new_tab("https://youtube.com")
        elif (
            "ютуб" in commandCheckOnSpace[0]
            and "открой" in commandCheckOnSpace[0]
            and "видео" in deleteComma
        ):
            print(commandCheckOnSpace, len(deleteComma))
            webbrowser.open_new_tab(
                f"https://www.youtube.com/results?search_query={commandCheckOnSpace[1].strip().replace(' ' or '', '+')}"
            )
        elif "дискорд" in commandCheckOnSpace and "открой" in commandCheckOnSpace:
            print("Открываю дискорд")
            os.system(
                'start "" "C:\\Users\\User\\AppData\\Local\\Discord\\app-1.0.9154\\Discord.exe"'
            )
        elif (
            "следующее" in commandCheckOnSpace or "следующее" in commandCheckOnSpace[0]
        ):
            print("Следующее видео в процессе")
            keyboard.send("shift+n")
        elif "выключи" in commandCheckOnSpace:
            shutil.rmtree(os.getcwd() + "\\voice")
            os.system("shutdown /s /t 0")
        elif "открой" in commandCheckOnSpace and "набор" in commandCheckOnSpace:
            os.system(
                'start "" "D:\\Steam\\steamapps\\common\\dota 2 beta\\game\\bin\\win64\\dota2.exe"'
            )
            webbrowser.open_new_tab("https://youtube.com")
            webbrowser.open_new_tab(
                "https://chatgpt.com/c/577b9d11-85f0-4ca9-992e-8e1fa9b70091"
            )
            webbrowser.open_new_tab("https://platform.openai.com/usage")
            os.system("code")
        elif "закрой" in commandCheckOnSpace and (
            "браузер" in commandCheckOnSpace or "browser" in commandCheckOnSpace
        ):
            kill_process_by_name("Firefox.exe".lower())
        else:
            print("Попробуйте еще раз")
