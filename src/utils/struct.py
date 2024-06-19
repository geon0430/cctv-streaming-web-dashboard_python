from pydantic import BaseModel
from typing import Optional, List

class APIstruct(BaseModel):
    id: int
    name: str

json_list: List[APIstruct] = []

class DB(BaseModel):
    id: int
    name: str
    gpu: int

db_list: List[DB] = []
