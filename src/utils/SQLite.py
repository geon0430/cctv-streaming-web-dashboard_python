from sqlmodel import SQLModel, Session, select, Field, asc, desc
from typing import Optional, Type
import sys
import traceback
sys.path.append("../")
from utils.struct import ChannelDBStruct, VideoPlayerStruct
from utils.aes import AESCipher

class SQLite:
    def __init__(self, engine, KEY, struct_type: Type[SQLModel], logger):
        self.engine = engine
        self.cipher = AESCipher(KEY)
        self.struct_type = struct_type
        self.logger = logger

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

    def update_entry(self, entry: SQLModel):
        with Session(self.engine) as session:
            session.add(entry)
            session.commit()

    def update_device_by_channel_id(self, idx: int, new_data: dict) -> bool:
        with Session(self.engine) as session:
            instance = session.exec(select(self.struct_type).where(self.struct_type.channel_id == idx)).first()
            if instance:
                for key, value in new_data.items():
                    setattr(instance, key, value)
                session.commit()
                return True
            return False

    def get_all_devices(self, sort_by: Optional[str] = None, order: str = 'asc'):
        try:
            with Session(self.engine) as session:
                query = select(self.struct_type)
                if sort_by:
                    if order == 'desc':
                        query = query.order_by(desc(getattr(self.struct_type, sort_by)))
                    else:
                        query = query.order_by(asc(getattr(self.struct_type, sort_by)))
                devices = session.exec(query).all()
                return devices
        except Exception as e:
            self.logger.error(f"Error in get_all_devices: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise e

    def get_device_by_idx(self, idx: int):
        try:
            with Session(self.engine) as session:
                return session.exec(select(self.struct_type).where(self.struct_type.channel_id == idx)).first()
        except Exception as e:
            self.logger.error(f"Error in get_device_by_idx: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise e

    def initialize_players(self, max_player: int):
        try:
            created_players = []
            with Session(self.engine) as session:
                for i in range(1, max_player + 1):
                    existing_player = session.exec(select(VideoPlayerStruct).where(VideoPlayerStruct.channel_id == i)).first()
                    if not existing_player:
                        player = VideoPlayerStruct(channel_id=i, onvif_result_address=None, height=0, width=0, fps=0.0, codec="")
                        session.add(player)
                        created_players.append(i)
                session.commit()
            if created_players:
                self.logger.info(f"Players with channel_id {created_players} created")
        except Exception as e:
            self.logger.error(f"Error in initialize_players: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise e

    def update_player(self, player_number: int, channel_info: dict):
        try:
            with Session(self.engine) as session:
                player = session.exec(select(VideoPlayerStruct).where(VideoPlayerStruct.channel_id == player_number)).first()
                if player:
                    for key, value in channel_info.items():
                        setattr(player, key, value)
                    session.commit()
                    self.logger.info(f"Updated player {player_number} with channel info: {channel_info}")
                else:
                    self.logger.error(f"Player {player_number} not found")
        except Exception as e:
            self.logger.error(f"Error in update_player: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise e

    def get_player_by_number(self, player_number: int):
        try:
            with Session(self.engine) as session:
                return session.exec(select(VideoPlayerStruct).where(VideoPlayerStruct.channel_id == player_number)).first()
        except Exception as e:
            self.logger.error(f"Error in get_player_by_number: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise e

    def get_all_players(self):
        try:
            with Session(self.engine) as session:
                return session.exec(select(VideoPlayerStruct)).all()
        except Exception as e:
            self.logger.error(f"Error in get_all_players: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise e

    def get_all_groups(self):
        try:
            with Session(self.engine) as session:
                query = select(self.struct_type.group).distinct()
                result = session.exec(query).all()
                groups = list(set(group for group in result if group and group.strip()))
            return groups
        except Exception as e:
            self.logger.error(f"Error in get_all_groups: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise e

    def get_all_channel_ids(self):
        try:
            with Session(self.engine) as session:
                query = select(VideoPlayerStruct.channel_id)
                result = session.exec(query).all()
                return [r[0] for r in result]
        except Exception as e:
            self.logger.error(f"Error in get_all_channel_ids: {str(e)}")
            self.logger.error(traceback.format_exc())
            raise e
