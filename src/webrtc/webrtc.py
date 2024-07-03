from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from multiprocessing import Queue
import asyncio
import logging

class VideoTransformTrack(VideoStreamTrack):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    async def recv(self):
        frame = await self.queue.get()
        logging.info(f"Sending frame to WebRTC: {frame}")
        return frame

async def run(pc: RTCPeerConnection, offer: RTCSessionDescription, queue: Queue, logger : logging):
    pc.addTrack(VideoTransformTrack(queue))
    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    logger.info(f"Generated local description: {answer}")
    return pc.localDescription
