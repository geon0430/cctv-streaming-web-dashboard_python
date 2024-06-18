import time
from multiprocessing import Process, Queue 
import subprocess
import shlex
import sys
import threading

def FFmpegRead(url: str, height: int, width: int, gpu: int, queue: Queue):
    cmd = f"""
    ffmpeg
    -rtsp_transport tcp
    -hwaccel cuda
    -hwaccel_device {gpu}
    -i {url}
    -preset fast
    -tune hq
    -timeout 300000
    -reconnect 1
    -reconnect_streamed 1
    -reconnect_delay_max 300
    -vf scale={width}:{height}
    -f rawvideo
    -pix_fmt rgb24
    -
    """
    cmd = shlex.split(cmd)  
    data_size = height * width * 3
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

    try:
        while True:
            raw_image = process.stdout.read(data_size)
            if not raw_image:
                break
            queue.put(raw_image)
    except Exception as e:
        print(f"Error in FFmpegRead: {e}")
    finally:
        queue.put(None)
        process.stdout.close()
        process.terminate()
        stderr_output = process.stderr.read().decode()
        print(f"FFmpegRead stderr: {stderr_output}")

def FFmpegStream(height: int, width: int, gpu: int, stream_address: str, name: str, codec: str, queue: Queue):
    cmd = f"""
    ffmpeg
    -re
    -hwaccel cuda
    -hwaccel_device {gpu}
    -f rawvideo
    -pix_fmt rgb24
    -s {width}x{height}
    -r 30
    -i -
    -vcodec {codec}
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
    {stream_address}/{name}
    """
    cmd = shlex.split(cmd)
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

    try:
        while True:
            if not queue.empty():
                data = queue.get()
                if process.poll() is not None:
                    raise Exception("FFmpeg process terminated unexpectedly")
                process.stdin.write(data)
                process.stdin.flush()
                print(f"FFmpegStream | Streaming {len(data)} bytes of data.")
                time.sleep(0.03)
    except Exception as e:
        print(f"Error in FFmpegStream: {e}")
    finally:
        try:
            if process.stdin:
                process.stdin.close()
        except BrokenPipeError:
            pass
        process.terminate()
        stderr_output = process.stderr.read().decode()
        print(f"FFmpegStream stderr: {stderr_output}")