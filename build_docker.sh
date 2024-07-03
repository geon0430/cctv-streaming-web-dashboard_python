#!/bin/bash

IMAGE_NAME="webrtc_python"
TAG="0.2"

docker build --no-cache -t ${IMAGE_NAME}:${TAG} .
