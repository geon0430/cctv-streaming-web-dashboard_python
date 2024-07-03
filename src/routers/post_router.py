from fastapi import APIRouter, UploadFile, File, status, Depends, Request, HTTPException, WebSocket
from typing import List, Dict
import json
from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi.responses import JSONResponse
import logging
import sys
import asyncio
from starlette.middleware.cors import CORSMiddleware

sys.path.append("../")
from utils import ONVIFstruct, ChannelAddstruct, RTSPChannelStruct, ChannelDBStruct
from utils.request import get_logger, get_channel_db, get_ini_dict, get_player_db
from onvif import search_onvif_list
from tools import save_screenshot
from channel import channel_add, sort_player_layout, rtsp_channel_search, play_video
from webrtc import run

post_router = APIRouter()

player_streams = {}

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
async def assign_device_to_player_endpoint(player_idx: int, device: ChannelDBStruct, logger=Depends(get_logger), player_db=Depends(get_player_db)):
    logger.info(f"Received POST request to assign device {device.idx} to player {player_idx}")
    read_queue = asyncio.Queue()
    stop_event = asyncio.Event()
    channel_info = {
        'onvif_result_address': device.onvif_result_address,
        'height': device.height,
        'width': device.width,
        'fps': device.fps,
        'codec': device.codec
    }
    player_streams[player_idx] = (read_queue, stop_event)
    asyncio.create_task(play_video(read_queue, stop_event, channel_info, logger))
    logger.info("Started video playback process")
    return {"message": "Device assigned successfully"}

@post_router.websocket("/ws/{player_idx}")
async def websocket_endpoint(websocket: WebSocket, player_idx: int, logger=Depends(get_logger)):
    logger.info(f"WebSocket connection attempt for player {player_idx}")
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for player {player_idx}")

    if player_idx not in player_streams:
        await websocket.close()
        logger.error(f"No stream found for player {player_idx}")
        return

    read_queue, stop_event = player_streams[player_idx]

    async def on_offer(offer):
        pc = RTCPeerConnection()
        local_description = await run(pc, offer, read_queue, logger)
        logger.info(f"Generated answer: {local_description.sdp}")
        return local_description

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"Received WebSocket message: {message}")

            if message['type'] == 'offer':
                offer = RTCSessionDescription(sdp=message['sdp'], type=message['type'])
                answer = await on_offer(offer)
                await websocket.send_text(json.dumps({
                    'sdp': answer.sdp,
                    'type': answer.type
                }))
                logger.info(f"Sent WebSocket answer: {answer}")

    except Exception as e:
        logger.error(f"Error in websocket: {e}")

    finally:
        stop_event.set()
        await websocket.close()
        logger.info("Closed WebSocket and stopped RTSP reading")
        del player_streams[player_idx]
