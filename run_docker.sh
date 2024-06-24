#!/bin/bash

port_num="1"
CONTAINER_NAME="geon_webrtc_python"
IMAGE_NAME="webrtc_python"
TAG="0.1"

webrtc_python_path=$(pwd)

docker run \
    --runtime nvidia \
    --gpus all \
    -it \
    -p ${port_num}2888:8888 \
    -p ${port_num}2444:8444 \
    -p ${port_num}2555:8555 \
    -p ${port_num}2554:8554 \
    -p ${port_num}2000:9000 \
    --name ${CONTAINER_NAME} \
    --privileged \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ${webrtc_python_path}:/webrtc_python \
    -e DISPLAY=$DISPLAY \
    --shm-size 20g \
    --restart=always \
    -w /webrtc_python \
    ${IMAGE_NAME}:${TAG}
