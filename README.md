# FuzzImageMagick
Sample files for fuzzing ImageMagick

## ImageMagick Build instructions:##

### Vanilla Build: ###

    CC=afl-clang-fast CXX=afl-clang-fast++ ./configure && make

### Minimize Shared libraries  + ASAN ###
    AFL_USE_ASAN=1 AFL_HARDEN=1 CC=afl-clang-fast CXX=afl-clang-fast++ ./configure --with-bzlib=no --with-djvu=no --with-dps=no --with-fftw=no --with-fpx=no --with-fontconfig=no --with-freetype=no --with-gvc=no --with-jbig=no --with-jpeg=no --with-lcms=no --with-lqr=no --with-ltdl=no --with-lzma=no --with-openexr=no --with-openjp2=no --with-pango=no --with-png=no --with-tiff=no --with-wmf=no --with-x=no --with-xml=no --with-zlib=no --enable-hdri=no --enable-shared=no && AFL_USE_ASAN=1 AFL_HARDEN=1 make

## AFL command ##

    afl-fuzz -m none -i "samples" -o "imagemagick_fuzz_results" magick @@ /dev/null
