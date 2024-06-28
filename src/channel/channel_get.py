from fastapi import APIRouter, Depends, HTTPException, status, Request
from utils import get_logger, get_channel_db

async def channel_get_db(channel_db=Depends(get_channel_db), logger=Depends(get_logger)):
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
    
async def get_group(channel_db = Depends(get_channel_db), logger = Depends(get_logger)):
    try:
        groups = channel_db.get_all_groups()
        logger.info(f"Get_Router | group get :  {groups}")
        return groups
    except Exception as e:
        logger.error(f"Get_Router | ERROR | Exception occurred during group fetch: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch groups")