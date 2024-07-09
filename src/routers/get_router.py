from fastapi import APIRouter, Depends, HTTPException, status, Request
from utils import get_logger, get_channel_db, get_player_db, get_ini_dict
from channel import channel_get_db, get_group
from onvif import get_video_info

get_router = APIRouter()

from fastapi import APIRouter, Depends, HTTPException, status, Request
from utils import get_logger, get_channel_db, get_player_db
from channel import channel_get_db, get_group
from onvif import get_video_info

get_router = APIRouter()

@get_router.get("/video_info/", status_code=status.HTTP_200_OK)
async def get_all_video_infos(player_db=Depends(get_player_db), logger=Depends(get_logger),ini=Depends(get_ini_dict)):
    results = []
    max_player = ini['CONFIG']['MAX_CHANNEL']
    for idx in range(1, max_player +1): 
        result = await get_video_info(idx, player_db, logger)
        results.append(result)
    return results


@get_router.get("/get_groups/", status_code=status.HTTP_200_OK)
async def get_groups_endpoint(channel_db = Depends(get_channel_db), logger = Depends(get_logger)):
    return await get_group(channel_db, logger)

@get_router.get("/get_channel_db/", status_code=status.HTTP_200_OK)
async def get_channel_db_endpoint(channel_db=Depends(get_channel_db), logger=Depends(get_logger)):
    return await channel_get_db(channel_db, logger)
