header = b"\xff\xd8\xff\xfe\x00\x02"

def read_bytes(filename):
    with open(filename, "rb") as f:
        data = bytearray(f.read())
    return data

data = read_bytes("raw_nums/0.jpg")

new_data = header + data[2:]

with open("overleaf.jpg", "wb") as f:
    f.write(new_data)

from PIL import Image

im = Image.open("overleaf.jpg")
im.show()
