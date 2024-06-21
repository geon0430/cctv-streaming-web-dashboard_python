FROM ubuntu:latest

ENV TZ=Asia/Seoul
ENV DEBIAN_FRONTEND=noninteractive

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

COPY . /webrtc_python/

RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.8 python3.8-dev python3.8-distutils && \
    apt-get install -y python3-pip && \
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1

RUN ln -s $(which python3) /usr/bin/python
RUN bash /webrtc_python/setting-scripts/install_ffmpeg.sh
RUN bash /webrtc_python/setting-scripts/install_dependencies.sh
RUN bash /webrtc_python/setting-scripts/install_pip.sh
RUN bash /webrtc_python/setting-scripts/install_OpenCV.sh

