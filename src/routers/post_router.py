from fastapi import APIRouter, UploadFile, File, status, Depends, Request, WebSocket
from starlette.requests import HTTPConnection
from typing import List
import json
from fastapi.responses import JSONResponse
import sys
sys.path.append("../")
from utils import ONVIFstruct, ChannelAddstruct, RTSPChannelStruct
from utils.request import get_logger, get_channel_db, get_ini_dict, get_player_db
from onvif import search_onvif_list
from tools import save_screenshot
from videoplayer import play_video, sort_player_layout
from channel import channel_add, rtsp_channel_search

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
async def websocket_proxy(websocket: WebSocket, player_idx: int):
    conn = HTTPConnection(websocket.scope)
    player_db = get_player_db(conn)
    logger = get_logger(conn)

    await play_video(websocket, player_idx, player_db, logger)
