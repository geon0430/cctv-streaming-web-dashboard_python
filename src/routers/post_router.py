from fastapi import APIRouter, UploadFile, File, status, Depends
from typing import List
from fastapi.responses import JSONResponse
from utils import ONVIFstruct, ChannelAddstruct
from utils.request import get_logger, get_db_manager, get_ini_dict
from onvif import search_onvif_list
from tools import save_screenshot
from channel import channel_add as channel_add_func

post_router = APIRouter()

@post_router.post("/onvif_list/", status_code=status.HTTP_201_CREATED)
async def onvif_list_endpoint(devices: List[ONVIFstruct], logger=Depends(get_logger)) -> JSONResponse:
    return await search_onvif_list(devices, logger)

@post_router.post("/channel_add/", status_code=status.HTTP_200_OK)
async def channel_add_endpoint(devices: List[ChannelAddstruct], logger=Depends(get_logger), db_manager=Depends(get_db_manager), ini_dict=Depends(get_ini_dict)):
    return await channel_add_func(devices, logger, db_manager, ini_dict)

@post_router.post("/save_screenshot/", status_code=status.HTTP_201_CREATED)
async def save_screenshot_endpoint(image: UploadFile = File(...), logger=Depends(get_logger), ini_dict=Depends(get_ini_dict)):
    return await save_screenshot(image, logger, ini_dict)
