from typing import List, Optional
from utils.struct import APIstruct

class DBManager:
    def __init__(self):
        self.devices: List[APIstruct] = []

    def add_device(self, device: APIstruct):
        self.devices.append(device)

    def remove_device(self, device_idx: int) -> bool:
        device = self.get_device_by_idx(device_idx)
        if device:
            self.devices.remove(device)
            return True
        return False

    def update_device(self, device_idx: int, new_data: dict) -> bool:
        device = self.get_device_by_idx(device_idx)
        if device:
            for key, value in new_data.items():
                setattr(device, key, value)
            return True
        return False

    def get_all_devices(self, sort_by: Optional[str] = None, order: str = 'asc') -> List[APIstruct]:
        if sort_by:
            reverse = order == 'desc'
            return sorted(self.devices, key=lambda x: getattr(x, sort_by), reverse=reverse)
        return self.devices

    def get_device_by_idx(self, idx: int) -> Optional[APIstruct]:
        for device in self.devices:
            if device.idx == idx:
                return device
        return None
