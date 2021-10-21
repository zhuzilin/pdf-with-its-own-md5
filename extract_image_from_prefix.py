import os

SOF = b"\xff\xd8"
EOF = b"\xff\xd9"

digit = 4

for i in range(16):
    with open(f"prefix_{digit}/prefix_15_{i}.txt", "rb") as f:
        data = bytearray(f.read())

    if digit == 1:
        data = SOF + SOF.join(data.split(SOF)[1:])
    else:
        data = data.split(b"stream\n")[-1]
    data = EOF.join(data.split(EOF)[:-1]) + EOF

    if not os.path.exists(f"processed/{digit}/"):
        os.mkdir(f"processed/{digit}/")
    if i < 10:
        val = str(i)
    else:
        val = "ABCDEF"[i - 10]
    with open(f"processed/{digit}/{val}.jpg", "wb") as f:
        f.write(data)


