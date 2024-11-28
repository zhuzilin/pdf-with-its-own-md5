# PDF template with its own MD5

MD5 is a famous cryptographic hash function that was proved to be insecure by Xiaoyun Wang's team in 2004. Due to its insecurity, we could create a pdf that shows its own MD5. However, it's time consuming to create a pdf with its MD5 and that's what this project is for.

![example](doc/example.webp)

[`main.pdf`](./main.pdf) is a example of the template.

## Usage

1. Install pdflatex.

    The header of pdf varies among pdflatex versions. To use the processed figures directly, please install the following pdflatex (MacTex in my case):

    ```bash
    >> pdflatex -v
    pdfTeX 3.141592653-2.6-1.40.24 (TeX Live 2022)
    kpathsea version 6.3.4
    Copyright 2022 Han The Thanh (pdfTeX) et al.
    There is NO warranty.  Redistribution of this software is
    covered by the terms of both the pdfTeX copyright and
    the Lesser GNU General Public License.
    For more information about these matters, see the file
    named COPYING and the pdfTeX source.
    Primary author of pdfTeX: Han The Thanh (pdfTeX) et al.
    Compiled with libpng 1.6.37; using libpng 1.6.37
    Compiled with zlib 1.2.11; using zlib 1.2.11
    Compiled with xpdf version 4.03
    ```

2. Create your own pdf starting from `main.tex`.

    You could change the content in the `main.tex` to whatever you want, as long as you keep the images in the header part. Those code will insert the binary of the figures right after the header of pdf, from which the figures are created.

    Right now, the `main.tex` is almost the starter code of overleaf.

3. Compile `main.tex` to get `main.pdf` files.

    you could compile the `main.tex` with:

    ```bash
    pdflatex main.tex
    ```

    and this generate the `main.pdf`.

4. Modify the images used in `main.tex` to match the MD5 of `main.pdf`.

    * You can use scripts to do this automatically:

        ```bash
        python3 ./updateMD5.py
        ```

    * Or you can do this manually:

        * First you need to calculate the MD5 of `main.tex` with:

        ```bash
        md5sum main.pdf
        ```

        * And then you need to change the 32 figures in the header of `main.tex`.

5. Run `pdflatex main.tex` again. Now you have a PDF that shows its own MD5!


## Start from scratch

As you can guess, the mystery of the generated PDF files lie in the processed figures. They are caculated collisions of MD5. If you are using different version of pdflatex (or using overleaf), then the header (prefix) of the PDF are different, which will take the magic away from the figures. In those cases, or if you simply want to create your own figures, here are the steps:

1. Install HashClash

    * To generate the collision for MD5, we need to use the amazing [hashclash](https://github.com/cr-marcstevens/hashclash):

    * Requirements of Project HashClash
        - C++11 compiler (e.g. g++)
        - make
        - autoconf & automake & libtool

            `sudo apt-get install autoconf automake libtool`
        - zlib & bzip2 libraries

            `sudo apt-get install zlib1g-dev libbz2-dev`
        - Optional: CUDA (It will not be used in this project)

    * Building

        ```bash
        git clone git@github.com:cr-marcstevens/hashclash.git --depth=1
        cd hashclash
        ./build.sh
        ```

    * Note that file `boost_1_57_0.tar.gz` can be slow to download in some areas, in which case you can [download it yourself](https://nchc.dl.sourceforge.net/project/boost/boost/1.57.0/boost_1_57_0.tar.gz) and upload it to the root directory of `hashclash` before executing the installation script.

2. Create the raw digits.

    * You need to create images of the 16 possible values (0-9, A-F) as we have in `raw_nums` directory. All images must have the same resolution, as the resolution will be recorded in the metadata of PDF format. I will call them raw nums for now.

    * A method of extracting images from font files using fontforge

        * Install [fontforge](https://fontforge.org/)

        * Use `font2bmp.py` to get the BMP image of the required letters.

            ```bash
            # Remember to change the file name in the script
            ffpython ./font2bmp.py
            ```

        * Convert the BMP image in `raw_nums_bmp` to a JPEG image and move them to the directory `raw_nums`.

2. Prepare the header (prefix).

    * Then we need to prepare the prefix of the images. When using `\immediate\pdfximage` at the very start of a `.tex` file, the generated PDF will be:

        ```
        header -> images_0 -> mid_header_1 -> images_1 -> mid_header_2 -> ...
        ```

    * We need to extract the `header` and `mid_header_i` because they are part of the prefix of each images and will determine the generated collision.

    * To extract the headers, you should use the raw nums in main.tex and compile the files. Then, run `extract_headers.py`:

        ```bash
        # main.tex now only contains raw nums.
        pdflatex main.tex
        ```

    * The extracted headers will be in the `headers` folder.

2. Create the initial prefix.

    * The next step is to create the very first prefix with:

        ```bash
        python3 get_prefix_0.py
        ```

    * This will generate `prefix.txt` in `prefix_0` folder.

3. Run `prefix_loop.py`.

    * Enter the hashclash folder and run the `prefix_loop.py` there. The reason to go to the hashclash folder first is that I found the unicoll shell fails in other directory...

        ```bash
        cd ~/hashclash
        mkdir ipc_workdir
        cd ipc_workdir
        python3 ~/pdf-with-its-own-md5/prefix_loop.py
        ```

    * The script `prefix_loop.py` will gradually create the `prefix_1`, `prefix_2`, ..., `prefix_32`. Note that the script can be restarted at any time. We need to sequntially make 16 collision for each digit, and after the i-th collision of digit j finished, there will be a `i.jpg` file in the `prefix_j`. This is not the image we need at last, but `prefix_loop.py` will detect them to know the current progress. And you can delete the certain image to retry that collision.

    * The `script/poc_no.sh` script we use in `hashclash` will stuck sometime. You can kill the process and change the `data` value in `poc_no.sh` and restart the `prefix_loop.py`. Another way to solve the stuck is remove the last generated jpg in the folder.

    * You might get the error `../scripts/poc_no.sh: 49: function: not found`, that can be resolved by modifying `auto_kill_connect` function in `script/poc_no.sh` like this:

        ```
        auto_kill_connect()
        {
            pidfile="$1"
            while [ ! -s data/bestpath.bin.gz ]; do
                sleep 1
            done
            sleep 10
            if [ "$pidfile" != "" ]; then
                if [ -s "$pidfile" ]; then
                    echo "Found differential paths, killing md5diffpathconnect"
                    pkill -F $pidfile
                fi
            fi
        }
        ```

4. Extract the processed nums.

    * Use `extract_image_from_prefix.py` to extract the image for digits. The script will only extract one digit at a time, for example:

        ```bash
        python3 extract_image_from_prefix.py --digit=3
        ```

    * will extract the processed 16 figures for digit 3 and save them to `processed/3/`.

    * After extracting the all 32 digits, you will get your version of the processed figures. Now you can create the PDF with its MD5 with them.

## Acknowlegement

This project is created with the repo or article from following links:

1. cr-marcstevens/hashclash https://github.com/cr-marcstevens/hashclash
2. corkami/collisions https://github.com/corkami/collisions
3. PoC||GTFO issue 14 https://www.alchemistowl.org/pocorgtfo/pocorgtfo14.pdf
4. 能否构造一个含有自己哈希或MD5等的文件？ - 某某的回答 - 知乎 https://www.zhihu.com/question/411191287/answer/1384197672
