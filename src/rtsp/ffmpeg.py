import time
from multiprocessing import Queue, Process, Event
import subprocess
import shlex
import logging

def FFmpegRead(url: str, height: int, width: int, gpu: int, queue: Queue, stop_event: Event, logger: logging):
    while not stop_event.is_set():
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
        logger.info("FFmpegRead | Starting FFmpeg read process.")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

        try:
            while not stop_event.is_set():
                raw_image = process.stdout.read(data_size)
                if not raw_image:
                    logger.error("FFmpegRead Error | Data is not raw_image")
                    break
                queue.put(raw_image)
                logger.debug(f"FFmpegRead | Sent {len(raw_image)} bytes of data.")
                
        except Exception as e:
            logger.error(f"Error in FFmpegRead: {e}")
            print(f"Error in FFmpegRead: {e}")
            
        finally:
            process.stdout.close()
            process.terminate()
            logger.info("FFmpegRead | FFmpeg read process has completed.")
        
        time.sleep(5)
        logger.info("FFmpegRead | Restarting FFmpeg read process")

def FFmpegStream(height: int, width: int, gpu: int, stream_address: str, name: str, codec: str, queue: Queue, stop_event: Event, logger: logging):
    while not stop_event.is_set():
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
        logger.info("FFmpegStream | Starting FFmpeg stream process.")
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

        try:
            while not stop_event.is_set():
                if not queue.empty():
                    data = queue.get()
                    process.stdin.write(data)
                    process.stdin.flush()
                    logger.debug(f"FFmpegStream | Streaming {len(data)} bytes of data.")
                    
        except Exception as e:
            print(f"FFmpegStream Error | {e}")
            logger.error(f"FFmpegStream Error | {e}")
            
        finally:
            try:
                if process.stdin:
                    process.stdin.close()
            except BrokenPipeError:
                pass
            process.terminate()
            logger.info("FFmpegStream | FFmpeg stream process has completed.")
        
        time.sleep(5)
        logger.info("FFmpegStream | Restarting FFmpeg stream")
        print("FFmpegStream | Restarting FFmpeg stream")
