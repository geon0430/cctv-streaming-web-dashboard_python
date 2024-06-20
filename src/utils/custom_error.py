import re
import socket
from typing import List
from utils.struct import ONVIFstruct

def onvif_list_type_check(devices: List[ONVIFstruct]) -> bool:
    try:
        for device in devices:
            if not (isinstance(device.ip_address, str) and isinstance(device.id, str) and isinstance(device.pw, str)):
                raise ValueError(f"Device attributes must be strings. Got: ip={type(device.ip_address)}, id={type(device.id)}, pw={type(device.pw)}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False



def port_open_check(ip_address: str, port: int) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex((ip_address, port))
    sock.close()
    return result == 0
