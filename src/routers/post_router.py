from fastapi import APIRouter, UploadFile, File, status, Depends, Request, HTTPException
from typing import List
from fastapi.responses import JSONResponse
from utils import ONVIFstruct, ChannelAddstruct, RTSPChannelStruct, ChannelDBStruct
from utils.request import get_logger, get_channel_db, get_ini_dict, get_player_db
from onvif import search_onvif_list
from tools import save_screenshot
from channel import channel_add, sort_player_layout, rtsp_channel_search
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
async def rtsp_channel_add(device: RTSPChannelStruct, logger=Depends(get_logger)):
    return await rtsp_channel_search(device, logger)

@post_router.post("/video_player/{player_idx}", status_code=status.HTTP_200_OK)
async def assign_device_to_player(player_idx: int, device: ChannelDBStruct, logger=Depends(get_logger), player_db=Depends(get_player_db)):
    logger.info(f"POST Router | video_player start | Received RTSP data: {device}")
    try:
        channel_info = {
            'channel_id':player_idx,
            'onvif_result_address': device.onvif_result_address,
            'height': device.height,
            'width': device.width,
            'fps': device.fps,
            'codec': device.codec
        }
        
        player_db.update_player(player_idx, channel_info)
        logger.info(f"Device {device.idx} assigned to player {player_idx}")
        
        return {"message": "Device assigned successfully"}
    except Exception as e:
        logger.error(f"Error assigning device to player: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to assign device to player")