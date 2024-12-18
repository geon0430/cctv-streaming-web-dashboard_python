from fastapi import HTTPException, status, Depends
from typing import List
from datetime import datetime
from utils.request import get_logger, get_channel_db
from utils.struct import ChannelDBStruct

async def channel_delete(id: int, logger=Depends(get_logger), db_manager=Depends(get_channel_db)) -> List[ChannelDBStruct]:
    start_time = datetime.now()

    success = db_manager.remove_device(id)

    if not success:
        logger.error(f"DELETE Router | Item with id {id} not found ")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id {id} not found")

    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    if elapsed_time > 2.0:
        logger.error("DELETE Router | ERROR | Time Out Error")
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout")

    logger.info(f"DELETE Router | Item with id {id} deleted successfully")
    return db_manager.get_all_devices()
