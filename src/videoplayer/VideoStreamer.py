import asyncio
import logging
from typing import Dict, List
from fastapi import WebSocket
from videoplayer import FFmpegRead

class VideoStreamer:
    active_streams: Dict[int, "VideoStreamer"] = {}

    def __init__(self, websocket: WebSocket, channel_info: Dict, logger: logging.Logger):
        self.websocket = websocket
        self.channel_info = channel_info
        self.logger = logger
        self.stop_event = asyncio.Event()
        self.send_task = None

    @classmethod
    async def video_start(cls, websocket: WebSocket, channel_info: Dict, logger: logging.Logger):
        player_idx = channel_info['player_idx']
        if player_idx in cls.active_streams:
            await cls.active_streams[player_idx].stop_stream()

        streamer = cls(websocket, channel_info, logger)
        cls.active_streams[player_idx] = streamer
        streamer.stop_event, streamer.send_task = await streamer.start()

    @classmethod
    async def stop_stream(cls, player_idx: int, logger: logging.Logger):
        if player_idx in cls.active_streams:
            streamer = cls.active_streams[player_idx]
            streamer.stop_event.set()
            if streamer.send_task:
                streamer.send_task.cancel()
            await streamer.websocket.close()
            del cls.active_streams[player_idx]
            logger.info(f'VideoStreamer | ffmpeg stop {player_idx}')

    async def start(self):
        self.send_task = asyncio.create_task(self._ffmpeg_start())
        return self.stop_event, self.send_task

    async def _ffmpeg_start(self):
        url = self.channel_info['onvif_result_address']
        height = self.channel_info['height']
        width = self.channel_info['width']
        gpu = 0

        await FFmpegRead(
            url,
            height,
            width,
            gpu,
            self.websocket,
            self.stop_event,
            self.logger,
        )