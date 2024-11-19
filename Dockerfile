FROM nvcr.io/nvidia/pytorch:23.01-py3

ENV TZ=Asia/Seoul
ENV DEBIAN_FRONTEND=noninteractive

ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

COPY . /cctv-streaming-web-dashboard_python/

RUN bash /cctv-streaming-web-dashboard_python/setting-scripts/install_dependencies.sh
RUN bash /cctv-streaming-web-dashboard_python/setting-scripts/install_ffmpeg.sh
RUN bash /cctv-streaming-web-dashboard_python/setting-scripts/install_pip.sh
RUN bash /cctv-streaming-web-dashboard_python/setting-scripts/install_OpenCV.sh
