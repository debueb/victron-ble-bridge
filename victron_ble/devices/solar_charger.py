from construct import Int16sl, Int16ul, Struct
from typing import Optional

from devices.base import Device, DeviceData, OperationMode


class SolarChargerData(DeviceData):
    def get_charge_state(self) -> OperationMode:
        """
        Return an enum indicating the current charging state
        """
        return self._data["charge_state"]

    def get_battery_voltage(self) -> float:
        """
        Return the battery voltage in volts
        """
        return self._data["battery_voltage"]

    def get_battery_charging_current(self) -> float:
        """
        Return the battery charging current in amps
        """
        return self._data["battery_charging_current"]

    def get_yield_today(self) -> float:
        """
        Return the yield_today in Wh
        """
        return self._data["yield_today"]

    def get_solar_power(self) -> float:
        """
        Return the current solar power in W
        """
        return self._data["solar_power"]

    def get_external_device_load(self) -> Optional[float]:
        """
        Return the external device load in amps - if 0xFFFF no load output exists
        """
        if self._data["external_device_load"] == 0xFFFF:
            return None
        return (self._data["external_device_load"] & 0x01FF) / 10


class SolarCharger(Device):

    PACKET = Struct(
        # Charge State:   0 - Off
        #                 3 - Bulk
        #                 4 - Absorption
        #                 5 - Float
        "charge_state" / Int16sl,
        # Battery voltage reading in 0.01V increments
        "battery_voltage" / Int16ul,
        # Battery charging Current reading in 0.1A increments
        "battery_charging_current" / Int16ul,
        # Todays solar power yield in 10Wh increments
        "yield_today" / Int16ul,
        # Current power from solar in 1W increments
        "solar_power" / Int16ul,
        # External device load in 0.1A increments
        "external_device_load" / Int16ul,
    )

    def parse(self, data: bytes) -> SolarChargerData:
        decrypted = self.decrypt(data)
        pkt = self.PACKET.parse(decrypted)

        parsed = {
            "charge_state": OperationMode(pkt.charge_state),
            "battery_voltage": pkt.battery_voltage / 100,
            "battery_charging_current": pkt.battery_charging_current / 10,
            "yield_today": pkt.yield_today * 10,
            "solar_power": pkt.solar_power,
            "external_device_load": pkt.external_device_load,
        }

        return SolarChargerData(self.get_model_id(data), parsed)
