from fastapi import APIRouter, Depends, HTTPException, status, Request
from utils import get_logger, get_channel_db, get_player_db
from channel import channel_get_db, get_group
from onvif import get_video_info

get_router = APIRouter()

@get_router.get("/video_info/{player_idx}", status_code=status.HTTP_200_OK)
async def get_video_info_endpoint(player_idx: int, player_db=Depends(get_player_db), logger=Depends(get_logger)):
    return await get_video_info(player_idx, player_db, logger)


@get_router.get("/get_groups/", status_code=status.HTTP_200_OK)
async def get_groups_endpoint(channel_db = Depends(get_channel_db), logger = Depends(get_logger)):
    return await get_group(channel_db, logger)


@get_router.get("/get_channel_db/", status_code=status.HTTP_200_OK)
async def get_channel_db_endpoint(channel_db=Depends(get_channel_db), logger=Depends(get_logger)):
    return await channel_get_db(channel_db, logger)
