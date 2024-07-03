import asyncio
import logging
import shlex

async def FFmpegRead(url: str, height: int, width: int, gpu: int, queue: asyncio.Queue, stop_event: asyncio.Event, logger: logging.Logger):
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
            while not stop_event.is_set():
                raw_image = await process.stdout.read(data_size)
                if not raw_image:
                    logger.error("FFmpegRead Error | Data is not raw_image")
                    break
                await queue.put(raw_image)
                logger.debug(f"FFmpegRead | Sent {len(raw_image)} bytes of data.")
                
        except Exception as e:
            logger.error(f"Error in FFmpegRead: {e}")
            print(f"Error in FFmpegRead: {e}")
            
        finally:
            process.stdout.close()
            await process.terminate()
            logger.info("FFmpegRead | FFmpeg read process has completed.")
        
        await asyncio.sleep(5)
        logger.info("FFmpegRead | Restarting FFmpeg read process")
