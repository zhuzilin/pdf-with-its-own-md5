import io
from PIL import Image

def read_bytes(filename):
    with open(filename, "rb") as f:
        data = bytearray(f.read())
    return data


def comment_len(prefix):
    assert len(prefix) % 64 == 0
    block_start = len(prefix) - 128

    return int.from_bytes(prefix[block_start + 9:block_start + 11], byteorder="big") - (128 - 9)

def to_bytes(n, len=2):
    return (n).to_bytes(length=len, byteorder="big")

prefix1 = read_bytes("collision/collision1.bin")
com_len1 = comment_len(prefix1)
prefix2 = read_bytes("collision/collision2.bin")
com_len2 = comment_len(prefix2)

print(com_len1, com_len2)

assert com_len1 + 2 < com_len2

filename = "0"

fig1 = read_bytes(f"raw_nums/{filename}.jpg")
# remove the starting 0xff0xd8
fig1 = fig1[2:]
len1 = len(fig1)

mid = to_bytes(0, com_len1)

mid += b"\xff\xfe"
n = 256 - 2 + fig1

# 2 is the 2 
mid += to_bytes(0, n - 2)


data1 = prefix2 + mid + fig1
data2 = prefix1 + mid + fig1


with open(f"prefix/00.txt", "wb") as f:
    f.write(data1)

image = b"\xff\xd8" + b"".join(data1.split(b"\xff\xd8")[1:])
with open(f"prefix/0.jpg", "wb") as f:
    f.write(image)

with open(f"prefix/01.txt", "wb") as f:
    f.write(data2)
