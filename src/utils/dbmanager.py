from utils.struct import APIstruct

class DBManager:
    def __init__(self):
        self.db_list = []  

    def get_db(self):
        return self.db_list  
    
    def add_device(self, device):
        self.db_list.append(device)

    def remove_device(self, device_id: int) -> bool:
        original_length = len(self.db_list)
        self.db_list = [device for device in self.db_list if device.id != device_id]
        return len(self.db_list) < original_length

    def update_device(self, device_id, new_device):
        for i, device in enumerate(self.db_list):
            if device.id == device_id:
                self.db_list[i] = new_device
                return True 
    def set_db(self, new_db_list):
        self.db_list = [APIstruct(**item) for item in new_db_list]

        return False