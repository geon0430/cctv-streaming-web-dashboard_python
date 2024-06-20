from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from utils import  DBStruct
from utils.request import  get_logger, get_db_manager

put_router = APIRouter()

@put_router.put("/list/{id}", response_model=DBStruct)
async def PUT_Router(id: int, device: DBStruct, logger=Depends(get_logger),db_manager=Depends(get_db_manager)):
    start_time = datetime.now()
    existing_device = next((d for d in db_manager.get_db() if d.id == id), None)
    if not existing_device:
        logger.error(f"PUT Router | ERROR | No existing device with id: {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No existing device with id: {id}")

    success = db_manager.update_device(id, device)
    if not success:
        logger.error(f"PUT Router | ERROR | Failed to update device with id: {id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Failed to update device with id: {id}")

    logger.info(f"PUT Router | Device with id {id} updated successfully")

    elapsed_time = (datetime.now() - start_time).total_seconds()
    if elapsed_time > 2.0:
        logger.error("PUT Router | ERROR | TIMEOUT Result")
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout")
    
    logger.info("PUT Router | JSON Data update successfully")
    return device