#!/bin/bash

port_num="1"
CONTAINER_NAME="webrtc_python"
IMAGE_NAME="webrtc_python"
TAG="0.1"

webrtc_python_path=$(pwd)

docker run \
    --runtime nvidia \
    --gpus all \
    -it \
    -p ${port_num}2000:7000 \
    -p ${port_num}2888:8888 \
    -p ${port_num}2444:8444 \
    -p ${port_num}4000:9000 \
    -p ${port_num}3000:8000 \
    --name ${CONTAINER_NAME} \
    --privileged \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ${webrtc_python_path}:/webrtc_python \
    -e DISPLAY=$DISPLAY \
    --shm-size 20g \
    --restart=always \
    -w /webrtc_python \
    ${IMAGE_NAME}:${TAG}
