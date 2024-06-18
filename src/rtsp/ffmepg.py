import time
from multiprocessing import Process
import subprocess
import shlex
import sys
import threading
import numpy as np
import math
from typing import Tuple, Any
sys.path.append("../")
import cv2

def FFmpegRead(
    url: str,
    height: int,
    width: int,
    gpu: int,
    ) -> Tuple[subprocess.Popen, int]:
    
    IN_HEIGHT = height
    IN_WIDTH  = width
    gpuDevice = gpu
    videoSrc  = url

    cmd = f"""
    ffmpeg
    -rtsp_transport tcp
    -hwaccel cuda
    -hwaccel_device {gpuDevice}
    -i {videoSrc}
    -preset fast
    -tune hq
    -timeout 300000
    -reconnect 1
    -reconnect_streamed 1
    -reconnect_delay_max 300
    -vf scale={IN_WIDTH}:{IN_HEIGHT}
    -f rawvideo
    -pix_fmt bgr24
    -
    """
    cmd = shlex.split(cmd)
    data_size = IN_HEIGHT * IN_WIDTH * 3

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
    return process, data_size

def FFmpegStream(
    height: int,
    width: int,
    gpu: int,
    stream_address: str,
    name: str,
    codec: str,
    ) -> subprocess.Popen:
    
    IN_HEIGHT = height
    IN_WIDTH  = width
    gpuDevice = gpu
    FPS  = 30
    ENCODER = codec
    STREAM_ADDRESS = stream_address
    NAME = name

    cmd = f"""
    ffmpeg
    -re
    -hwaccel cuda
    -hwaccel_device {gpuDevice}
    -f rawvideo
    -pix_fmt rgb24
    -s {IN_WIDTH}x{IN_HEIGHT}
    -r {FPS}
    -i -
    -vcodec {ENCODER}
    -preset fast
    -tune hq
    -maxrate 4000k
    -timeout 300000
    -reconnect 1
    -reconnect_streamed 1
    -reconnect_delay_max 300
    -g 60
    -f rtsp
    -rtsp_transport tcp
    {STREAM_ADDRESS}/{NAME}
    """
    cmd = shlex.split(cmd)
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
    return process
