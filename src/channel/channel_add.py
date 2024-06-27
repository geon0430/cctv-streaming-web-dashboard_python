from datetime import datetime
import re
from fastapi import HTTPException, status
from typing import List
from utils import ChannelAddstruct, ChannelDBStruct

async def channel_add(devices: List[ChannelAddstruct], logger, db_manager, ini_dict) -> dict:
    logger.info(f"POST Router | channel_add | Received RTSP data: {devices}")
    current_time = datetime.now().isoformat()
    results = []

    logger.info(f"POST Router | channel_add | start")
    
    for device in devices:
        try:
            match = re.search(r'(\d{1,3}\.){3}\d{1,3}', device.onvif_result_address)
            print(match.group(0))
            logger.info(match.group(0))
            db_struct = ChannelDBStruct(
                idx=None,
                onvif_result_address=device.onvif_result_address,
                height=device.height,
                width=device.width,
                codec=device.codec,
                fps=device.fps,
                create_time=current_time,
                group=device.group,
                ip=match.group(0),
            )
            logger.info(f"POST Router | channel_add | Received RTSP data: {db_struct}")

            db_manager.add_device(db_struct)
            logger.info(f"POST Router | channel_add | device added to database: {db_struct}")

            channel_info = {
                'codec': db_struct.codec,
                'rtsp': db_struct.onvif_result_address,
                'height': db_struct.height,
                'width': db_struct.width,
                'fps': db_struct.fps
            }

            results.append(channel_info)

        except Exception as e:
            logger.error(f"POST Router | ERROR | channel_add | Exception occurred during RTSP submission: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    logger.info("POST Router | channel_add | work finish")
    return {"results": results}
