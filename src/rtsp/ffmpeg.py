import asyncio
import logging
import shlex
import cv2
import numpy as np
from fastapi import WebSocket

async def FFmpegRead(url: str, height: int, width: int, gpu: int, websocket: WebSocket, stop_event: asyncio.Event, logger: logging.Logger):
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

        process = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        try:
            buffer = bytearray()
            while not stop_event.is_set():
                chunk = await process.stdout.read(data_size - len(buffer))
                if not chunk:
                    logger.error("FFmpegRead Error | No more data from FFmpeg")
                    break
                buffer.extend(chunk)
                if len(buffer) >= data_size:
                    raw_image = bytes(buffer[:data_size])
                    buffer = buffer[data_size:]
                    
                    frame = np.frombuffer(raw_image, dtype=np.uint8).reshape((height, width, 3))

                    result, encimg = cv2.imencode('.jpg', frame)
                    if not result:
                        logger.error("OpenCV encoding error")
                        break

                    await websocket.send_bytes(encimg.tobytes())
                    logger.debug(f"FFmpegRead | Sent {len(encimg.tobytes())} bytes of data.")
        except Exception as e:
            logger.error(f"Error in FFmpegRead: {e}")
        finally:
            process.stdout.close()
            await process.terminate()
            logger.info("FFmpegRead | FFmpeg read process has completed.")
        await asyncio.sleep(5)
        logger.info("FFmpegRead | Restarting FFmpeg read process")
