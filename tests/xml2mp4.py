import thala2
import xml.etree.ElementTree as ET
from datetime import datetime as DT
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("xmlfile")
args = parser.parse_args()
print(args.xmlfile)

root = ET.parse(args.xmlfile).getroot()

clip = thala2.Video(colorBGR=(0, 0, 0, 255)).encode(root)
clip.write_videofile(args.xmlfile+".mp4", fps=16.0, verbose=False, logger=None)

