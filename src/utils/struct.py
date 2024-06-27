from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from typing import List
from typing import Optional

class Offer(BaseModel):
    sdp: str
    type: str

class ONVIFstruct(BaseModel):
    id: Optional[str] = Field(index=True)
    pw: Optional[str]
    ip_address: Optional[str]
    
class RTSPChannelStruct(BaseModel):
    address: str
    id: str
    password: str
    group: Optional[str]

class ChannelAddstruct(BaseModel):
    ip: str
    onvif_result_address: Optional[str]
    height: int
    width: int
    fps: int
    codec: str
    group: str
    

class ChannelDBStruct(SQLModel, table=True):
    idx: Optional[int] = Field(default=None, primary_key=True)
    ip : str
    onvif_result_address: Optional[str]
    height: int
    width: int
    fps: float
    codec: str
    create_time: str
    group: str
    
class VideoPlayerStruct(SQLModel, table=True):
    channel_id: Optional[int] = Field(default=None, primary_key=True)
    onvif_result_address: Optional[str] = None
    height: int = 0
    width: int = 0
    fps: float = 0.0
    codec: str = ""
