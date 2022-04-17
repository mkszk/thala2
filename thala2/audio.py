import pydub
import io
import base64
from .tts import VoiceVoxTTS, GoogleTTS
from .util import parse_time, parse_gain, ALL_ELEMENTS
import requests
import regex


def speedup(audio, ft):
    return pydub.AudioSegment(
        data=audio.raw_data,
        sample_width=audio.sample_width,
        frame_rate=int(audio.frame_rate / ft),
        channels=audio.channels)


class Audio:
    def __init__(self, *, tts=None):
        super().__init__()
        if tts:
            self.__tts = tts
        else:
            try:
                res = requests.get("http://localhost:50021/docs")
                if res.status_code == 200 and regex.search(
                    "<title>VOICEVOX ENGINE - Swagger UI</title>",
                        res.text):
                    self.__tts = VoiceVoxTTS(host="http://localhost:50021")
                else:
                    self.__tts = GoogleTTS()
            except requests.exceptions.ConnectionError:
                self.__tts = GoogleTTS()

    def _build_audio(self, elem):
        assert len(elem) == 0, "no child is needed."

        if "src" in elem.attrib:
            src = elem.attrib["src"]
        else:
            assert False, "src file is needed."

        return pydub.AudioSegment.from_file(src)

    def _build_image(self, elem):
        assert len(elem) == 0, "no child is needed."

        if "duration" in elem.attrib:
            duration = parse_time(elem.attrib["duration"])
        else:
            duration = 0.0

        return pydub.AudioSegment.silent(duration*1000)

    def _build_speak(self, elem):
        text = elem.text or ""
        for child in elem:
            if child.tag == "sub":
                assert "alias" in child.attrib
                text += child.attrib["alias"]
                text += child.tail
            else:
                assert False, "child with sub-tag is needed."

        (data, fmt) = self.__tts.text_to_speech(text)
        audio = pydub.AudioSegment.from_file(io.BytesIO(data), format=fmt)

        return audio

    def _build_media(self, elem):
        assert len(elem) == 1, "only 1 child is needed."
        assert elem[0].tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

        audio = self._build_any(elem[0])

        if "duration" in elem.attrib:
            duration = parse_time(elem.attrib["duration"])

            if duration < audio.duration_seconds:
                audio = speedup(audio,
                                duration / audio.duration_seconds
                                )
            elif audio.duration_seconds < duration:
                audio = audio + \
                    pydub.AudioSegment.silent(
                        (duration - audio.duration_seconds) * 1000)

        return audio

    def _build_crop(self, elem):
        assert len(elem) == 1, "only 1 child is needed."
        assert elem[0].tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

        audio = self._build_any(elem[0])

        if "t0" in elem.attrib:
            t0 = parse_time(elem.attrib["t0"])
            assert 0 <= t0, "0 <= t0 is needed."
        else:
            t0 = 0
        if "t1" in elem.attrib:
            t1 = parse_time(elem.attrib["t1"])
            assert 0 <= t1, "0 <= t1 is needed."
        else:
            t1 = audio.duration_seconds

        if 0 < t0 or t1 < audio.duration_seconds:
            audio = audio[t0 * 1000:t1 * 1000]

        return audio

    def _build_margin(self, elem):
        assert len(elem) == 1, "only 1 child is needed."
        assert elem[0].tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

        audio = self._build_any(elem[0])

        if "before" in elem.attrib:
            before = parse_time(elem.attrib["before"])
            assert 0 <= before, "0 <= before is needed."
        else:
            before = 0
        if "after" in elem.attrib:
            after = parse_time(elem.attrib["after"])
            assert 0 <= after, "0 <= after is needed."
        else:
            after = 0

        if 0 < before:
            audio = pydub.AudioSegment.silent(before * 1000) + audio
        if 0 < after:
            audio = audio + pydub.AudioSegment.silent(after * 1000)

        return audio

    def _build_scale(self, elem):
        assert len(elem) == 1, "only 1 child is needed."
        assert elem[0].tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

        audio = self._build_any(elem[0])

        if "soundLevel" in elem.attrib:
            soundLevel = parse_gain(elem.attrib["soundLevel"])

            audio = audio.apply_gain(soundLevel)

        if "ft" in elem.attrib:
            ft = float(elem.attrib["ft"])
            assert 0 < ft, "0 <= ft is needed."
        elif "duration" in elem.attrib:
            ft = parse_time(elem.attrib["duration"]) / audio.duration_seconds
        else:
            ft = 1

        if ft != 1 and ft != 0:
            audio = speedup(audio, ft)

        return audio

    def _build_par(self, elem):
        audio = None

        for child in elem:
            assert child.tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

            next = self._build_any(child)

            if audio:
                if audio.duration_seconds < next.duration_seconds:
                    audio = next.overlay(audio)
                else:
                    audio = audio.overlay(next)
            else:
                audio = next

        return audio

    def _build_seq(self, elem):
        audio = None

        for child in elem:
            assert child.tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

            assert elem.tag in (
                "media", "seq", "par", ), "child with media-tag / seq-tag / par-tag is needed."

            next = self._build_any(child)

            if audio:
                audio += next
            else:
                audio = next

        return audio

    def _build_any(self, elem):
        if ("raw_data" in elem.attrib and "sample_width" in elem.attrib and
                "frame_rate" in elem.attrib and "channels" in elem.attrib):
            return pydub.AudioSegment(
                data=base64.b64decode(elem.attrib["raw_data"].encode()),
                sample_width=int(elem.attrib["sample_width"]),
                frame_rate=int(elem.attrib["frame_rate"]),
                channels=int(elem.attrib["channels"])
            )
        else:
            audio = self._build_dummy(elem)

            elem.attrib["raw_data"] = base64.b64encode(audio.raw_data).decode()
            elem.attrib["sample_width"] = str(audio.sample_width)
            elem.attrib["frame_rate"] = str(audio.frame_rate)
            elem.attrib["channels"] = str(audio.channels)

            return audio

    def _build_dummy(self, elem):
        assert elem.tag in ALL_ELEMENTS, f"elem with {ALL_ELEMENTS}-tag is needed."

        if elem.tag in ("audio", "movie"):
            return self._build_audio(elem)
        elif elem.tag == "image":
            return self._build_image(elem)
        elif elem.tag == "speak":
            return self._build_speak(elem)
        elif elem.tag == "media":
            return self._build_media(elem)
        elif elem.tag == "crop":
            return self._build_crop(elem)
        elif elem.tag == "margin":
            return self._build_margin(elem)
        elif elem.tag == "scale":
            return self._build_scale(elem)
        elif elem.tag == "par":
            return self._build_par(elem)
        elif elem.tag == "seq":
            return self._build_seq(elem)
        else:
            assert False

    def build(self, elem):
        return self._build_any(elem)
