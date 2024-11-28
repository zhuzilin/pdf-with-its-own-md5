import os
from fontforge import *

nums = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
letters = ["A", "B", "C", "D", "E", "F"]

if not os.path.isdir("./raw_nums_bmp"):
    os.makedirs("./raw_nums_bmp")

font = open("./JetBrainsMono-Medium.ttf")

for glyph in font:
    if font[glyph].isWorthOutputting():
        # font[glyph].export('./out/' + font[glyph].glyphname + ".png", 128)
        name = str(font[glyph].glyphname)
        try:
            idx = nums.index(name)
            font[glyph].export("./raw_nums_bmp/{}.bmp".format(idx + 1), 128)
        except:
            pass
        try:
            letters.index(name)
            font[glyph].export("./raw_nums_bmp/{}.bmp".format(name), 128)
        except:
            pass
