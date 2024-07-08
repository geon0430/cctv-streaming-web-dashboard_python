from datetime import datetime
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from utils import ONVIFstruct, onvif_list_type_check, port_open_check
from onvif import get_onvif_rtsp_address_list
from rtsp import ffprobe

async def search_onvif_list(devices: List[ONVIFstruct], logger) -> JSONResponse:
    start_time = datetime.now()
    results = []

    for device in devices:
        type_check = onvif_list_type_check([device])
        if not type_check:
            logger.error(f"POST Router | ERROR | search_onvif_list | Type Error Detected: {device.ip_address}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="type error.")
        
        logger.info("POST Router | starting type check success")

        if not port_open_check(device.ip_address, 80):
            logger.error(f"POST Router | ERROR | search_onvif_list | No connection could be made to the IP address: {device.ip_address}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="IP address is not reachable.")

        logger.info("POST Router | search_onvif_list | starting port open check success")
        
        logger.info(f"POST Router | search_onvif_list | start onvif to read rtsp address : {device}")

        try:
            device_results = get_onvif_rtsp_address_list(device.ip_address, 80, device.id, device.pw)
            logger.info("POST Router | search_onvif_list | start onvif check success")
            results.extend(device_results)
        except ValueError as ve:
            if "Authentication failed" in str(ve):
                logger.error(f"POST Router | ERROR | search_onvif_list | Authentication failed: {device.ip_address}")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ID or password provided.")
            else:
                logger.error(f"POST Router | ERROR | search_onvif_list | {str(ve)}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(ve))
        except Exception as e:
            logger.error(f"POST Router | ERROR | search_onvif_list | Exception occurred: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        finally:
            elapsed_time = (datetime.now() - start_time).total_seconds()

            if elapsed_time > 10.0:
                logger.error("POST Router | ERROR | search_onvif_list | ONVIF data retrieval took too long.")
                raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Request timeout due to long processing time")
            
    logger.info("POST Router | search_onvif_list | ONVIF Data send successfully")
    return JSONResponse(status_code=200, content={"detail": "success", "data": results})

async def get_video_info(player_idx: int, player_db, logger):
    player = player_db.get_device_by_idx(player_idx)
    if not player or not player.onvif_result_address:
        return {"error": True, "message": "No video data available"}
    
    try:
        fps, codec, width, height, bit_rate = ffprobe(player.onvif_result_address, logger)
        return {
            "idx": player.idx,
            "fps": fps,
            "codec": codec,
            "width": width,
            "height": height,
            "bit_rate": bit_rate,
            "status": "good"
        }
    except RuntimeError as e:
        return {"error": True, "message": str(e)}
