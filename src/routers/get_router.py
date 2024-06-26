from fastapi import APIRouter, Depends, HTTPException, status, Request
from utils import get_logger, get_channel_db, get_player_db
from rtsp import ffprobe

get_router = APIRouter()

@get_router.get("/get_groups/", status_code=status.HTTP_200_OK)
async def get_groups_endpoint(channel_db = Depends(get_channel_db), logger = Depends(get_logger)):
    try:
        groups = channel_db.get_all_groups()
        logger.info(f"Get_Router | group get :  {groups}")
        return groups
    except Exception as e:
        logger.error(f"Get_Router | ERROR | Exception occurred during group fetch: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch groups")

@get_router.get("/video_info/{player_idx}", status_code=status.HTTP_200_OK)
async def get_video_info(player_idx: int, player_db=Depends(get_player_db), logger=Depends(get_logger)):
    player = player_db.get_device_by_idx(player_idx)
    if not player or not player.onvif_result_address:
        return {"error": True, "message": "No video data available"}
    
    try:
        fps, codec, width, height, bit_rate = ffprobe(player.onvif_result_address, logger)
        return {
            "fps": fps,
            "codec": codec,
            "width": width,
            "height": height,
            "bit_rate": bit_rate,
            "status": "good"
        }
    except RuntimeError as e:
        return {"error": True, "message": str(e)}
