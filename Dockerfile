FROM nvcr.io/nvidia/pytorch:23.01-py3

ENV TZ=Asia/Seoul
ENV DEBIAN_FRONTEND=noninteractive

ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

COPY . /webrtc_python/

RUN bash /webrtc_python/setting-scripts/install_dependencies.sh
RUN bash /webrtc_python/setting-scripts/install_ffmpeg.sh
RUN bash /webrtc_python/setting-scripts/install_pip.sh
RUN bash /webrtc_python/setting-scripts/install_OpenCV.sh
