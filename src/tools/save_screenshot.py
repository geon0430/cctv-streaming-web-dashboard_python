import os
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import JSONResponse

async def save_screenshot(image: UploadFile, logger, ini_dict) -> JSONResponse:
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image type")
    
    save_directory = ini_dict['CONFIG']['SAVE_IMAGE_PATH']

    save_path = os.path.join(save_directory, image.filename)
    
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        logger.info(f"POST Router | save_screenshot | search_onvif_listCreated directory {save_directory}")

    try:
        with open(save_path, "wb") as buffer:
            buffer.write(await image.read())
    except Exception as e:
        logger.error(f"POST Router | ERROR | save_screenshot | Failed to save image: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save image: {str(e)}")
    
    logger.info(f"POST Router | save_screenshot | Image saved successfully at {save_path}")
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "success"})
