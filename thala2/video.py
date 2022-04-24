import io
import numpy as np
import platform
from moviepy.editor import *
from moviepy.audio.AudioClip import *
from moviepy.video.VideoClip import *
from PIL import ImageFont
from .audio import Audio
from .util import parse_time, ALL_ELEMENTS
from .bbox import *

FONT_PATH = {
    "Windows": "C:/Windows/Fonts/meiryo.ttc",
    "Darwin": "/System/Library/Fonts/Courier.dfont",
    "Linux": "/usr/share/fonts/OTF/TakaoPMincho.ttf"
}


class Video:
    def __init__(self, *, fontPath=None, fontSize=52,
                 colorBGR=(0, 0, 0, 255), audio=None):
        super().__init__()
        if not fontPath:
            pf = platform.system()
            if pf in FONT_PATH:
                fontPath = FONT_PATH[pf]
            else:
                assert False, "fontPath is not specified."

        self.__fontPIL = ImageFont.truetype(fontPath, fontSize)
        self.__colorBGR = colorBGR
        self.__audio = audio or Audio()

    def _build_audio(self, elem):
        assert len(elem) == 0, "no child is needed."

        audio = self.__audio.build(elem)
        video = BoundingBox(1, 1, audio.duration_seconds)

        return (video, audio)

    def _build_movie(self, elem):
        assert len(elem) == 0, "no child is needed."

        if "src" in elem.attrib:
            src = elem.attrib["src"]
        else:
            assert False, "src file is needed."

        return (MovieBB(src), self.__audio._build_any(elem))

    def _build_image(self, elem):
        assert len(elem) == 0, "no child is needed."

        if "src" in elem.attrib:
            src = elem.attrib["src"]
        else:
            assert False, "src file is needed."

        if "duration" in elem.attrib:
            duration = parse_time(elem.attrib["duration"])
        else:
            duration = 0

        return (ImageBB(duration, src), self.__audio._build_any(elem))

    def _build_speak(self, elem):
        text = elem.text or ""
        for child in elem:
            if child.tag == "sub":
                assert "alias" in child.attrib
                if child.text:
                    text += child.text
                if child.tail:
                    text += child.tail
            else:
                assert False, "child with sub-tag is needed."

        audio = self.__audio._build_any(elem)
        video = TextBB(
            audio.duration_seconds,
            text,
            self.__fontPIL,
            self.__colorBGR)

        return (video, audio)

    def _build_media(self, elem):
        assert len(elem) == 1, "only 1 child is needed."
        assert elem[0].tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

        (video, _) = self._build_any(elem[0])
        w0, h0, d0 = video.boundings()

        if "width" in elem.attrib:
            width = int(elem.attrib["width"])
        else:
            width = w0
        if "height" in elem.attrib:
            height = int(elem.attrib["height"])
        else:
            height = h0
        if "duration" in elem.attrib:
            duration = parse_time(elem.attrib["duration"])
        else:
            duration = d0

        if width < w0 or height < h0 or duration < d0:
            video = ScaleBB(video, min(width / w0, height /
                            h0, 1), min(duration / d0, 1))
            w0, h0, d0 = video.boundings()
            if "width" not in elem.attrib:
                width = w0
            if "height" not in elem.attrib:
                height = h0
        if w0 < width or h0 < height or d0 < duration:
            video = MarginBB(
                video,
                0,
                0,
                0.,
                max(width - w0, 0),
                max(height - h0, 0),
                max(duration - d0, 0))

        return (video, self.__audio._build_any(elem))

    def _build_crop(self, elem):
        assert len(elem) == 1, "only 1 child is needed."
        assert elem[0].tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

        (video, _) = self._build_any(elem[0])
        width, height, duration = video.boundings()

        if "x0" in elem.attrib:
            x0 = int(elem.attrib["x0"])
            assert 0 <= x0, "0 <= x0 is needed."
        else:
            x0 = 0
        if "y0" in elem.attrib:
            y0 = int(elem.attrib["y0"])
            assert 0 <= y0, "0 <= y0 is needed."
        else:
            y0 = 0
        if "t0" in elem.attrib:
            t0 = parse_time(elem.attrib["t0"])
            assert 0 <= t0, "0 <= t0 is needed."
        else:
            t0 = 0
        if "x1" in elem.attrib:
            x1 = int(elem.attrib["x1"])
            assert x0 <= x1, "x0 <= x1 is needed."
        else:
            x1 = width
        if "y1" in elem.attrib:
            y1 = int(elem.attrib["y1"])
            assert y0 <= y1, "y0 <= y1 is needed."
        else:
            y1 = height
        if "t1" in elem.attrib:
            t1 = parse_time(elem.attrib["t1"])
            assert 0 <= t1, "0 <= t1 is needed."
        else:
            t1 = duration

        if 0 < x0 or 0 < y0 or 0 < t0 or x1 < width or y1 < height or t1 < duration:
            video = CropBB(video, x0, y0, t0, x1, y1, t1)

        return (video, self.__audio._build_any(elem))

    def _build_margin(self, elem):
        assert len(elem) == 1, "only 1 child is needed."
        assert elem[0].tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

        (video, _) = self._build_any(elem[0])

        if "left" in elem.attrib:
            left = int(elem.attrib["left"])
        else:
            left = 0
        if "right" in elem.attrib:
            right = int(elem.attrib["right"])
            assert 0 <= right, "0 <= right is needed."
        else:
            right = 0
        if "before" in elem.attrib:
            before = parse_time(elem.attrib["before"])
            assert 0 <= before, "0 <= before is needed."
        else:
            before = 0
        if "top" in elem.attrib:
            top = int(elem.attrib["top"])
            assert 0 <= top, "0 <= top is needed."
        else:
            top = 0
        if "bottom" in elem.attrib:
            bottom = int(elem.attrib["bottom"])
            assert 0 <= bottom, "0 <= bottom is needed."
        else:
            bottom = 0
        if "after" in elem.attrib:
            after = parse_time(elem.attrib["after"])
            assert 0 <= after, "0 <= after is needed."
        else:
            after = 0

        if 0 < left or 0 < top or 0 < before or 0 < right or 0 < bottom or 0 < after:
            video = MarginBB(video, left, top, before, right, bottom, after)

        return (video, self.__audio._build_any(elem))

    def _build_scale(self, elem):
        assert len(elem) == 1, "only 1 child is needed."
        assert elem[0].tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

        (video, _) = self._build_any(elem[0])
        w0, h0, d0 = video.boundings()

        if "fxy" in elem.attrib:
            fxy = float(elem.attrib["fxy"])
            assert 0 < fxy, "0 <= fxy is needed."
        else:
            if "width" in elem.attrib:
                width = int(elem.attrib["width"])
            else:
                width = w0
            if "height" in elem.attrib:
                height = int(elem.attrib["height"])
            else:
                height = h0
            fxy = min(width / w0, height / h0)
            assert 0 < fxy, "0 <= fxy is needed."
        if "ft" in elem.attrib:
            ft = float(elem.attrib["ft"])
            assert 0 < fxy, "0 <= fxy is needed."
        elif "duration" in elem.attrib:
            ft = parse_time(elem.attrib["duration"]) / d0
        else:
            ft = 1

        if fxy != 1 or ft != 1:
            video = ScaleBB(video, fxy, ft)

        return (video, self.__audio._build_any(elem))

    def _build_par(self, elem):
        bblst = []

        for child in elem:
            assert child.tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

            (video, _) = self._build_any(child)
            bblst.append(video)

        return (ParBB(bblst), self.__audio._build_any(elem))

    def _build_seq(self, elem):
        bblst = []

        for child in elem:
            assert child.tag in ALL_ELEMENTS, f"child with {ALL_ELEMENTS}-tag is needed."

            (video, _) = self._build_any(child)
            bblst.append(video)

        return (SeqBB(bblst), self.__audio._build_any(elem))

    def _build_any(self, elem):
        assert elem.tag in ALL_ELEMENTS, f"elem with {ALL_ELEMENTS}-tag is needed."

        if elem.tag == "audio":
            return self._build_audio(elem)
        elif elem.tag == "movie":
            return self._build_movie(elem)
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

    def encode(self, elem):
        (video, audio) = self.build(elem)

        (_, _, duration) = video.boundings()

        def make_frame(t):
            return video.image(t)[:, :, 2::-1]

        clip = VideoClip(make_frame, duration=duration)
        # WORK_AROUND: MoviePy seem to have bugs to calculate the duration of
        # monoral audio
        audio = audio.set_channels(2)
        array = np.frombuffer(audio.raw_data,
                              dtype=np.int16).reshape(-1,
                                                      audio.channels) / 65535.
        clip.audio = AudioArrayClip(array, fps=audio.frame_rate)

        return clip
