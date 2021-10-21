import os

with open("headers/header", "rb") as f:
    header = bytearray(f.read())

print(header)

def reset_length_in_header(header):
    image_lens = []
    for i in range(16):
        val = str(i)
        if i > 9:
            val = "ABCDEF"[i - 10]
        image = f"raw_nums/{val}.jpg"
        with open(image, "rb") as f:
            img_data = f.read()
            image_lens.append((val, len(img_data)))

    while True:
        old_header = header
        prefix_len = len(old_header)
        print("old_header:", old_header)
        for val, l in image_lens:
            # Before append image, pad prefix to 64N + 12
            if prefix_len % 64 == 0:
                prefix_len += 12
            else:
                prefix_len += 2  # 0xff0xfe
                prefix_len += 12 + 64 - prefix_len % 64
            print(f"{val} mid prefix len:", prefix_len)
            # hashclash will change the last 12 bytes to 128
            prefix_len += 128 - 12
            # add the middle empty string
            prefix_len += 256
            # append image, the 2 is 0xFF0xD8
            prefix_len += l - 2
            print(f"{val} mid img len:", prefix_len - len(old_header))
        generated_image_len = prefix_len - len(old_header)
        print(generated_image_len)
        header_segs = old_header.split(b"\n")
        header_segs[-6] = bytes(f"/Length {generated_image_len}", 'utf-8')
        header = b"\n".join(header_segs)
        print(len(header), len(old_header))
        if len(header) == len(old_header):
            break
    return header

header = reset_length_in_header(header)

def to_bytes(n, len=2):
    return (n).to_bytes(length=len, byteorder="big")

if len(header) % 64 == 0:
    header += b"\xff\xd8\xff\xfe\x00\x03\x00\xff\xfe\x00\x77\x00"
else:
    header += b"\xff\xd8\xff\xfe"
    n = 64 - len(header) % 64 + 12 - 5
    header += to_bytes(n)
    header += to_bytes(0, len=n-2)
    header += b"\xff\xfe\x00\x77\x00"

assert (len(header) - 12) % 64 == 0

print(bytearray(header))

if not os.path.exists("prefix_0"):
    os.mkdir("prefix_0")

with open("prefix_0/prefix.txt", "wb") as f:
    f.write(header)
