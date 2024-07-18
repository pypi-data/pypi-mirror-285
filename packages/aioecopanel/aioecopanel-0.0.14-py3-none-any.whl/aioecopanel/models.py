""" Model for BACnet add-on data."""
from dataclasses import dataclass
from typing import Any, Union

from .exceptions import DeviceDictEmpty, DeviceDictError, DeviceDictObjectEmpty

from .const import LOGGER


@dataclass
class Object:
    """Represent a BACnet object."""

    objectIdentifier: str
    objectType: str
    objectName: str
    description: str
    presentValue: Union[int, float, str, bool]
    statusFlags: Union[str, list]
    units: str
    outOfService: bool
    eventState: str
    reliability: str
    covIncrement: Union[int, float]
    vendorName: str
    modelName: str
    stateText: list
    numberOfStates: int
    notificationClass: int
    minPresValue: Union[int, float, str, bool]
    maxPresValue: Union[int, float, str, bool]
    resolution: Union[int, float]
    serialNumber: str

    def __post_init__(self):
        if self.objectIdentifier is None:
            raise DeviceDictObjectEmpty("objectIdentifier missing!")

    @property
    def id(self):
        return f"{self.objectIdentifier}"

    def __getattr__(self, name):
        if name == "id":
            return self.id
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError


@dataclass
class Device:
    """Represent a BACnet Device."""

    objects: dict[str, Object]

    @staticmethod
    def update_device(device_name: str, device_data: dict[str, Any]):
        """Update the device from device data."""
        objects = {}
        for object_name, object_data in device_data.items():
            try:
                object = Object(
                    object_data.get("objectIdentifier"),
                    object_data.get("objectType"),
                    object_data.get("objectName"),
                    object_data.get("description"),
                    object_data.get("presentValue"),
                    object_data.get("statusFlags"),
                    object_data.get("units"),
                    object_data.get("outOfService"),
                    object_data.get("eventState"),
                    object_data.get("reliability"),
                    object_data.get("covIncrement"),
                    object_data.get("vendorName"),
                    object_data.get("modelName"),
                    object_data.get("stateText"),
                    object_data.get("numberOfStates"),
                    object_data.get("notificationClass"),
                    object_data.get("minPresValue"),
                    object_data.get("maxPresValue"),
                    object_data.get("resolution"),
                    object_data.get("serialNumber"),
                )
                objects.update({object_name: object})
            except DeviceDictObjectEmpty as err:
                LOGGER.warning(f"{device_name} {object_name}, {object_data}: {err}")

        if objects is None:
            raise DeviceDictObjectEmpty

        return Device(objects)

    def __getattr__(self, name):
        try:
            return self.objects[name]
        except KeyError:
            raise AttributeError


class DeviceDict:
    """Represent a dictionary of all BACnet devices on the network."""

    devices: dict[str, Device] = {}

    def __init__(self, data: dict[str, Any]):
        if data is None:
            raise DeviceDictEmpty(f"Received empty data: {data}")
        self.update_from_data(data)

    def update_from_data(self, data: dict[str,Device | dict[str,Any]]):
        """Update the device dictionary from received data"""
        if data is None:
            raise DeviceDictEmpty(f"Received empty data: {data}")
        for device_name, device_data in data.items():
            if device_name is None or device_data is None:
                continue
            device = Device.update_device(device_name, device_data)
            self.devices.update({device_name: device})
        if self.devices is not None:
            return self
        else:
            raise DeviceDictEmpty(f"Previous None checks didn't prevent this!'")
