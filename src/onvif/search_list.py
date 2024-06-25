from datetime import datetime
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from utils import ONVIFstruct, onvif_list_type_check, port_open_check
from onvif import get_onvif_rtsp_address_list

async def search_onvif_list(devices: List[ONVIFstruct], logger) -> JSONResponse:
    start_time = datetime.now()
    results = []

    for device in devices:
        type_check = onvif_list_type_check([device])
        if not type_check:
            logger.error(f"POST Router | ERROR | Type Error Detected: {device.ip_address}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="type error.")
        
        logger.info("POST Router | starting type check success")

        if not port_open_check(device.ip_address, 80):
            logger.error(f"POST Router | ERROR | No connection could be made to the IP address: {device.ip_address}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IP address is not reachable.")

        logger.info("POST Router | starting port open check success")
        
        logger.info(f"POST Router | start onvif to read rtsp address : {device}")

        try:
            device_results = get_onvif_rtsp_address_list(device.ip_address, 80, device.id, device.pw)
            logger.info("POST Router | start onvif check success")
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