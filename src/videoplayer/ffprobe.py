import subprocess
import shlex
import json
import logging
from typing import Tuple
import sys
sys.path.append("../")
from utils import ConfigManager, setup_logger

def ffprobe(url: str, logger: logging.Logger) -> Tuple[float, str, int, int, int]:
    cmd = f"""
    ffprobe
    -v error
    -select_streams v:0
    -show_entries stream=width,height,codec_name,avg_frame_rate
    -of json
    {url}
    """
    cmd = shlex.split(cmd)
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        logger.error(f"ffprobe | ERROR | {stderr.decode('utf-8')}")
        raise RuntimeError(f"ffprobe | ERROR | {stderr.decode('utf-8')}")
    
    output = json.loads(stdout.decode('utf-8'))
    
    if 'streams' not in output or len(output['streams']) == 0:
        logger.error("ffprobe | ERROR | No video streams found")
        raise RuntimeError("ffprobe | ERROR | No video streams found")
    
    stream = output['streams'][0]
    
    width = int(stream['width'])
    height = int(stream['height'])
    codec = stream['codec_name']
    
    avg_frame_rate = stream.get('avg_frame_rate', '0/1')
    
    try:
        fps = eval(avg_frame_rate)
    except:
        logger.error("ffprobe | ERROR | Failed to evaluate frame rate")
        fps = 0.0
    
    logger.info(f"ffprobe | INFO | Extracted metadata - FPS: {fps}, Codec: {codec}, Width: {width}, Height: {height}")
    return fps, codec, width, height

if __name__ == "__main__":
    ini_path = "/webrtc_python/src/config.ini"
    Config = ConfigManager(ini_path)
    ini_dict = Config.get_config_dict()
    logger = setup_logger(ini_dict)
    rtsp_url = "rtsp://admin:qazwsx123!@192.168.10.70/1080p/media.smp"
    try:
        fps, codec, width, height = ffprobe(rtsp_url, logger)
        print(f"FPS: {fps}, Codec: {codec}, Width: {width}, Height: {height}")
    except RuntimeError as e:
        logger.error(f"Main | ERROR | {str(e)}")
        print(e)
