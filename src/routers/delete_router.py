from fastapi import APIRouter, Depends
from typing import List
import sys
sys.path.append("../")
from utils.request import get_logger, get_channel_db
from utils.struct import ChannelDBStruct
from channel import channel_delete  

delete_router = APIRouter()


@delete_router.delete("/delete_channel/{id}", response_model=List[ChannelDBStruct])
async def DELETE_Router(id: int, logger=Depends(get_logger), db_manager=Depends(get_channel_db)):
    return await channel_delete(id, logger, db_manager)
