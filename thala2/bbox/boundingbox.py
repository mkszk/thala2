import io
import cv2
import numpy as np
from PIL import Image, ImageDraw


def alpha_brend(dst, src, *, left=0, top=0):
    h1, w1, a1 = dst.shape
    h2, w2, a2 = src.shape
    h = min(h1 - top, h2)
    w = min(w1 - left, w2)
    assert 0 <= left
    assert 0 <= top
    assert 0 <= h
    assert 0 <= w
    assert a1 in (3, 4)
    assert a2 in (3, 4)
    if a2 == 3:
        dst[top:top + h, left:left + w, :3] = src[:h, :w, :3]
        if a1 == 4:
            dst[top:top + h, left:left + w, 3] = 255
    else:
        mask = src[:h, :w, 3] / 255
        for i in range(3):
            dst[top:top + h, left:left + w, i] = (dst[top:top + h, left:left + w, i] * (1 - mask) +
                                                  src[:h, :w, i] * mask).astype(np.uint8)
        if a1 == 4:
            dst[top:top + h, left:left + w, 3] = ((1 - (1 - dst[top:top + h, left:left + w, 3] / 255)
                                                   * (1 - mask)) * 255).astype(np.uint8)

    return dst


def get_textbbox(text, fontPIL):
    dummy_draw = ImageDraw.Draw(Image.new("RGBA", (0, 0)))
    _, _, text_w, text_h = dummy_draw.multiline_textbbox(
        (0, 0), text, font=fontPIL)

    return (text_w, text_h)


def put_text(img, text, left, top, fontPIL, colorBGR):
    assert 0 <= left, "left>=0 is needed."
    assert 0 <= top, "top>=0 is needed."

    text_w, text_h = get_textbbox(text, fontPIL)
    text_img = np.full((text_h, text_w, 4), (0, 0, 0, 0), dtype=np.uint8)

    imgPIL = Image.fromarray(text_img)
    draw = ImageDraw.Draw(imgPIL)
    draw.text(xy=(0, 0), text=text, fill=colorBGR, font=fontPIL)
    text_img = np.array(imgPIL, dtype=np.uint8)

    alpha_brend(img, text_img, left=left, top=top)

    return img


class BoundingBox:
    def __init__(self, width, height, duration):
        self.width = width
        self.height = height
        self.duration = duration

    def image(self, t):
        temp = np.zeros([self.height, self.width, 4],
                        dtype=np.uint8)

        return np.zeros([self.height, self.width, 4],
                        dtype=np.uint8)

    def boundings(self):
        return (self.width, self.height, self.duration)


