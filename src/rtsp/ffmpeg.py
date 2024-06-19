import time
from multiprocessing import Queue, Process
import subprocess
import shlex
import logging

def FFmpegRead(url: str, height: int, width: int, gpu: int, queue: Queue, logger: logging):
    while True:
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
            while True:
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
            queue.put(None)
            process.stdout.close()
            process.terminate()
            stderr_output = process.stderr.read().decode()
            logger.info(f"FFmpegRead stderr: {stderr_output}")
            logger.info("FFmpegRead | FFmpeg read process has completed.")
        
        logger.info("FFmpegRead | Restarting FFmpeg read process in 5 seconds...")
        time.sleep(5)  # 재시작하기 전에 5초 대기

def FFmpegStream(height: int, width: int, gpu: int, stream_address: str, name: str, codec: str, queue: Queue, logger: logging):
    while True:
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
            while True:
                if not queue.empty():
                    data = queue.get()
                    process.stdin.write(data)
                    process.stdin.flush()
                    logger.debug(f"FFmpegStream | Streaming {len(data)} bytes of data.")
                    time.sleep(0.03)
                    
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
            stderr_output = process.stderr.read().decode()
            logger.info(f"FFmpegStream stderr: {stderr_output}")
            logger.info("FFmpegStream | FFmpeg stream process has completed.")
        
        logger.info("FFmpegStream | Restarting FFmpeg stream process in 5 seconds...")
        time.sleep(5)  
