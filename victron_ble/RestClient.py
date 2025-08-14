import logging
from config import CONFIG
from bleak.backends.device import BLEDevice
from devices import Device
from requests import post
import json

logger = logging.getLogger(__name__)

class RestClient:

    def __init__(self):
        self.url = CONFIG["server_url"]

    def send(self, devices: list):
        
        print(devices)
        post(f"{self.url}/api/devices", json=devices, timeout=60)
