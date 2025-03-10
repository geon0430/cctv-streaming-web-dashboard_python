#!/bin/bash

set -ex

WORKDIR="/ffmpeg"
mkdir -p ${WORKDIR} && cd ${WORKDIR}

git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git
cd nv-codec-headers
git checkout sdk/12.0
make -j$(nproc) && make install
ldconfig
cd ..

git clone https://git.ffmpeg.org/ffmpeg.git ffmpeg
cd ffmpeg

apt-get update
apt-get install -y --no-install-recommends \
    software-properties-common \
    libx264-dev \
    libx265-dev

./configure \
    --enable-nonfree --enable-gpl \
    --enable-libx264 --enable-ffnvcodec \
    --enable-cuda-nvcc --enable-libnpp \
    --extra-cflags=-I/usr/local/cuda/include \
    --extra-ldflags=-L/usr/local/cuda/lib64 \
    --disable-static --enable-shared

make -j$(nproc) && make install
ldconfig

cd /
rm -rf ${WORKDIR}