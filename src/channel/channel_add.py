from datetime import datetime
from fastapi import HTTPException, status
from typing import List
from utils import ChannelAddstruct, DBStruct

async def channel_add(devices: List[ChannelAddstruct], logger, db_manager, ini_dict) -> dict:
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
