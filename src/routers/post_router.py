from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from typing import List
from fastapi.responses import JSONResponse
from utils import ONVIFstruct, onvif_list_type_check, port_open_check, ChannelAddstruct, DBStruct
from utils.request import get_logger, get_db_manager, get_ini_dict
from rtsp.onvif import get_onvif_rtsp_address_list
import os

post_router = APIRouter()

@post_router.post("/onvif_list/", status_code=status.HTTP_201_CREATED)
async def onvif_list(devices: List[ONVIFstruct], logger=Depends(get_logger), db_manager=Depends(get_db_manager)) -> JSONResponse:
    start_time = datetime.now()
    results = []

    for device in devices:
        type_check = onvif_list_type_check([device])
        if not type_check:
            logger.error(f"POST Router | ERROR | Type Error Detected: {device.ip_address}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="type error.")
        
        logger.info("POST Router | INFO | starting type check success")

        if not port_open_check(device.ip_address, 80):
            logger.error(f"POST Router | ERROR | No connection could be made to the IP address: {device.ip_address}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IP address is not reachable.")

        logger.info("POST Router | INFO | starting port open check success")
        
        logger.info(f"POST Router | start onvif to read rtsp address : {device}")

        try:
            device_results = get_onvif_rtsp_address_list(device.ip_address, 80, device.id, device.pw)
            logger.info("POST Router | INFO | start onvif check success")
            results.extend(device_results)
        except ValueError as ve:
            if "Authentication failed" in str(ve):
                logger.error(f"POST Router | ERROR | Authentication failed: {device.ip_address}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ID or password provided.")
            else:
                logger.error(f"POST Router | ERROR | {str(ve)}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ve))
        except Exception as e:
            logger.error(f"POST Router | ERROR | Exception occurred: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        finally:
            elapsed_time = (datetime.now() - start_time).total_seconds()

            if elapsed_time > 2.0:
                logger.error("POST Router | ERROR | TIMEOUT | ONVIF data retrieval took too long.")
                raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout due to long processing time")
            
    logger.info("POST Router | ONVIF Data send successfully")
    return JSONResponse(status_code=200, content={"detail": "success", "data": results})

@post_router.post("/channel_add/", status_code=status.HTTP_200_OK)
async def channel_add(devices: List[ChannelAddstruct], logger=Depends(get_logger), db_manager=Depends(get_db_manager), ini_dict=Depends(get_ini_dict)):
    logger.info(f"POST Router | Received RTSP data: {devices}")
    current_time = datetime.now().isoformat()
    results = []
    max_channel = int(ini_dict['CONFIG']['MAX_CHANNEL'])

    current_devices = db_manager.get_all_devices()
    current_channel_count = len(current_devices)
    input_channel_count = len(devices)
    if current_channel_count + input_channel_count > max_channel:
        logger.error(f"POST Router | Channel limit exceeded: Attempt to add {input_channel_count} channels to existing {current_channel_count} channels with limit of {max_channel}")
        raise HTTPException(status_code=409, detail="Channel limit exceeded. Cannot add more channels.")
    logger.info(f"POST Router | start")
    for device in devices:
        try:
            db_struct = DBStruct(
                idx=None,
                id=device.id,
                pw=device.pw,
                name=device.name,
                onvif_result_address=device.onvif_result_address,
                height=device.height,
                width=device.width,
                codec=device.codec,
                fps=device.fps,
                create_time=current_time
            )
            logger.info(f"POST Router | Received RTSP data: {db_struct}")
            
            encrypted_password = db_manager.cipher.encrypt(device.pw)
            db_struct.pw = encrypted_password
            
            logger.info(f"POST Router | device password encrypted : {db_struct.pw}")

            channel_info = {
                'name': db_struct.name,
                'codec': db_struct.codec,
                'rtsp': db_struct.onvif_result_address,
                'height': db_struct.height,
                'width': db_struct.width,
                'fps': db_struct.fps
            }

            results.append(channel_info)

        except Exception as e:
            logger.error(f"POST Router | ERROR | Exception occurred during RTSP submission: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    logger.info("POST Router | work finish")
    return {"results": results}


@post_router.post("/save_screenshot/", status_code=status.HTTP_201_CREATED)
async def save_screenshot(image: UploadFile = File(...)):
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type")

    save_path = os.path.join('./save/', image.filename)  
    try:
        with open(save_path, "wb") as buffer:
            buffer.write(await image.read())
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save image: {str(e)}")
    
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "success"})