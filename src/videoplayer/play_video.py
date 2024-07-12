import asyncio
import logging
from typing import Dict
import sys
import json
from fastapi import WebSocket, HTTPException, WebSocketDisconnect
from aiortc import RTCSessionDescription
from sqlalchemy.orm.exc import NoResultFound
from starlette.websockets import WebSocketState
from videoplayer import VideoStreamer
from utils import VideoPlayerStruct
from webrtc import WebRTC

async def play_video(websocket: WebSocket, player_idx: int, player_db, logger: logging.Logger):
    logger.info(f"WebSocket connection attempt for player {player_idx}")

    try:
        existing_entry = player_db.get_player_by_number(player_idx)
        if not existing_entry or not all([
            existing_entry.onvif_result_address, 
            existing_entry.height, 
            existing_entry.width, 
            existing_entry.fps, 
            existing_entry.codec
        ]):
            logger.error(f"Player {player_idx} not found or not properly configured in DB")
            await websocket.close(code=403, reason="Player not found or not properly configured in DB")
            return

        await websocket.accept()

        try:
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    logger.info(f"POST Router | video play WebSocket | {message}")

                    if message['type'] in ['assign_device', 'reassign_device']:
                        device = message['device']
                        logger.info(f"POST Router | video play WebSocket | Assigning device {device['idx']} to player {player_idx}")

                        # Save the device information in the database
                        if not existing_entry:
                            existing_entry = VideoPlayerStruct(
                                channel_id=player_idx,
                                onvif_result_address=device['onvif_result_address'],
                                height=device['height'],
                                width=device['width'],
                                codec=device['codec'],
                                fps=device['fps'],
                            )
                            player_db.add_device(existing_entry)
                        else:
                            existing_entry.onvif_result_address = device['onvif_result_address']
                            existing_entry.height = device['height']
                            existing_entry.width = device['width']
                            existing_entry.codec = device['codec']
                            existing_entry.fps = device['fps']
                            player_db.update_entry(existing_entry)

                        logger.info(f"POST Router | video play WebSocket | Updated existing entry for channel_id {player_idx}")

                        channel_info = {
                            'player_idx': player_idx,
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

                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected for player {player_idx}")
                    await VideoStreamer.stop_stream(player_idx, logger)
                    break

                except Exception as e:
                    logger.error(f"POST Router | video play WebSocket | Error | {e}")
                    break

        except Exception as e:
            logger.error(f"POST Router | video play WebSocket | Connection Error | {e}")
        finally:
            logger.info(f"WebSocket connection closed for player {player_idx}")
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await VideoStreamer.stop_stream(player_idx, logger)

    except NoResultFound:
        logger.error(f"Player {player_idx} not found in DB")
        await websocket.close(code=403, reason="Player not found in DB")
