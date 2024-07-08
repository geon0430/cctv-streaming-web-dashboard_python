from fastapi import HTTPException, status
from starlette.requests import HTTPConnection

def get_player_db(conn: HTTPConnection):
    try:
        db_manager = conn.app.state.player_db
        if db_manager is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Manager not initialized")
        return db_manager
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Manager attribute not found in app state")

def get_channel_db(conn: HTTPConnection):
    try:
        db_manager = conn.app.state.channel_db
        if db_manager is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Manager not initialized")
        return db_manager
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="DB Manager attribute not found in app state")

def get_logger(conn: HTTPConnection):
    try:
        logger = conn.app.state.logger
        if logger is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logger not initialized")
        return logger
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Logger attribute not found in app state")

def get_ini_dict(conn: HTTPConnection):
    try:
        ini_dict = conn.app.state.ini_dict
        if ini_dict is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ini_dict not initialized")
        return ini_dict
    except AttributeError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="ini_dict attribute not found in app state")
