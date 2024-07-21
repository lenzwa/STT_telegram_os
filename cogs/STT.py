from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import openai
from langchain_community.document_loaders.parsers.audio import OpenAIWhisperParser
import os

load_dotenv()

TOKEN = os.environ.get("CHATGPT")
openai.api_key = TOKEN


class SpeechToText:
    def __init__(self, name) -> None:
        self.name = name

    def transcribe_audio(self):
        with open(
            os.getcwd() + "\\voice\\" + self.name,
            "rb",
        ) as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1", file=audio_file
            )
        print(response.text)
        return response.text


print()
