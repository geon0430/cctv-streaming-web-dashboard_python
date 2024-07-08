from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from multiprocessing import Queue
import logging

class WebRTC(VideoStreamTrack):
    def __init__(self, queue: Queue):
        super().__init__()
        self.queue = queue

    async def recv(self):
        frame = await self.queue.get()
        logging.info(f"WebRTC | Sending frame to WebRTC: {frame}")
        return frame

    @staticmethod
    async def run(pc: RTCPeerConnection, offer: RTCSessionDescription, queue: Queue, logger: logging):
        logger.info("WebRTC | Entering run function")
        try:
            pc.addTrack(WebRTC(queue))
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            logger.info(f"WebRTC | Generated local description: {answer}")
            return pc.localDescription
        except Exception as e:
            logger.error(f"WebRTC | run ERROR | {e}")
            return None
        
    @staticmethod
    async def on_offer(offer : RTCSessionDescription, logger : logging):
        pc = RTCPeerConnection()
        try:
            local_description = await WebRTC.run(pc, offer, None, logger)
            if not local_description:
                logger.error("WebRTC | ERROR | run function did not return a valid local_description")
            else:
                logger.info(f"WebRTC | Generated answer: {local_description.sdp}")
            return local_description
        except Exception as e:
            logger.error(f"WebRTC | on_offer ERROR | {e}")
            return None