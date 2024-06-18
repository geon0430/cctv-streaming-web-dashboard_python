#!/bin/bash

IMAGE_NAME="webrtc_python"
TAG="0.1"

docker build --no-cache -t ${IMAGE_NAME}:${TAG} .
