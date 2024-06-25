from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from fastapi.staticfiles import StaticFiles
import uvicorn

from utils import setup_logger, DBManager, ConfigManager
from utils.struct import ChannelDBStruct, VideoPlayerStruct
from routers import root, post_router, get_router, delete_router, put_router

app = FastAPI()

app.mount("/static/", StaticFiles(directory="/webrtc_python/src/web/static/"), name="static")

app.include_router(root)
app.include_router(post_router)
app.include_router(get_router)
app.include_router(delete_router)
app.include_router(put_router)

async def startup_event():
    api_ini_path = "/webrtc_python/src/config.ini"
    api_config = ConfigManager(api_ini_path)
    ini_dict = api_config.get_config_dict()
    logger = setup_logger(ini_dict)

    Channel_DB_NAME = ini_dict['CONFIG']['CHANNEL_DB_NAME']
    KEY = ini_dict['CONFIG']['KEY']
    channel_database_connection_string = f"sqlite:///{Channel_DB_NAME}"
    connect_args = {"check_same_thread": False}
    channel_engine = create_engine(channel_database_connection_string, echo=False, connect_args=connect_args)
    
    PLAYER_DB_NAME = ini_dict['CONFIG']['PLAYER_DB_NAME']
    player_database_connection_string = f"sqlite:///{PLAYER_DB_NAME}"
    connect_args_player = {"check_same_thread": False}
    player_engine = create_engine(player_database_connection_string, echo=False, connect_args=connect_args_player)
    
    db_manager_channel = DBManager(channel_engine, KEY, ChannelDBStruct)
    db_manager_player = DBManager(player_engine, KEY, VideoPlayerStruct)

    SQLModel.metadata.create_all(channel_engine)
    SQLModel.metadata.create_all(player_engine)

    logger.info("DASHBOARD STARTED")

    app.state.logger = logger
    app.state.channel_db = db_manager_channel
    app.state.player_db = db_manager_player
    app.state.ini_dict = ini_dict

app.on_event("startup")(startup_event)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
