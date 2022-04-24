
import xml.etree.ElementTree as ET


def make_bg(src, duration):
    bg = ET.Element("media", {"width": "960", "height": "540"})
    img = ET.SubElement(
        bg, "image", {
            "duration": f"{duration}s", "src": src})
    return bg


def make_mov_speak(src, text, t0, t1, ft):
    return (ET.fromstring(f"""
<par>
    <scale ft="{ft}">
        <crop x0="0" x1="270" y0="30" y1="570" t0="{t0}s" t1="{t1}s">
            <scale fxy="0.375" soundLevel="-15dB">
                <media width="720" height="1600">
                    <movie src="{src}"/>
                </media>
            </scale>
        </crop>
    </scale>
    <margin top="50" left="300">
        <par>
            <margin before="0s">
                <media width="600" height="450" duration="{(t1-t0)*ft}s">
                    <speak>{text}</speak>
                </media>
            </margin>
        </par>
    </margin>
</par>
"""), (t1 - t0) * ft)


def make_full_speak(text, duration):
    return (ET.fromstring(f"""
<margin top="50" left="100">
    <media width="800" height="450" duration="{duration}s">
        <speak>{text}</speak>
    </media>
</margin>"""), duration)
