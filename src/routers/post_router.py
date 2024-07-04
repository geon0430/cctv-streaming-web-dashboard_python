from fastapi import APIRouter, UploadFile, File, status, Depends, Request, WebSocket
from typing import List, Dict
import json
from aiortc import RTCPeerConnection, RTCSessionDescription
from fastapi.responses import JSONResponse
import sys
import asyncio
sys.path.append("../")
from utils import ONVIFstruct, ChannelAddstruct, RTSPChannelStruct, ChannelDBStruct, setup_logger, ConfigManager
from utils.request import get_logger, get_channel_db, get_ini_dict, get_player_db
from onvif import search_onvif_list
from tools import save_screenshot
from channel import channel_add, sort_player_layout, rtsp_channel_search, play_video
from webrtc import run

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
async def websocket_endpoint(websocket: WebSocket, player_idx: int):
    api_ini_path = "/webrtc_python/src/config.ini"
    api_config = ConfigManager(api_ini_path)
    ini_dict = api_config.get_config_dict()
    logger = setup_logger(ini_dict)
    logger.info(f"WebSocket connection attempt for player {player_idx}")
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for player {player_idx}")

    stop_event = asyncio.Event()
    send_task = None

    async def on_offer(offer):
        pc = RTCPeerConnection()
        try:
            local_description = await run(pc, offer, None, logger)
            if not local_description:
                logger.error("run function did not return a valid local_description")
            else:
                logger.info(f"Generated answer: {local_description.sdp}")
            return local_description
        except Exception as e:
            logger.error(f"Error in on_offer: {e}")
            return None

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"Received WebSocket message: {message}")

            if message['type'] == 'assign_device':
                device = message['device']
                logger.info(f"Assigning device {device['idx']} to player {player_idx}")
                channel_info = {
                    'onvif_result_address': device['onvif_result_address'],
                    'height': device['height'],
                    'width': device['width'],
                    'fps': device['fps'],
                    'codec': device['codec']
                }
                if send_task:
                    stop_event.set()
                    await send_task
                stop_event.clear()
                send_task = asyncio.create_task(play_video(websocket, stop_event, channel_info, logger))

            elif message['type'] == 'offer':
                offer = RTCSessionDescription(sdp=message['sdp'], type=message['type'])
                answer = await on_offer(offer)
                if answer:
                    await websocket.send_text(json.dumps({
                        'sdp': answer.sdp,
                        'type': answer.type
                    }))
                    logger.info(f"Sent WebSocket answer: {answer}")
                else:
                    logger.error("No valid answer generated for the offer")

    except Exception as e:
        logger.error(f"Error in websocket: {e}")

    finally:
        stop_event.set()
        if send_task:
            send_task.cancel()
        await websocket.close()
        logger.info("Closed WebSocket and stopped RTSP reading")
