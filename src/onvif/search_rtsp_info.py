from fastapi import HTTPException, status, Depends
from utils import get_logger, get_player_db
from rtsp import ffprobe

async def get_video_info(player_idx: int, player_db=Depends(get_player_db), logger=Depends(get_logger)):
    player = player_db.get_device_by_idx(player_idx)
    if not player or not player.onvif_result_address:
        return {"error": True, "message": "No video data available"}
    
    try:
        fps, codec, width, height, bit_rate = ffprobe(player.onvif_result_address, logger)
        return {
            "idx": player.idx,
            "fps": fps,
            "codec": codec,
            "width": width,
            "height": height,
            "bit_rate": bit_rate,
            "status": "good"
        }
    except RuntimeError as e:
        return {"error": True, "message": str(e)}
