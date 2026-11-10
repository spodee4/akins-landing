#!/usr/bin/env python3
"""Scan-proof a transparent QR PNG: composite it on several print backgrounds and sizes, blur it,
and decode with two independent readers (zxing-cpp, OpenCV). Exit 1 on any miss or wrong URL.

usage: verify_qr.py <png> <expected-url>

capability: render:branded_qr e6585cb1b83f
"""
import sys

import cv2
import numpy as np
import zxingcpp
from PIL import Image, ImageFilter

BACKGROUNDS = {"white": (255, 255, 255), "ad-yellow": (255, 221, 0), "cream": (247, 245, 240),
               "kraft": (214, 190, 150)}
SIZES = [1200, 400, 200, 120]   # px; 120 px ~ 1 inch at 120 dpi phone-photo resolution


def readers(img):
    out = set()
    for r in zxingcpp.read_barcodes(img):
        out.add(("zxing", r.text))
    arr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    text, _, _ = cv2.QRCodeDetector().detectAndDecode(arr)
    if text:
        out.add(("opencv", text))
    return out


def main():
    png, url = sys.argv[1], sys.argv[2]
    src = Image.open(png).convert("RGBA")
    fails = 0
    for bname, rgb in BACKGROUNDS.items():
        for px in SIZES:
            canvas = Image.new("RGB", src.size, rgb)
            canvas.paste(src, mask=src)
            small = canvas.resize((px, px), Image.LANCZOS)
            for blur in (0, 1):
                img = small.filter(ImageFilter.GaussianBlur(blur)) if blur else small
                got = readers(img)
                zx = ("zxing", url) in got
                cvok = ("opencv", url) in got
                wrong = [t for _, t in got if t != url]
                ok = zx and cvok and not wrong
                fails += not ok
                print(f"{'PASS' if ok else 'FAIL'} bg={bname:9} {px:5}px blur={blur} zxing={zx} opencv={cvok}"
                      + (f" WRONG={wrong}" if wrong else ""))
    print("ALL PASS" if not fails else f"{fails} FAIL")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
