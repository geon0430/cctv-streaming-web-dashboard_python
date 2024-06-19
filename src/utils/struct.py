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
    
class APIstruct(BaseModel):
    id: int
    name: str
    id: Optional[str] = Field(index=True)
    pw: Optional[str]
    ip_address: Optional[str]
    

class DB(BaseModel):
    id: int
    name: str
    gpu: int
    id: Optional[str] = Field(index=True)
    pw: Optional[str]
    ip_address: Optional[str]

