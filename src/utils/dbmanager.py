from sqlmodel import SQLModel, Session, select, asc, desc, Field
from typing import Optional, Type
import shortuuid
import sys
sys.path.append("../")
from utils.struct import ChannelDBStruct, VideoPlayerStruct
from utils.aes import AESCipher

class DBManager:
    def __init__(self, engine, KEY, struct_type: Type[SQLModel]):
        self.engine = engine
        self.cipher = AESCipher(KEY)
        self.struct_type = struct_type

    def add_device(self, device: SQLModel):
        with Session(self.engine) as session:
            session.add(device)
            session.commit()
            session.refresh(device) 

    def remove_device(self, device_idx: int) -> bool:
        with Session(self.engine) as session:
            instance = session.exec(select(self.struct_type).where(self.struct_type.idx == device_idx)).first()
            if instance:
                session.delete(instance)
                session.commit()
                return True
            return False

    def update_device(self, device_idx: int, new_data: dict) -> bool:
        with Session(self.engine) as session:
            instance = session.exec(select(self.struct_type).where(self.struct_type.idx == device_idx)).first()
            if instance:
                for key, value in new_data.items():
                    setattr(instance, key, value)
                session.commit()
                return True
            return False

    def get_all_devices(self, sort_by: Optional[str] = None, order: str = 'asc'):
        with Session(self.engine) as session:
            query = select(self.struct_type)
            if sort_by:
                if order == 'desc':
                    query = query.order_by(desc(getattr(self.struct_type, sort_by)))
                else:
                    query = query.order_by(asc(getattr(self.struct_type, sort_by)))
            devices = session.exec(query).all()
            return devices

    def get_device_by_idx(self, idx: int):
        with Session(self.engine) as session:
            return session.exec(select(self.struct_type).where(self.struct_type.idx == idx)).first()

    def initialize_players(self):
        with Session(self.engine) as session:
            for i in range(1, 17):  
                player = VideoPlayerStruct(player_number=i, channel_id=None)
                session.add(player)
            session.commit()

    def update_player(self, player_number: int, channel_id: Optional[int]):
        with Session(self.engine) as session:
            player = session.exec(select(VideoPlayerStruct).where(VideoPlayerStruct.player_number == player_number)).first()
            if player:
                player.channel_id = channel_id
                session.commit()

    def get_player_by_number(self, player_number: int):
        with Session(self.engine) as session:
            return session.exec(select(VideoPlayerStruct).where(VideoPlayerStruct.player_number == player_number)).first()

    def get_all_players(self):
        with Session(self.engine) as session:
            return session.exec(select(VideoPlayerStruct)).all()
        
    def get_all_groups(self):
        with Session(self.engine) as session:
            query = select(self.struct_type.group).distinct()
            result = session.exec(query).all()
            groups = list(set(group for group in result if group and group.strip()))
        return groups
