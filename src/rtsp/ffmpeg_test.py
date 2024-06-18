import subprocess
import shlex
import multiprocessing
from multiprocessing import Process, Queue
import time
import sys
sys.path.append("../")
from rtsp import FFmpegRead, FFmpegStream

def stream_rtsp(url: str, height: int, width: int, gpu: int, stream_address: str, name: str, codec: str):
    read_queue = Queue()

    process_read = Process(
        target=FFmpegRead,
        args=(
            url,
            height,
            width,
            gpu,
            read_queue,
            )
    )
    
    process_stream = Process(
        target=FFmpegStream,
        args=(height,
              width,
              gpu,
              stream_address,
              name,
              codec,
              read_queue,
              )
    )

    process_read.start()
    process_stream.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user, stopping...")
    finally:
        read_queue.put(None)
        process_read.terminate()
        process_stream.terminate()
        process_read.join()
        process_stream.join()
        print("Processes terminated.")

if __name__ == "__main__":
    url = "rtsp://admin:qazwsx123!@192.168.10.70:554/0/onvif/profile2/media.smp"
    height = 1080
    width = 1920
    gpu = 0
    stream_address = "rtsp://localhost:8444"
    name = "test"
    codec = "h264_nvenc"
    
    stream_rtsp(url, height, width, gpu, stream_address, name, codec)
