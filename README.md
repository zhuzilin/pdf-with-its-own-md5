# PDF template that contains its own MD5

## Install HashClash

```bash
git clone git@github.com:cr-marcstevens/hashclash.git
cd hashclash
./build.sh
```

## 生成初始 prefix

为了获取最初的 pdf header，需要先编译一下 main.tex

```
cd tex
pdflatex main.tex
```

然后去提取图片前面的 pdf header：

```
python3 extract_headers.py
```

会保存 `header` 和 `mid_header_{i}` 在 `headers` 目录备用。


得到相同大小的图片之后，先生成一次 pdf，输出最初的 prefix：

```bash
python3 get_prefix.py
```

得到的 `prefix_0/prefix.txt` 是最初的不包含任何数字的前缀，由 pdf header + padding 组成。注意需要把 header 中的图片的大小（Length）替换为生成的图片的大小。`prefix_0/get_prefix.py` 中就是进行的这样的处理。

之后在 hashclash 的目录中运行 `prefix_loop.py`：

```
cd hashclash/ipc_workdir
python ~/md5-pdf-hashquine/prefix_loop.py
```

就可以依次在 `prefix_1`, `prefix_2`, ... `prefix_15` 等目录中得到对应的 collision 文件以及 prefix。

然后用 `extract_image_from_prefix.py` 得到每一位的图片，图片保存于 `processed/{i}/{j}.jpg`。这里为了方便调试，`extract_image_from_prefix.py` 每次只会处理单一一位的 16 张图片，所以请手动修改 `extract_image_from_prefix.py` 中的 `digit` 参数：

```
python3 extract_image_from_prefix.py --digit=3
```

最后，进入 `tex` 目录，在 `main.tex` 中修改最上方 32 位对应的值，即可得到一个包含自己 md5 的 pdf。


## 注意事项：

- 使用 pdf 一次放入 jpg，而不是合成一整个 jpg。

- 为了让 pdf 的 header 保持不变，需要保证所有图片的大小相同。

- hashclash 有时会卡死，可以直接杀死重试。如果多次重试都会卡死，可以通过修改 `script/poc_no.sh` 中的 `data` 值来重新运行。
