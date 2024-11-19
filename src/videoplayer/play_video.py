import logging
import json
from fastapi import WebSocket, WebSocketDisconnect
from aiortc import RTCSessionDescription
from sqlalchemy.orm.exc import NoResultFound
from starlette.websockets import WebSocketState
from videoplayer import VideoStreamer
from videoplayer.webrtc import WebRTC
from utils import VideoPlayerStruct


async def play_video(websocket: WebSocket, player_idx: int, player_db, logger: logging.Logger):
    logger.info(f"WebSocket connection attempt for player {player_idx}")

    try:
        existing_entry = player_db.get_player_by_number(player_idx)
        if not existing_entry or not all([
            existing_entry.onvif_result_address,
            existing_entry.height,
            existing_entry.width,
            existing_entry.fps,
            existing_entry.codec,
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

                    if message["type"] in ["assign_device", "reassign_device"]:
                        device = message["device"]
                        logger.info(f"Assigning device {device['idx']} to player {player_idx}")
                        if not existing_entry:
                            existing_entry = VideoPlayerStruct(
                                channel_id=player_idx,
                                onvif_result_address=device["onvif_result_address"],
                                height=device["height"],
                                width=device["width"],
                                codec=device["codec"],
                                fps=device["fps"],
                            )
                            player_db.add_device(existing_entry)
                        else:
                            existing_entry.onvif_result_address = device["onvif_result_address"]
                            existing_entry.height = device["height"]
                            existing_entry.width = device["width"]
                            existing_entry.codec = device["codec"]
                            existing_entry.fps = device["fps"]
                            player_db.update_entry(existing_entry)

                        logger.info(f"Updated entry for channel_id {player_idx}")

                        # Start the video streamer
                        channel_info = {
                            "player_idx": player_idx,
                            "onvif_result_address": device["onvif_result_address"],
                            "height": device["height"],
                            "width": device["width"],
                            "fps": device["fps"],
                            "codec": device["codec"],
                        }

                        await VideoStreamer.video_start(websocket, channel_info, logger)

                    elif message["type"] == "offer":
                        offer = RTCSessionDescription(sdp=message["sdp"], type=message["type"])
                        answer = await WebRTC.on_offer(offer, logger)
                        if answer:
                            await websocket.send_text(json.dumps({
                                "sdp": answer.sdp,
                                "type": answer.type,
                            }))
                            logger.info(f"Sent WebSocket answer: {answer}")
                        else:
                            logger.warning("No valid answer generated for the offer.")

                except WebSocketDisconnect:
                    logger.info(f"WebSocket disconnected for player {player_idx}")
                    break

                except Exception as e:
                    logger.error(f"Unexpected error in WebSocket handling: {e}")
                    break

        finally:
            logger.info(f"Cleaning up resources for player {player_idx}")
            await VideoStreamer.stop_stream(player_idx, logger)
            if websocket.client_state != WebSocketState.DISCONNECTED:
                await websocket.close()
            logger.info(f"WebSocket connection fully closed for player {player_idx}")

    except NoResultFound:
        logger.error(f"Player {player_idx} not found in DB")
        await websocket.close(code=403, reason="Player not found in DB")

    except Exception as e:
        logger.error(f"Unexpected error during WebSocket connection: {e}")
        if websocket.client_state != WebSocketState.DISCONNECTED:
            await websocket.close()
        await VideoStreamer.stop_stream(player_idx, logger)
