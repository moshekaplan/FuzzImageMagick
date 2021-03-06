# FuzzImageMagick
Full setup for fuzzing ImageMagick. Currently (2016-02-07) covers over 30% of the codebase.

## 1. Download ImageMagick
    git clone https://github.com/ImageMagick/ImageMagick.git --depth 1

## 2. Build ImageMagick

### Vanilla Build:

    CC=afl-clang-fast CXX=afl-clang-fast++ ./configure && make

### Minimize Shared libraries + AFL_HARDEN
    AFL_HARDEN=1 CC=afl-clang-fast CXX=afl-clang-fast++ ./configure --with-bzlib=no --with-djvu=no --with-dps=no --with-fftw=no --with-fpx=no --with-fontconfig=no --with-freetype=no --with-gvc=no --with-jbig=no --with-jpeg=no --with-lcms=no --with-lqr=no --with-lzma=no --with-openexr=no --with-openjp2=no --with-pango=no --with-png=no --with-tiff=no --with-raqm=no --with-webp=no --with-wmf=no --with-x=no --with-xml=no --with-zlib=no --enable-hdri=no --enable-shared=no && AFL_HARDEN=1 make

## 3. Fuzz with AFL

    afl-fuzz -m none -i "samples" -o "imagemagick_fuzz_results" magick @@ /dev/null
    
## Additional Notes:
### Cleaning temporary files
ImageMagick creates temporary files while running. If ImageMagick crashes, the temporary files are not cleaned up. To prevent the fuzzing machine's hard disk from filling up, you can create a cron job to run `rm /tmp/magick-*` every hour. For more discussion about this issue, see [this](https://github.com/ImageMagick/ImageMagick/issues/139) bug report.

### Limiting number of threads
http://www.imagemagick.org/discourse-server/viewtopic.php?t=20756#p83480

Via arguments: `-limit thread 1` , via env vars: `MAGICK_THREAD_LIMIT=1` 

### Avoid Fuzzing Delegates
Remove all delegates from: `config/delegates.xml.in` before running `./configure`
