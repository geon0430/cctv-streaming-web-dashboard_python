import asyncio
import numpy as np
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaRecorder
from av import VideoFrame

class VideoTransformTrack(VideoStreamTrack):
    def __init__(self, queue, height, width):
        super().__init__()
        self.queue = queue
        self.height = height
        self.width = width

    async def recv(self):
        frame = await self.next_timestamp()
        try:
            data = self.queue.get_nowait()
            img = np.frombuffer(data, np.uint8).reshape((self.height, self.width, 3))
            video_frame = VideoFrame.from_ndarray(img, format='bgr24')
            video_frame.pts = frame.pts
            video_frame.time_base = frame.time_base
            return video_frame
        except asyncio.QueueEmpty:
            return None

# router = APIRouter()

# @router.post("/offer")
# async def offer(request: Offer):
#     global read_queue, height, width
    
#     params = request.dict()
#     pc = RTCPeerConnection()
    
#     @pc.on("iceconnectionstatechange")
#     async def on_iceconnectionstatechange():
#         if pc.iceConnectionState == "failed":
#             await pc.close()

#     video_track = VideoTransformTrack(read_queue, height, width)
#     pc.addTrack(video_track)
    
#     offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
#     await pc.setRemoteDescription(offer)
#     answer = await pc.createAnswer()
#     await pc.setLocalDescription(answer)
    
 