from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, create_engine
from fastapi.staticfiles import StaticFiles
import uvicorn

from utils import setup_logger, DBManager, ConfigManager
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

    DBNAME = ini_dict['CONFIG']['DB_NAME']
    KEY = ini_dict['CONFIG']['KEY']
    database_connection_string = f"sqlite:///{DBNAME}"
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_connection_string, echo=False, connect_args=connect_args)
    db_manager = DBManager(engine, KEY)

    SQLModel.metadata.create_all(engine)

    logger.info("DASHBOARD STARTED")

    app.state.logger = logger
    app.state.db_manager = db_manager
    app.state.ini_dict = ini_dict

app.on_event("startup")(startup_event)