#!/bin/bash

port_num="1"
CONTAINER_NAME="cctv-streaming-web-dashboard_python"
IMAGE_NAME="cctv-streaming-web-dashboard_python"
TAG="0.1"

code_path=$(pwd)

docker run \
    --runtime nvidia \
    --gpus all \
    -it \
    -p ${port_num}3888:8888 \
    -p ${port_num}3444:8444 \
    -p ${port_num}3555:8555 \
    -p ${port_num}3554:8554 \
    -p ${port_num}3000:8000 \
    -p ${port_num}4000:9000 \
    --name ${CONTAINER_NAME} \
    --privileged \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ${code_path}:/cctv-streaming-web-dashboard_python \
    -e DISPLAY=$DISPLAY \
    --shm-size 20g \
    --restart=always \
    -w /cctv-streaming-web-dashboard_python \
    ${IMAGE_NAME}:${TAG}
