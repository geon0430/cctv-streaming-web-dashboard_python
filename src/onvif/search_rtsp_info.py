from fastapi import APIRouter, Depends, HTTPException, status
from utils import get_logger, get_player_db
from videoplayer import ffprobe

get_router = APIRouter()

async def get_video_info(player_idx: int, player_db=Depends(get_player_db), logger=Depends(get_logger)):
    player = player_db.get_device_by_idx(player_idx)
    if not player or not player.onvif_result_address:
        return {"idx": player_idx, "error": True, "message": "No video data available"}
    
    try:
        fps, codec, width, height = ffprobe(player.onvif_result_address, logger)
        return {
            "idx": player.channel_id,
            "fps": fps,
            "codec": codec,
            "width": width,
            "height": height,
            "status": "good"
        }
    except RuntimeError as e:
        return {"idx": player.idx, "error": True, "message": str(e)}
