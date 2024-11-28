import os


BASE_DIR = os.path.dirname(os.path.realpath(__file__))

SOF = b"\xff\xd8"
EOF = b"\xff\xd9"


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

def pad(data):
    if len(data) % 64 == 0:
        data += b"\xff\xfe\x00\x05\x00\x00\x00\xff\xfe\x00\x77\x00"
    else:
        data += b"\xff\xfe"
        n = 64 - len(data) % 64 + 12 - 5
        data += to_bytes(n)
        data += to_bytes(0, len=n-2)
        data += b"\xff\xfe\x00\x77\x00"
    return data


def reset_length_in_header(data, header):
    image_lens = []
    for i in range(16):
        val = str(i)
        if i > 9:
            val = "ABCDEF"[i - 10]
        image = f"{BASE_DIR}/raw_nums/{val}.jpg"
        with open(image, "rb") as f:
            img_data = f.read()
            image_lens.append((val, len(img_data)))

    while True:
        old_header = header
        print("old_header:", old_header)
        prefix_len = len(data) + len(old_header)
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
            print(f"{val} mid img len:", prefix_len - len(old_header) - len(data))
        generated_image_len = prefix_len - len(old_header) - len(data)
        print(generated_image_len)
        header_segs = old_header.split(b"\n")
        header_segs[-6] = bytes(f"/Length {generated_image_len}", 'utf-8')
        header = b"\n".join(header_segs)
        print(len(header), len(old_header))
        if len(header) == len(old_header):
            break
    return header


def pad_header(header):
    if len(header) % 64 == 0:
        header += b"\xff\xd8\xff\xfe\x00\x03\x00\xff\xfe\x00\x77\x00"
    else:
        header += b"\xff\xd8\xff\xfe"
        n = 64 - len(header) % 64 + 12 - 5
        header += to_bytes(n)
        header += to_bytes(0, len=n-2)
        header += b"\xff\xfe\x00\x77\x00"
    return header


for i in range(32):
    if not os.path.exists(f"{BASE_DIR}/prefix_{i+1}"):
        os.mkdir(f"{BASE_DIR}/prefix_{i+1}")
    j = 0
    while j < 16:
        print(f"Step {j} of loop {i} started...")
        if j < 10:
            img_name = f"{j}.jpg"
        else:
            val = "ABCDEF"[j - 10]
            img_name = f"{val}.jpg"
        if os.path.exists(f"{BASE_DIR}/prefix_{i + 1}/{img_name}"):
            print(f"{img_name} exists. Skip step.")
            j += 1
            continue
        if j == 0:
            prefix_filename = f"{BASE_DIR}/prefix_{i}/prefix.txt"
        else:
            prefix_filename = f"{BASE_DIR}/prefix_{i + 1}/prefix_{j - 1}_{j}.txt"

        prefix = read_bytes(prefix_filename)

        # The hashclash need to copy the prefix file to the ipc_workdir directory...
        print(f"cp {prefix_filename} prefix.txt")
        os.system(f"cp {prefix_filename} prefix.txt")
        print('sh ~/hashclash/scripts/generic_ipc.sh prefix.txt')
        os.system(f'sh ../scripts/generic_ipc.sh prefix.txt')
        col1_path = f"{BASE_DIR}/prefix_{i + 1}/collision_{j}_1.bin"
        col2_path = f"{BASE_DIR}/prefix_{i + 1}/collision_{j}_2.bin"
        os.system(f"cp collision1.bin {col1_path}")
        os.system(f"cp collision2.bin {col2_path}")

        prev_prefix = {}
        for k in range(j):
            print(f"{BASE_DIR}/prefix_{i + 1}/prefix_{j - 1}_{k}.txt")
            prev_prefix[k] = read_bytes(f"{BASE_DIR}/prefix_{i + 1}/prefix_{j - 1}_{k}.txt")
            assert len(prev_prefix[k]) == len(prefix), f"{len(prev_prefix)} vs {len(prefix)}"

        col1 = read_bytes(col1_path)
        com_len1 = comment_len(col1)
        col2 = read_bytes(col2_path)
        com_len2 = comment_len(col2)
        print(com_len1, com_len2)

        assert com_len1 < com_len2

        for k in prev_prefix:
            print(len(col1), len(prefix), len(col1[len(prefix):]))
            prev_prefix[k] += col1[len(prefix):]
            assert len(prev_prefix[k]) == len(col1), f"{len(prev_prefix[k])} vs {len(col1)}"
            assert len(prev_prefix[k]) == len(col2)

        # remove the starting 0xff0xd8
        fig = read_bytes(f"{BASE_DIR}/raw_nums/{img_name}")[2:]

        mid = to_bytes(0, com_len1)
        mid += b"\xff\xfe"
        n = 256 - 2 + len(fig)
        # 2 is the 0xff0xfe
        mid += to_bytes(n)
        mid += to_bytes(0, 256 - 4)

        data1 = col2 + mid + fig
        data2 = col1 + mid + fig

        for k in prev_prefix:
            prev_prefix[k] += mid + fig
            assert len(data1) == len(prev_prefix[k]), f"{len(data1)} vs {len(prev_prefix[k])}"
            assert len(data2) == len(prev_prefix[k])

        image = b"\xff\xd8" + b"\xff\xd8".join(data1.split(b"\xff\xd8")[1:])
        with open(f"{BASE_DIR}/prefix_{i + 1}/{img_name}", "wb") as f:
            f.write(image)

        data1 = pad(data1)
        data2 = pad(data2)
        assert (len(data1) - 12) % 64 == 0
        assert (len(data2) - 12) % 64 == 0
        for k in prev_prefix:
            prev_prefix[k] = pad(prev_prefix[k])
            assert (len(prev_prefix[k]) - 12) % 64 == 0

        with open(f"{BASE_DIR}/prefix_{i + 1}/prefix_{j}_{j}.txt", "wb") as f:
            f.write(data1)

        with open(f"{BASE_DIR}/prefix_{i + 1}/prefix_{j}_{j + 1}.txt", "wb") as f:
            f.write(data2)

        for k in prev_prefix:
            with open(f"{BASE_DIR}/prefix_{i + 1}/prefix_{j}_{k}.txt", "wb") as f:
                f.write(prev_prefix[k])

        j += 1
    # Need to get a new prefix for the next round.
    with open(f"{BASE_DIR}/headers/mid_header_{i}", "rb") as f:
        mid_header = bytearray(f.read())
    with open(f"{BASE_DIR}/prefix_{i + 1}/prefix_15_0.txt", "rb") as f:
        data = bytearray(f.read())
        data = EOF.join(data.split(EOF)[:-1]) + EOF
    new_mid_header = reset_length_in_header(data, mid_header)
    print(new_mid_header)
    header = data + new_mid_header
    header = pad_header(header)
    with open(f"{BASE_DIR}/prefix_{i + 1}/prefix.txt", "wb") as f:
        f.write(header)
