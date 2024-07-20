from bec_lib.devicemanager import DeviceContainer
from bec_lib.tests.utils import ConnectorMock


# pylint: disable=missing-function-docstring
# pylint: disable=protected-access
class DeviceMock:
    def __init__(self, name: str, value=None):
        self.name = name
        self.read_buffer = {self.name: {"value": value}} if value is not None else None
        self._config = {"deviceConfig": {"limits": [-50, 50]}, "userParameter": None}
        self._read_only = False
        self._enabled = True

    def read(self):
        return self.read_buffer

    def readback(self):
        return self.read_buffer

    @property
    def obj(self):
        return self

    @property
    def limits(self):
        return self._config["deviceConfig"]["limits"]

    @property
    def read_only(self) -> bool:
        return self._read_only

    @read_only.setter
    def read_only(self, val: bool):
        self._read_only = val

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, val: bool):
        self._enabled = val

    @property
    def user_parameter(self):
        return self._config["userParameter"]


class DMMock:
    devices = DeviceContainer()
    connector = ConnectorMock()

    def add_device(self, name, value=None):
        self.devices[name] = DeviceMock(name, value=value)
