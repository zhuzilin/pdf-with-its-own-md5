with open("tex/main.pdf", "rb") as f:
    data = bytearray(f.read())

header = data.split(b"\xff\xd8")[0]

print(header)
with open("headers/header", "wb") as f:
    f.write(header)

mid_headers = []
for i in range(1, 32):
    mid_headers.append(b"\nendstream" + data.split(b"\nendstream")[i].split(b"stream\n")[0] + b"stream\n")
    print("")
    print(mid_headers[-1])

for i in range(0, 31):
    with open(f"headers/mid_header_{i}", "wb") as f:
        f.write(mid_headers[i])
