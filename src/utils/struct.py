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
    
class ChannelAddstruct(BaseModel):
    id: str
    pw: Optional[str]
    name: str
    onvif_result_address: Optional[str]
    height: int
    width: int
    fps: int
    codec: str
    group: str
    

class ChannelDBStruct(SQLModel, table=True):
    idx: Optional[int] = Field(default=None, primary_key=True)
    id: str
    pw: Optional[str]
    name: str
    onvif_result_address: Optional[str]
    height: int
    width: int
    fps: float
    codec: str
    create_time: str
    group: str
    
class VideoPlayerStruct(SQLModel, table=True):
    idx: Optional[int] = Field(default=None, primary_key=True)
    onvif_result_address: Optional[str]
    height: int
    width: int
    fps: float
    codec: str

    
