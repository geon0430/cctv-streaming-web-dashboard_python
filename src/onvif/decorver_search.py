import socket
import struct
import netifaces as ni
from datetime import datetime
import xml.etree.ElementTree as ET
import ipaddress
import sys
sys.path.append("../")
from utils import setup_logger, ConfigManager

def get_local_ip_and_subnet(iface='eth0'):  # 인터페이스 이름을 eth0으로 변경
    try:
        ip_info = ni.ifaddresses(iface)[ni.AF_INET][0]
        ip = ip_info['addr']
        subnet_mask = ip_info['netmask']
        return ip, subnet_mask
    except KeyError:
        raise ValueError(f"Interface {iface} not found or doesn't have an IP address")

def calculate_ip_range(ip, netmask):
    network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
    return [str(ip) for ip in network.hosts()]

def discover_onvif_devices(logger, ip_range, timeout=5):
    message_id = f'uuid:{datetime.now().strftime("%Y%m%d%H%M%S%f")}'
    probe_message = f'''<?xml version="1.0" encoding="UTF-8"?>
    <e:Envelope xmlns:e="http://www.w3.org/2003/05/soap-envelope"
                xmlns:w="http://schemas.xmlsoap.org/ws/2004/08/addressing"
                xmlns:d="http://schemas.xmlsoap.org/ws/2005/04/discovery"
                xmlns:dn="http://www.onvif.org/ver10/network/wsdl">
      <e:Header>
        <w:MessageID>{message_id}</w:MessageID>
        <w:To>urn:schemas-xmlsoap-org:ws:2005:04:discovery</w:To>
        <w:Action>http://schemas.xmlsoap.org/ws/2005/04/discovery/Probe</w:Action>
      </e:Header>
      <e:Body>
        <d:Probe>
          <d:Types>dn:NetworkVideoTransmitter</d:Types>
        </d:Probe>
      </e:Body>
    </e:Envelope>'''

    devices = []

    for ip in ip_range:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(timeout)

            logger.info(f"discover_onvif_devices | Sending ONVIF discovery probe message to {ip}")
            sock.sendto(probe_message.encode('utf-8'), (ip, 3702))

            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < timeout:
                try:
                    data, address = sock.recvfrom(4096)
                    device_info = parse_onvif_response(data, logger)
                    if device_info and device_info not in devices:
                        device_info['ip'] = address[0]
                        devices.append(device_info)
                        logger.info(f"discover_onvif_devices | Device discovered: {device_info}")
                except socket.timeout:
                    logger.info(f"discover_onvif_devices | Socket timeout for {ip}, ending discovery")
                    break

            sock.close()
        except Exception as e:
            logger.error(f"discover_onvif_devices | ERROR | Exception occurred while probing {ip}: {str(e)}")

    logger.info(f"discover_onvif_devices | Discovery completed, {len(devices)} devices found")
    return devices

def parse_onvif_response(response, logger):
    try:
        ns = {
            'SOAP-ENV': 'http://www.w3.org/2003/05/soap-envelope',
            'wsd': 'http://schemas.xmlsoap.org/ws/2005/04/discovery',
            'wsa': 'http://schemas.xmlsoap.org/ws/2004/08/addressing',
            'dn': 'http://www.onvif.org/ver10/network/wsdl'
        }
        root = ET.fromstring(response)
        urn = root.find('.//wsa:Address', ns).text
        types = root.find('.//wsd:Types', ns).text
        scopes = [scope.text for scope in root.findall('.//wsd:Scopes', ns)]
        xaddrs = [xaddr.text for xaddr in root.findall('.//wsd:XAddrs', ns)]

        return {
            'urn': urn,
            'types': types,
            'scopes': scopes,
            'xaddrs': xaddrs
        }
    except Exception as e:
        logger.error(f"discover_onvif_devices | ERROR | Failed to parse ONVIF response: {str(e)}")
        return None

if __name__ == "__main__":
    api_ini_path = "/webrtc_python/src/config.ini"
    api_config = ConfigManager(api_ini_path)
    ini_dict = api_config.get_config_dict()
    logger = setup_logger(ini_dict)

    local_ip, subnet_mask = get_local_ip_and_subnet()

    ip_range = calculate_ip_range(local_ip, subnet_mask)

    discovered_devices = discover_onvif_devices(logger, ip_range, timeout=5)
    
    if not discovered_devices:
        print([])
    else:
        device_ips = [device['ip'] for device in discovered_devices]
        print(device_ips)
