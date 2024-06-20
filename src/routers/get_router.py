from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import List
from utils import DBStruct
from utils.request import get_logger, get_db_manager

get_router = APIRouter()

@get_router.get("/list/", response_model=List[DBStruct])
async def get_items(logger=Depends(get_logger), db_manager=Depends(get_db_manager)):
    start_time = datetime.now() 
    json_list = []

    for item in db_manager.get_db():
        json_list_data = {}
        for field in DBStruct.__fields__.keys():
            json_list_data[field] = getattr(item, field)
        
        transformed_item = DBStruct(**json_list_data)
    
        json_list.append(transformed_item)

    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    if elapsed_time > 2.0:
        logger.error("GET Router | ERROR | Time Out Error")
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout")
    logger.info("GET Router | JSON Data send successfully ")
    return json_list

@get_router.get("/list/{id}", response_model=DBStruct)
async def get_item_by_idx(id: int, logger=Depends(get_logger), db_manager=Depends(get_db_manager)):
    start_time = datetime.now() 
    for item in db_manager.get_db():
        if item.id == id:
            logger.info("GET Router | JSON Data send successfully ")
            return item
    elapsed_time = (datetime.now() - start_time).total_seconds()
    
    if elapsed_time > 2.0:
        logger.error("GET Router | Time Out Error")
        raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout")
    
    logger.error(f"GET Router | Item with id {id} not found ")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Item with id {id} not found")