class MovieBB(BoundingBox):
    def __init__(self, fname):
        if isinstance(fname, str):
            self.fname = fname
            self.movie = cv2.VideoCapture(fname)
        elif isinstance(fname, io.BytesIO):
            self.fname = None
            self.movie = cv2.VideoCapture(fname)
        else:
            assert False

        super().__init__(int(self.movie.get(cv2.CAP_PROP_FRAME_WIDTH)),
                         int(self.movie.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                         (self.movie.get(cv2.CAP_PROP_FRAME_COUNT) - 1) /
                         self.movie.get(cv2.CAP_PROP_FPS))

    def __del__(self):
        self.movie.release()

    def image(self, t):
        self.movie.set(0, t * 1000)
        ret, frame = self.movie.read()
        if ret:
            return frame
        else:
            return super().image(t)


class TextBB(BoundingBox):
    def __init__(self, duration: float, text: str, fontPIL, colorBGR: tuple):
        w, h = get_textbbox(text, fontPIL)
        super().__init__(w, h, duration)

        self.text = text
        self.fontPIL = fontPIL
        self.colorBGR = colorBGR

    def image(self, t):
        img = super().image(t)
        put_text(img, self.text, 0, 0, self.fontPIL, self.colorBGR)
        return img


class ImageBB(BoundingBox):
    def __init__(self, duration: float, fname: str):
        if isinstance(fname, str):
            self.fname = fname
            self.frame = cv2.imread(fname, cv2.IMREAD_UNCHANGED)
        elif isinstance(fname, io.BytesIO):
            self.fname = None
            self.frame = cv2.imread(fname, cv2.IMREAD_UNCHANGED)
        else:
            assert False

        h, w, _ = self.frame.shape
        super().__init__(w, h, duration)

    def image(self, t):
        return self.frame.copy()


class CropBB(BoundingBox):
    def __init__(self, bb: BoundingBox, x0: int, y0: int,
                 t0: float, x1: int, y1: int, t1: float):
        width, height, duration = bb.boundings()

        x1 = min(x1, width)
        y1 = min(y1, height)
        t1 = min(t1, duration)
        assert 0 <= x0, f"x0={x0} should be more than 0."
        assert 0 <= y0, f"y0={y0} should be more than 0."
        assert 0 <= t0, f"t0={t0} should be more than 0."
        assert x0 <= x1, f"x0={x0} should be less than x1={x1}."
        assert y0 <= y1, f"y0={y0} should be less than y1={y1}."
        assert t0 <= t1, f"t0={t0} should be less than t1={t1}."

        super().__init__(x1 - x0, y1 - y0, t1 - t0)

        self.bb = bb
        self.x0 = x0
        self.y0 = y0
        self.t0 = t0
        self.x1 = x1
        self.y1 = y1
        self.t1 = t1

    def image(self, t):
        if self.t0 + t <= self.t1:
            img = self.bb.image(t + self.t0)
            return img[self.y0:self.y1, self.x0:self.x1, :]
        else:
            return super().image(t)


class MarginBB(BoundingBox):
    def __init__(self, bb: BoundingBox, left: int, top: int, before: float,
                 right: int, bottom: int, after: float):
        width, height, duration = bb.boundings()

        assert 0 <= left, "0 <= left is needed."
        assert 0 <= top, "0 <= top is needed."
        assert 0 <= before, "0 <= before is needed."
        assert 0 <= right, "0 <= right is needed."
        assert 0 <= bottom, "0 <= bottom is needed."
        assert 0 <= after, "0 <= after is needed."

        super().__init__(
            left + width + right,
            top + height + bottom,
            before + duration + after)

        self.bb = bb
        self.left = left
        self.top = top
        self.before = before
        self.right = right
        self.bottom = bottom
        self.after = after

    def image(self, t):
        width, height, duration = self.bb.boundings()
        if self.before <= t <= self.before + duration:
            img = super().image(t)
            alpha_brend(img, self.bb.image(t - self.before),
                        left=self.left, top=self.top)
            return img
        else:
            return super().image(t)


class ScaleBB(BoundingBox):
    def __init__(self, bb: BoundingBox, fxy: float, ft: float):
        width, height, duration = bb.boundings()

        assert 0 < fxy, "0 < fxy is needed."
        assert 0 < ft, "0 < ft is needed."

        super().__init__(int(width * fxy), int(height * fxy), duration * ft)

        self.bb = bb
        self.fxy = fxy
        self.ft = ft

    def image(self, t):
        width, height, duration = self.bb.boundings()
        if self.duration < t:
            return super().image(t)
        else:
            img = self.bb.image(t / self.ft)
            return cv2.resize(img, dsize=(self.width, self.height))


class ParBB(BoundingBox):
    def __init__(self, bblst):
        temp = [bb.boundings() for bb in bblst]

        super().__init__(max(b[0] for b in temp),
                         max(b[1] for b in temp), max(b[2] for b in temp))

        self.bblst = bblst

    def image(self, t):
        width, height, duration = self.boundings()

        if self.duration < t:
            return super().image(t)
        else:
            img = super().image(t)
            for bb in self.bblst:
                alpha_brend(img, bb.image(t))
            return img


class SeqBB(BoundingBox):
    def __init__(self, bblst):
        temp = [bb.boundings() for bb in bblst]

        super().__init__(max(b[0] for b in temp),
                         max(b[1] for b in temp), sum(b[2] for b in temp))

        self.bblst = bblst

    def image(self, t):
        for bb in self.bblst:
            _, _, duration = bb.boundings()

            if t < duration:
                return alpha_brend(super().image(t), bb.image(t))
            else:
                t -= duration
        return super().image(t)
