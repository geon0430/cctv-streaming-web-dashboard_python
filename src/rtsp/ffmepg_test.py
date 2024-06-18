from ffmpeg import FFmpegRead, FFmpegStream
import subprocess
import shlex
import multiprocessing
from multiprocessing import Process, Queue 
import signal
import time
import sys
sys.path.append("../")
from utils import setup_logger

def stream_rtsp(profile_info, pipeline_logger):
    pipeline_logger.info("stream_rtsp test start")

    FFmpegRead_send_queue = Queue()
    process_read = multiprocessing.Process(target=FFmpegRead, args=(pipeline_info, pipeline_logger, FFmpegRead_send_queue))
    process_stream = multiprocessing.Process(target=FFmpegStream, args=(pipeline_info, pipeline_logger, FFmpegRead_send_queue))

    process_read.start()
    process_stream.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user, stopping...")
    finally:
        process_read.terminate()
        process_stream.terminate()
        process_read.join()
        process_stream.join()
        print("Process terminated.")

if __name__ == "__main__":
    ini_path = "/python_object_detection_server/src/config.ini"
    
    config = ConfigManager(ini_path)
    ini_dict = config.get_config_dict()

    pipeline_info = InfoConverter(ini_dict)
    
    pipeline_logger = setup_logger(pipeline_info)
    pipeline_logger.info("pipeline logger start")
    
    stream_rtsp(pipeline_info, pipeline_logger)
