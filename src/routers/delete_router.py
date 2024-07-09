from fastapi import APIRouter, Depends
from typing import List
import sys
sys.path.append("../")
from utils.request import get_logger, get_channel_db, get_player_db
from utils.struct import ChannelDBStruct
from channel import channel_delete  
from videoplayer import VideoStreamer

delete_router = APIRouter()

@delete_router.delete("/delete_channel/{id}", response_model=List[ChannelDBStruct])
async def DELETE_Router(id: int, logger=Depends(get_logger), db_manager=Depends(get_channel_db)):
    return await channel_delete(id, logger, db_manager)

@delete_router.delete("/delete_player/{id}", response_model=dict)
async def DELETE_Player_Router(id: int, logger=Depends(get_logger), player_db=Depends(get_player_db)):
    
    await VideoStreamer.stop_stream(id, logger)
    
    default_player_data = {
        "onvif_result_address": None,
        "height": 0,
        "width": 0,
        "fps": 0.0,
        "codec": ""
    }

    player_db.update_device_by_channel_id(id, default_player_data)
    
    return {"detail": f"Player {id} has been reset"}