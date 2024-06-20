from sqlmodel import Session, select, asc, desc
from typing import Optional
import shortuuid
import sys
sys.path.append("../")
from utils.struct import DBStruct
from utils.aes import AESCipher

class DBManager:
    def __init__(self, engine, KEY):
        self.engine = engine
        self.cipher = AESCipher(KEY)

    def add_device(self, device):
        with Session(self.engine) as session:
            session.add(device)
            session.commit()

    def remove_device(self, device_idx: int) -> bool:
        with Session(self.engine) as session:
            instance = session.exec(select(DBStruct).where(DBStruct.idx == device_idx)).first()
            if instance:
                session.delete(instance)
                session.commit()
                return True
            return False

    def update_device(self, device_idx, new_data):
        with Session(self.engine) as session:
            instance = session.exec(select(DBStruct).where(DBStruct.idx == device_idx)).first()
            if instance:
                for key, value in new_data.items():
                    setattr(instance, key, value)
                session.commit()
                return True
            return False

    def get_all_devices(self, sort_by: Optional[str] = None, order: str = 'asc'):
        with Session(self.engine) as session:
            query = select(DBStruct)
            if sort_by:
                if order == 'desc':
                    query = query.order_by(desc(getattr(DBStruct, sort_by)))
                else:
                    query = query.order_by(asc(getattr(DBStruct, sort_by)))
            devices = session.exec(query).all()
            return devices

    def get_device_by_idx(self, idx: int):
        with Session(self.engine) as session:
            return session.exec(select(DBStruct).where(DBStruct.idx == idx)).first()

    async def name_create(db_manager, name_length):
        existing_names = {device.name for device in db_manager.get_all_devices()}
        epoch = 0

        while True:
            if epoch > 30:
                name_length += 1  
                epoch = 0  

            new_name = shortuuid.uuid()[:name_length]
            if new_name not in existing_names:
                return new_name  
            epoch += 1
