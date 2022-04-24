import thala2
import xml.etree.ElementTree as ET
from datetime import datetime as DT
import argparse
import megido

parser = argparse.ArgumentParser()
parser.add_argument("--src", type=str)
parser.add_argument("--bg", type=str)
parser.add_argument("--fps", type=float, default=30)
args = parser.parse_args()

root = ET.Element("media", {"width": "960", "height": "540"})

duration = 0
children = []

c, d = megido.make_full_speak("""
メギド72の解説動画です。
状態異常耐性についてです。""", 5)
children.append(c)
duration += d

c, d = megido.make_mov_speak(args.src, """
敵はスキルで
毒の状態異常を付与してきます。
もしも毒になると、
ターンごとにダメージを受けるうえに、
奥義の毒特効も受けてしまいます。
また、防御力も1248と高く、
半端な攻撃は意味がありません。""", 12, 16, 4)
children.append(c)
duration += d

c, d = megido.make_mov_speak(args.src, """
防御の高いガープのスキルで
敵のアタックや覚醒スキル、
奥義を防げます。""", 16, 17.5, 4)
children.append(c)
duration += d

c, d = megido.make_mov_speak(args.src, """
バルバトスの<sub alias="マスエフェクト">ME</sub>で
敵のスキルの毒を防げます。
また、奥義で回復もできます。""", 17.5, 19.5, 4)
children.append(c)
duration += d

c, d = megido.make_mov_speak(args.src, """
シャックスの奥義で攻撃します。
オーブのホーリーフェイクにより
敵の防御力を60%無視することで
攻撃が通るようになります。""", 19.5, 22, 4)
children.append(c)
duration += d

c, d = megido.make_mov_speak(args.src, """
ガープはスキルで守りを固めます。
バルバトスは覚醒を貯めます。
シャックスは攻撃しながら
覚醒を貯めます。""", 22, 57, 1)
children.append(c)
duration += d

c, d = megido.make_mov_speak(args.src, """
ガープはスキルで守りを固めます。
バルバトスは覚醒スキルで
シャックスの攻撃力を上げます。
シャックスは奥義で攻撃します。""", 57, 101, 1)
children.append(c)
duration += d

c, d = megido.make_mov_speak(args.src, """
あとは繰り返しなので早送りします。""", 101, 239, 0.25)
children.append(c)
duration += d

c, d = megido.make_mov_speak(args.src, """
勝ちました。""", 239, 243, 1)
children.append(c)
duration += d

c, d = megido.make_full_speak("""
メギド72の解説動画でした。
<sub alias="マスエフェクト">ME</sub>で状態異常を防ぐと
ダメージを大幅に減らせます。

<sub alias="音声はボイスボックスの四国めたんでした。">音声 VOICEVOX:四国めたん</sub>""", 12)
children.append(c)
duration += d

par = ET.SubElement(root, "par")
par.extend([megido.make_bg(args.bg, duration)])
seq = ET.SubElement(par, "seq")
seq.extend(children)

clip = thala2.Video(colorBGR=(0, 0, 0, 255)).encode(root)
clip.write_videofile(
    "example/20220417_222209.py.mp4",
    fps=args.fps,
    verbose=False,
    logger=None)
