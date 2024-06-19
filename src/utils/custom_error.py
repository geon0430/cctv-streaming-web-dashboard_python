import re
import socket
from typing import List
from utils.struct import ONVIFstruct


async def onvif_list_check(db_manager, json_list: List[ONVIFstruct], request=None) -> str:
    for new_item in json_list:
        for existing_item in db_manager.get_all_devices():
            if new_item.name == existing_item.name:
                return 'duplicate_name'
            if new_item.ip_address == existing_item.ip_address:
                return 'duplicate_ip'
    return "no_duplicate"



def port_open_check(ip_address: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex((ip_address, port))
    sock.close()
    return result == 0
