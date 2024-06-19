from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List

from utils import  APIstruct, db_list_check, validate_config
from utils.request import get_logger, get_db_manager, get_ini_dict

post_router = APIRouter()

@post_router.post("/list/", status_code=status.HTTP_200_OK)
async def POST_Router(devices: List[APIstruct],logger=Depends(get_logger), db_manager=Depends(get_db_manager), ini_dict=Depends(get_ini_dict)):
    start_time = datetime.now()
    
    duplicate_check_result = await db_list_check(db_manager, devices)  
    if duplicate_check_result:
        logger.error(f"POST Router | ERROR | db_list_check Result: {duplicate_check_result}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=duplicate_check_result)

    validation_result = await validate_config(devices)
    if validation_result:
        logger.error(f"POST Router | ERROR | Validation Result: {validation_result}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_result)

    for device in devices:
        db_manager.add_device(device)
        logger.info(f"POST Router | Device added: {device.id}")

    elapsed_time = (datetime.now() - start_time).total_seconds()

    if elapsed_time > 2.0:
        logger.error("POST Router | ERROR | TIMEOUT Result")
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout")
    
    logger.info("POST Router | JSON Data send successfully")
    return {"message": "POST Router | JSON Data processed successfully"}