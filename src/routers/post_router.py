from fastapi import APIRouter, UploadFile, File, status, Depends, Request, WebSocket, WebSocketDisconnect
from starlette.requests import HTTPConnection
from typing import List
import json
from fastapi.responses import JSONResponse
import sys
sys.path.append("../")
from utils import ONVIFstruct, ChannelAddstruct, RTSPChannelStruct, VideoPlayerStruct
from utils.request import get_logger, get_channel_db, get_ini_dict, get_player_db
from onvif import search_onvif_list
from tools import save_screenshot
from videoplayer import play_video, sort_player_layout
from channel import channel_add, rtsp_channel_search
from sqlalchemy.orm.exc import NoResultFound 

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
async def update_player_layout_endpoint(request: Request, logger=Depends(get_logger), player_db=Depends(get_player_db), ini_dict=Depends(get_ini_dict)):
    return await sort_player_layout(request, logger, player_db, ini_dict)

@post_router.post("/rtsp_channel_add/", status_code=status.HTTP_201_CREATED)
async def rtsp_channel_add(device: RTSPChannelStruct, logger=Depends(get_logger)):
    return await rtsp_channel_search(device, logger)

@post_router.websocket("/ws/{player_idx}")
async def websocket_proxy(websocket: WebSocket, player_idx: int, player_db=Depends(get_player_db), logger=Depends(get_logger)):
    try:
        await play_video(websocket, player_idx, player_db, logger)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for player {player_idx}")
    except Exception as e:
        logger.error(f"Error in websocket_proxy: {e}")

@post_router.post("/video_player/{player_idx}", status_code=status.HTTP_200_OK)
async def update_video_player(player_idx: int, device: ChannelAddstruct, player_db=Depends(get_player_db), logger=Depends(get_logger)):
    try:
        existing_entry = player_db.get_player_by_number(player_idx)
        if existing_entry:
            existing_entry.onvif_result_address = device.onvif_result_address
            existing_entry.height = device.height
            existing_entry.width = device.width
            existing_entry.codec = device.codec
            existing_entry.fps = device.fps
            player_db.update_entry(existing_entry)
            logger.info(f"Updated existing entry for player {player_idx}")
        else:
            new_entry = VideoPlayerStruct(
                channel_id=player_idx,
                onvif_result_address=device.onvif_result_address,
                height=device.height,
                width=device.width,
                codec=device.codec,
                fps=device.fps,
            )
            player_db.add_device(new_entry)
            logger.info(f"Added new entry for player {player_idx}")
    except NoResultFound:
        new_entry = VideoPlayerStruct(
            channel_id=player_idx,
            onvif_result_address=device.onvif_result_address,
            height=device.height,
            width=device.width,
            codec=device.codec,
            fps=device.fps,
        )
        player_db.add_device(new_entry)
        logger.info(f"Added new entry for player {player_idx}")

    return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Player updated or added successfully"})
