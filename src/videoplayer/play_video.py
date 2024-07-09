import asyncio
import logging
from typing import Dict
import signal
import sys
import json
from fastapi import WebSocket
from aiortc import RTCSessionDescription
from sqlalchemy.orm.exc import NoResultFound
sys.path.append("../")
from videoplayer import  VideoStreamer
from utils import VideoPlayerStruct
from webrtc import WebRTC

async def play_video(websocket: WebSocket, player_idx: int, player_db, logger: logging.Logger):
    logger.info(f"WebSocket connection attempt for player {player_idx}")
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            logger.info(f"POST Router | video play WebSocket | {message}")

            if message['type'] == 'assign_device':
                device = message['device']
                logger.info(f"POST Router | video play WebSocket | Assigning device {device['idx']} to player {player_idx}")

                try:
                    existing_entry = player_db.get_player_by_number(player_idx)
                    if existing_entry:
                        existing_entry.onvif_result_address = device['onvif_result_address']
                        existing_entry.height = device['height']
                        existing_entry.width = device['width']
                        existing_entry.codec = device['codec']
                        existing_entry.fps = device['fps']
                        player_db.update_entry(existing_entry)
                        logger.info(f"POST Router | video play WebSocket | Updated existing entry for channel_id {player_idx}")
                    else:
                        raise NoResultFound

                except NoResultFound:
                    db_struct = VideoPlayerStruct(
                        channel_id=player_idx,
                        onvif_result_address=device['onvif_result_address'],
                        height=device['height'],
                        width=device['width'],
                        codec=device['codec'],
                        fps=device['fps'],
                    )
                    player_db.add_device(db_struct)
                    logger.info(f"POST Router | video play WebSocket | Added new entry for channel_id {player_idx}")

                channel_info = {
                    'player_idx' : player_idx,
                    'onvif_result_address': device['onvif_result_address'],
                    'height': device['height'],
                    'width': device['width'],
                    'fps': device['fps'],
                    'codec': device['codec']
                }

                await VideoStreamer.video_start(websocket, channel_info, logger)

            elif message['type'] == 'offer':
                offer = RTCSessionDescription(sdp=message['sdp'], type=message['type'])
                answer = await WebRTC.on_offer(offer, logger)
                if answer:
                    await websocket.send_text(json.dumps({
                        'sdp': answer.sdp,
                        'type': answer.type
                    }))
                    logger.info(f"POST Router | video play WebSocket | Sent WebSocket answer: {answer}")
                else:
                    logger.info(f"POST Router | video play WebSocket | No valid answer generated for the offer")

    except Exception as e:
        logger.error(f"POST Router | video play WebSocket | Error | {e}")