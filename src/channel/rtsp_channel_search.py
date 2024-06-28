from fastapi import Depends, status
from fastapi.responses import JSONResponse
from utils import RTSPChannelStruct
from utils.request import get_logger
from rtsp import ffprobe

async def rtsp_channel_search(device: RTSPChannelStruct, logger=Depends(get_logger)):
    logger.info(f"POST Router | rtsp_channel_add | Received RTSP data: {device}")   
    address_without_scheme = device.address.split("//")[1]
    ip_address = address_without_scheme.split('/')[0]
    rtsp_url = f"rtsp://{device.id}:{device.password}@{address_without_scheme}"
    logger.info("POST Router | starting type check success")
    try:    
        fps, codec, width, height = ffprobe(rtsp_url, logger)
        
        data = {
                "ip": ip_address,
                "onvif_result_address": rtsp_url,
                "fps": fps,
                "codec": codec,
                "width": width,
                "height": height,
                "group": device.group,
            }
        logger.info(f"POST Router | rtsp_channel_add | return data: {data}")
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "success","data": data})
    except Exception as e:
        logger.error(f"RTSP Channel Add | ERROR | {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)})
