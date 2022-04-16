import requests
from .tts import TTS


class VoiceVoxTTS(TTS):
    def __init__(self, *, host="http://localhost:50021", speaker=2):
        super().__init__()

        self.__host = host
        self.__speaker = speaker

    def text_to_speech(self, text: str):
        """
        call Text-To-Speech of VOICEVOX
        """
        params = {
            "text": TTS.WHITESPACE.sub(text, " "),
            "speaker": self.__speaker,
        }
        query = requests.post("/".join([self.__host, "audio_query"]),
                              params=params)

        params = {
            "speaker": self.__speaker,
        }
        headers = {
            "accept": "audio/wav",
            "Content-Type": "application/json"
        }
        wave = requests.post("/".join([self.__host, "synthesis"]),
                             params=params,
                             json=query.json())

        return (wave._content, "wav")
