import gtts
import io
from .tts import TTS


class GoogleTTS(TTS):
    def __init__(self, host="http://localhost:50021", speaker=4):
        super().__init__()

        self.__host = host
        self.__speaker = speaker

    def text_to_speech(self, text: str):
        """
        call Text-To-Speech of VOICEVOX
        """

        f = io.BytesIO()

        gtts.gTTS(text=text, lang="ja").write_to_fp(f)

        return (f.getvalue(), "mp3")
