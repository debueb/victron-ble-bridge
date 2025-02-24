import logging
from time import time
from typing import Any, Dict
from enum import Enum
from config import CONFIG
from bleak.backends.device import BLEDevice
from devices import Device
from requests import post
# import json

logger = logging.getLogger(__name__)

class RestClient:

    def __init__(self):
        self.url = CONFIG["server_url"]

    def add(self, blob: dict, device: Device, key: str) -> dict:
        if key in device._data:
            value = device._data[key]
            if isinstance(value, Enum):
                value = value.name.lower()
            if value is not None:
                blob["data"][key] = value

    def send(self, bleDevice: BLEDevice, device: Device):
        blob = {
            "name": bleDevice.name,
            "address": bleDevice.address,
            "model_name": device.get_model_name(),
            "data": {
                "timestamp": int(time()*1000),
            }
        }
        self.add(blob, device, "model_name")
        self.add(blob, device, "remaining_mins")
        self.add(blob, device, "charge_state")
        self.add(blob, device, "soc")
        self.add(blob, device, "solar_power")
        self.add(blob, device, "yield_today")

        # DCDC
        self.add(blob, device, "device_state")
        self.add(blob, device, "input_voltage")
        self.add(blob, device, "output_voltage")

        if "voltage" in device._data and "current" in device._data:
            blob["data"]["power"] = round(device._data["voltage"]*device._data["current"])

        # print(json.dumps(blob))
        post(f"{self.url}/api/device", json=blob)

