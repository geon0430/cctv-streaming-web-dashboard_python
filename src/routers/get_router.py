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
            "idx": player_idx.idx,
            "fps": fps,
            "codec": codec,
            "width": width,
            "height": height,
            "bit_rate": bit_rate,
            "status": "good"
        }
    except RuntimeError as e:
        return {"error": True, "message": str(e)}


@get_router.get("/get_channel_db/", status_code=status.HTTP_200_OK)
async def get_channel_db_endpoint(channel_db=Depends(get_channel_db), logger=Depends(get_logger)):
    try:
        channels = channel_db.get_all_devices()
        logger.info(f"Get_Router | Channels fetched:  {channels}")
        sorted_channels = sorted(channels, key=lambda c: c.onvif_result_address)  
        return [
            {
                "idx" : c.idx,
                "ip": c.ip,
                "height": c.height,
                "width": c.width,
                "fps": c.fps,
                "codec": c.codec,
                "group": c.group,
                "onvif_result_address": c.onvif_result_address
            }
            for c in sorted_channels
        ]
    except Exception as e:
        logger.error(f"Get_Router | ERROR | Exception occurred during channel fetch: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch channels")