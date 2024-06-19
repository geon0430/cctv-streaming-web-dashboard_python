from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from fastapi.responses import JSONResponse
from utils import  ONVIFstruct, onvif_list_check, port_open_check
from utils.request import get_logger, get_db_manager
from rtsp.onvif import get_onvif_rtsp_address_list

post_router = APIRouter()

@post_router.post("/onvif_list/", status_code=status.HTTP_201_CREATED)
async def onvif_list(devices: List[ONVIFstruct], custom_logger=Depends(get_logger), db_manager=Depends(get_db_manager)) -> JSONResponse:
    start_time = datetime.now()
    results = []
    response_detail = "no_duplicate"

    for device in devices:
        custom_logger.debug("POST Router | DEBUG | starting duplicate check")
        duplicate_check = await onvif_list_check(db_manager, [device])
        if duplicate_check != 'no_duplicate':
            response_detail = duplicate_check
            custom_logger.error(f"POST Router | ERROR | Duplicate Detected: {device.ip_address}")

        custom_logger.debug("POST Router | DEBUG | starting validation check")
        
        custom_logger.debug("POST Router | DEBUG | starting port open check")
        if not port_open_check(device.ip_address, 80):
            custom_logger.error(f"POST Router | ERROR | No connection could be made to the IP address: {device.ip_address}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IP address is not reachable.")

        custom_logger.debug(f"POST Router | start onvif to read rtsp address : {device}")

        try:
            custom_logger.debug("POST Router | DEBUG | start onvif check")
            device_results = get_onvif_rtsp_address_list(device.ip_address, 80, device.id, device.pw)
            results.extend(device_results)
        except Exception as e:
            if "security token could not be authenticated or authorized" in str(e).lower():
                custom_logger.error("POST Router | ERROR | Authentication failed: Invalid ID or password")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ID or password provided.")
            else:
                custom_logger.error(f"POST Router | ERROR | Exception occurred: {str(e)}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        finally:
            elapsed_time = (datetime.now() - start_time).total_seconds()

            if elapsed_time > 2.0:
                custom_logger.error("POST Router | ERROR | TIMEOUT | ONVIF data retrieval took too long.")
                raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout due to long processing time")

    custom_logger.info("POST Router | ONVIF Data send successfully")
    return JSONResponse(status_code=200, content={"detail": response_detail, "data": results})


# @post_router.post("/list/", status_code=status.HTTP_200_OK)
# async def POST_Router(devices: List[APIstruct],logger=Depends(get_logger), db_manager=Depends(get_db_manager), ini_dict=Depends(get_ini_dict)):
#     start_time = datetime.now()
    
#     duplicate_check_result = await db_list_check(db_manager, devices)  
#     if duplicate_check_result:
#         logger.error(f"POST Router | ERROR | db_list_check Result: {duplicate_check_result}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=duplicate_check_result)

#     validation_result = await validate_config(devices)
#     if validation_result:
#         logger.error(f"POST Router | ERROR | Validation Result: {validation_result}")
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=validation_result)

#     for device in devices:
#         db_manager.add_device(device)
#         logger.info(f"POST Router | Device added: {device.id}")

#     elapsed_time = (datetime.now() - start_time).total_seconds()

#     if elapsed_time > 2.0:
#         logger.error("POST Router | ERROR | TIMEOUT Result")
#         raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout")
    
#     logger.info("POST Router | JSON Data send successfully")
#     return {"message": "POST Router | JSON Data processed successfully"}