import asyncio
import logging
from typing import Dict
import signal
import sys
sys.path.append("../")
from rtsp import FFmpegRead

async def shutdown(signal, loop, stop_event, logger):
    logger.info(f"Received exit signal {signal.name}...")
    stop_event.set()

async def play_video(read_queue: asyncio.Queue, stop_event: asyncio.Event, channel_info: Dict, logger: logging.Logger):
    url = channel_info['onvif_result_address']
    height = channel_info['height']
    width = channel_info['width']
    gpu = 0
    
    loop = asyncio.get_running_loop()
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda s=sig: asyncio.create_task(shutdown(s, loop, stop_event, logger))
        )

    await FFmpegRead(
        url,
        height,
        width,
        gpu,
        read_queue,
        stop_event,
        logger,
    )
