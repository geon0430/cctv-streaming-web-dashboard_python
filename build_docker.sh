#!/bin/bash

IMAGE_NAME="cctv-streaming-web-dashboard_python"
TAG="0.1"

docker build --no-cache -t ${IMAGE_NAME}:${TAG} .
