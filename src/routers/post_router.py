from fastapi import APIRouter, UploadFile, File, status, Depends, Request, HTTPException
from typing import List
from fastapi.responses import JSONResponse
from utils import ONVIFstruct, ChannelAddstruct, onvif_list_type_check, RTSPChannelStruct
from utils.request import get_logger, get_channel_db, get_ini_dict, get_player_db
from onvif import search_onvif_list
from tools import save_screenshot
from channel import channel_add, sort_player_layout
from rtsp import ffprobe

post_router = APIRouter()

@post_router.post("/onvif_list/", status_code=status.HTTP_201_CREATED)
async def onvif_list_endpoint(devices: List[ONVIFstruct], logger=Depends(get_logger)) -> JSONResponse:
    return await search_onvif_list(devices, logger)

@post_router.post("/channel_add/", status_code=status.HTTP_200_OK)
async def channel_add_endpoint(devices: List[ChannelAddstruct], logger=Depends(get_logger), channel_db=Depends(get_channel_db), ini_dict=Depends(get_ini_dict)):
    return await channel_add(devices, logger, channel_db, ini_dict)

@post_router.post("/save_screenshot/", status_code=status.HTTP_201_CREATED)
async def save_screenshot_endpoint(image: UploadFile = File(...), logger=Depends(get_logger), ini_dict=Depends(get_ini_dict)):
    return await save_screenshot(image, logger, ini_dict)

@post_router.post("/sort_player_layout/", status_code=status.HTTP_200_OK)
async def update_player_layout_endpoint(request: Request, custom_logger=Depends(get_logger), player_db=Depends(get_player_db), ini_dict=Depends(get_ini_dict)):
    return await sort_player_layout(request, custom_logger, player_db, ini_dict)


@post_router.post("/rtsp_channel_add/", status_code=status.HTTP_201_CREATED)
async def rtsp_channel_add_endpoint(device: RTSPChannelStruct, logger=Depends(get_logger)):
    logger.info(f"POST Router | rtsp_channel_add_endpoint | Received RTSP data: {device}")   
    address_without_scheme = device.address.split("//")[1]
    rtsp_url = f"rtsp://{device.id}:{device.password}@{address_without_scheme}"
    logger.info("POST Router | starting type check success")
    try:    
        fps, codec, width, height = ffprobe(rtsp_url, logger)
        
        data = {
                "rtsp": rtsp_url,
                "fps": fps,
                "codec": codec,
                "width": width,
                "height": height,
                "group" : device.group,
            }
        logger.info(f"POST Router | rtsp_channel_add | return data: {data}")
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "success","data": data})
    except Exception as e:
        logger.error(f"RTSP Channel Add | ERROR | {str(e)}")
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(e)})