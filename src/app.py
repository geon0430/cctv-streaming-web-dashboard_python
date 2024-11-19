from fastapi import FastAPI
from sqlmodel import SQLModel, create_engine
from fastapi.staticfiles import StaticFiles
import uvicorn
from utils import setup_logger, DBManager, ConfigManager
from utils.struct import ChannelDBStruct, VideoPlayerStruct
from routers import root, post_router, get_router, delete_router, put_router

app = FastAPI()

app.mount("/static/", StaticFiles(directory="/cctv-streaming-web-dashboard_python/src/web/static/"), name="static")

app.include_router(root)
app.include_router(post_router)
app.include_router(get_router)
app.include_router(delete_router)
app.include_router(put_router)

async def startup_event():
    api_ini_path = "/cctv-streaming-web-dashboard_python/src/config.ini"
    api_config = ConfigManager(api_ini_path)
    ini_dict = api_config.get_config_dict()
    logger = setup_logger(ini_dict)

    DB_NAME = ini_dict['CONFIG']['DB_NAME']
    KEY = ini_dict['CONFIG']['KEY']
    database_connection_string = f"sqlite:///{DB_NAME}"
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_connection_string, echo=False, connect_args=connect_args)
    
    db_manager_channel = DBManager(engine, KEY, ChannelDBStruct, logger)
    db_manager_player = DBManager(engine, KEY, VideoPlayerStruct, logger)

    SQLModel.metadata.create_all(engine)

    max_player = ini_dict['CONFIG']['MAX_CHANNEL']
    db_manager_player.initialize_players(max_player)

    logger.info("DASHBOARD STARTED")

    app.state.logger = logger
    app.state.channel_db = db_manager_channel
    app.state.player_db = db_manager_player
    app.state.ini_dict = ini_dict

app.on_event("startup")(startup_event)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)