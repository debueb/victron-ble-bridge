from VictronScanner import VictronScanner
from RestClient import RestClient
import asyncio
import click
import logging
from typing import List, Tuple, Optional
from bleak.backends.device import BLEDevice
from devices import Device
from config import CONFIG
from time import time
from typing import Any, Dict
from enum import Enum

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Increase logging output")
def cli(verbose):
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

@cli.command(help="scan for data from victron bluetooth devices specified in config.py")
def scan():

    loop = asyncio.new_event_loop()   
    restClient = RestClient()
    scanning = asyncio.Event()
    foundDevices = dict()
    timeout = CONFIG["timeout"]

    def add(blob: dict, device: Device, key: str) -> dict:
        if key in device._data:
            value = device._data[key]
            if isinstance(value, Enum):
                value = value.name.lower()
            if value is not None:
                blob["data"][key] = value
    
    def onDeviceFound(bleDevice: BLEDevice, device: Device):
        if (timeout > 0 and bleDevice.address not in foundDevices):
            print("found ", bleDevice.address)
            blob = {
                "name": bleDevice.name,
                "address": bleDevice.address,
                "model_name": device.get_model_name(),
                "data": {
                    "timestamp": int(time()*1000),
                }
            }
            add(blob, device, "model_name")
            add(blob, device, "remaining_mins")
            add(blob, device, "charge_state")
            add(blob, device, "soc")
            add(blob, device, "solar_power")
            add(blob, device, "yield_today")

            # DCDC
            add(blob, device, "device_state")
            add(blob, device, "input_voltage")
            add(blob, device, "output_voltage")

            if "voltage" in device._data and "current" in device._data:
                blob["data"]["power"] = round(device._data["voltage"]*device._data["current"])
                    
            foundDevices[bleDevice.address] = blob
            # if all devices have been found let the timeout loop stop of the scan
            if (len(foundDevices) == len(CONFIG['devices'].keys())):
                if scanning.is_set(): 
                    scanning.clear()


    async def startScanning():
        victronScanner = VictronScanner(onDeviceFound)     
        await victronScanner.start()
        
        scanning.set()
        end_time = loop.time() + timeout
        while scanning.is_set():
            if loop.time() > end_time:
                scanning.clear()
                print('\nScan has timed out so we terminate')
            await asyncio.sleep(0.1)
        await victronScanner.stop()
        restClient.send(list(foundDevices.values()))

    loop.run_until_complete(startScanning())

if __name__ == "__main__":
    cli()