from multiprocessing import Process, Queue, Event
import logging
from typing import Dict
import time
import sys
sys.path.append("../")
from rtsp import FFmpegRead, FFmpegStream
from utils import ConfigManager, setup_logger

def stream_rtsp(ini_dict : Dict, logger : logging):
    
    url = ini_dict['CONFIG']['RTSP']
    height = ini_dict['CONFIG']['HEIGHT']
    width = ini_dict['CONFIG']['WIDTH']
    gpu = ini_dict['CONFIG']['GPU']
    stream_address = ini_dict['CONFIG']['STREAM_ADDRESS']
    name = ini_dict['CONFIG']['NAME']
    codec = ini_dict['CONFIG']['ENCODER']
    
    read_queue = Queue()
    stop_event = Event()
     
    process_read = Process(
        target=FFmpegRead,
        args=(
            url,
            height,
            width,
            gpu,
            read_queue,
            stop_event,
            logger,
            )
    )
    
    process_stream = Process(
        target=FFmpegStream,
        args=(
            height,
            width,
            gpu,
            stream_address,
            name,
            codec,
            read_queue,
            stop_event,
            logger,
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
    ini_path = "/webrtc_python/src/config.ini"
    Config = ConfigManager(ini_path)
    ini_dict = Config.get_config_dict()
    logger = setup_logger(ini_dict)
        
    stream_rtsp(ini_dict, logger)



def stream_rtsp(url: str, height: int, width: int, gpu: int, stream_address: str, name: str, codec: str, logger: logging):
    read_queue = Queue()
    stop_event = Event()

    process_read = Process(
        target=FFmpegRead,
        args=(url, height, width, gpu, read_queue, stop_event, logger)
    )
    
    process_stream = Process(
        target=FFmpegStream,
        args=(height, width, gpu, stream_address, name, codec, read_queue, stop_event, logger)
    )

    process_read.start()
    process_stream.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Interrupted by user, stopping...")
    finally:
        stop_event.set()
        process_read.terminate()
        process_stream.terminate()
        process_read.join()
        process_stream.join()
        print("Processes terminated.")