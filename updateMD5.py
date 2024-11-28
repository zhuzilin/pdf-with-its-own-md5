# -*- coding:utf-8 -*-
import re
import hashlib

TEX_FILE_NAME = "./main.tex"
PDF_FILE_NAME = "./main.pdf"
TEX_FILE_BACKUP_NAME = "./main.bak.tex"

lineID = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]

with open(TEX_FILE_NAME, "rb") as f:
    data_bin = f.read()
    with open(TEX_FILE_BACKUP_NAME, "wb") as f_bak:
        f_bak.write(data_bin)
    data = data_bin.decode("UTF-8")

try:
    with open(PDF_FILE_NAME, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest().upper()
except:
    md5 = "00000000000000000000000000000000"

# print(data)
print("md5: " + md5)

numList = re.search(
    "(.*)START MD5 IMAGE RESOURCES.*END MD5 IMAGE RESOURCES(.*)", data, re.S | re.M
)
if len(numList.groups()) == 2:
    result = [
        numList.group(1),
        "START MD5 IMAGE RESOURCES\n",
        "%----------------------------------------------------------------------------------------\n",
        "%	MD5: {}\n".format(md5),
        "%----------------------------------------------------------------------------------------\n",
    ]
    for i in range(32):
        result.append(
            "\\immediate\\pdfximage height 7pt {processed/"
            + str(i + 1)
            + "/"
            + md5[i]
            + ".jpg}\n\edef\\num"
            + lineID[i]
            + "{\\kern 0pt \\pdfrefximage\\the\\pdflastximage}\n"
        )
    # for i in range(0, 32):
    #     result.append(
    #         "\\immediate\\pdfximage height 7pt {raw_nums/"
    #         + md5[i]
    #         + ".jpg}\n\edef\\num"
    #         + lineID[i]
    #         + "{\\kern 0pt \\pdfrefximage\\the\\pdflastximage}\n"
    #     )
    result.append("\n")
    result.append(
        "\\edef\\blockA{\\numa{}\\numb{}\\numc{}\\numd{}\\nume{}\\numf{}\\numg{}\\numh{}}\n"
    )
    result.append(
        "\\edef\\blockB{\\numi{}\\numj{}\\numk{}\\numl{}\\numm{}\\numn{}\\numo{}\\nump{}}\n"
    )
    result.append(
        "\\edef\\blockC{\\numA{}\\numB{}\\numC{}\\numD{}\\numE{}\\numF{}\\numG{}\\numH{}}\n"
    )
    result.append(
        "\\edef\\blockD{\\numI{}\\numJ{}\\numK{}\\numL{}\\numM{}\\numN{}\\numO{}\\numP{}}\n"
    )
    result.append("\n")
    result.append("\\edef\\MDFIVE{\\blockA{}\\blockB{}\\blockC{}\\blockD{}}\n")
    result.append(
        "%----------------------------------------------------------------------------------------\n"
    )
    result.append("%	END MD5 IMAGE RESOURCES")
    result.append(numList.group(2))

    with open(TEX_FILE_NAME, "wb") as f:
        f.write("".join(result).encode("UTF-8"))
else:
    print("Format error!")
