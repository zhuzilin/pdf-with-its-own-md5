import os
import io
import PIL.Image as Image

# https://en.wikipedia.org/wiki/JPEG
SOI = b"\xff\xd8"   # start of image
EOI = b"\xff\xd9"   # end of image
COM = b"\xff\xfe"

# Only support SOF0 and SOF2 introduced in the wikipage,
# there are a lot more in PIL.
SOF0 = b"\xff\xc0"  # start of frame (baseline DCT)
SOF2 = b"\xff\xc2"  # start of frame (progressive DCT)

SOS = b"\xff\xda"   # start of scan

# In PIL encoder
ZZZZ = b"\x00\x00"
# 0xFFFF is used as padding purposes
PADDING = b"\xff\xff"

frame = (
    SOF0 + (8).to_bytes(length=2, byteorder="big") +
    (8).to_bytes(length=1, byteorder="big") +  #  bits
    (32).to_bytes(length=2, byteorder="big") +  # width
    (16).to_bytes(length=2, byteorder="big") +  # height
    (3).to_bytes(length=1, byteorder="big") + # layers (mode)

    (0).to_bytes(length=65536, byteorder="big")
)

scan = (
    SOS
)

def image(str):
    return SOI + str + EOI

array = bytearray(image(frame + scan))

im = Image.open(io.BytesIO(array), formats=["JPEG"])
im.show()

im.save("img.jpg", format="JPEG")