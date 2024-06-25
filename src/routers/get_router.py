from fastapi import APIRouter, Depends, HTTPException, status
from utils import get_logger, get_channel_db

get_router = APIRouter()

@get_router.get("/get_groups/", status_code=status.HTTP_200_OK)
async def get_groups_endpoint(channel_db = Depends(get_channel_db), logger = Depends(get_logger)):
    try:
        groups = channel_db.get_all_groups()
        logger.info(f"Get_Router | group get :  {groups}")
        return groups
    except Exception as e:
        logger.error(f"Get_Router | ERROR | Exception occurred during group fetch: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch groups")
