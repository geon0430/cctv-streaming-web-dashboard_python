from fastapi import Depends, status
from fastapi.responses import JSONResponse
from utils import RTSPChannelStruct
from utils.request import get_logger
from rtsp import ffprobe

async def rtsp_channel_search(device: RTSPChannelStruct, logger=Depends(get_logger)):
    try:
        channels = channel_db.get_all_devices()
        logger.info(f"Get_Router | Channels fetched:  {channels}")
        sorted_channels = sorted(channels, key=lambda c: c.onvif_result_address)  
        return [
            {
                "ip": c.ip,
                "height": c.height,
                "width": c.width,
                "fps": c.fps,
                "codec": c.codec,
                "group": c.group,
                "onvif_result_address": c.onvif_result_address
            }
            for c in sorted_channels
        ]
    except Exception as e:
        logger.error(f"Get_Router | ERROR | Exception occurred during channel fetch: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch channels")