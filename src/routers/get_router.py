from fastapi import APIRouter, Depends, HTTPException, status, Request
from utils import get_logger, get_channel_db, get_player_db, get_ini_dict
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

@get_router.get("/get_player/")
async def get_player(player_db=Depends(get_player_db)):
    all_players = player_db.get_all_devices()
    return all_players

@get_router.get("/get_layout/")
async def get_layout(player_db=Depends(get_player_db)):
    all_players = player_db.get_all_devices()
    active_players = [player for player in all_players if player.onvif_result_address]
    
    if not active_players:
        return {"layout": "img1"}  

    max_channel_id = max(player.channel_id for player in active_players)

    if max_channel_id == 1:
        return {"layout": "img1"}
    elif 2 <= max_channel_id <= 4:
        return {"layout": "img2"}
    elif 5 <= max_channel_id <= 9:
        return {"layout": "img3"}
    elif 10 <= max_channel_id <= 16:
        return {"layout": "img4"}
    else:
        return {"layout": "img1"} 


@get_router.get("/get_groups/", status_code=status.HTTP_200_OK)
async def get_groups_endpoint(channel_db = Depends(get_channel_db), logger = Depends(get_logger)):
    return await get_group(channel_db, logger)

@get_router.get("/get_channel_db/", status_code=status.HTTP_200_OK)
async def get_channel_db_endpoint(channel_db=Depends(get_channel_db), logger=Depends(get_logger)):
    return await channel_get_db(channel_db, logger)