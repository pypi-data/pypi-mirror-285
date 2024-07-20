# Copyright 2019 Nicolas OBERLI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from .rawwire import RawWire


class CCDbg(RawWire):
    """
    CC Debugger protocol handler

    :example:

    >>> import pyHydrabus
    >>> swd = pyHydrabus.SWD('/dev/ttyACM0')
    >>> swd.bus_init()
    >>> swd.read_dp(0)
    >>> swd.write_dp(4, 0x50000000)
    >>> swd.scan_bus()

    """

    def __init__(self, port=""):
        super().__init__(port)

        self._config = 0x8
        self._configure_port()

        self._hydrabus.write(b"\xf0\x0e")
        self._hydrabus.write(b"\x44")

    @property
    def nrst(self):
        """
        nRST (PC4) status
        """
        CMD = 0b11000000
        self._hydrabus.write(CMD.to_bytes(1, byteorder="little"))
        val = self._hydrabus.read(1)
        return val
        if (val & 0b1) == 0b1:
            return 1
        else:
            return 0

    @nrst.setter
    def nrst(self, value):
        CMD = 0b11010000
        CMD = CMD | value
        self._hydrabus.write(CMD.to_bytes(1, byteorder="little"))
        if self._hydrabus.read(1) == b"\x01":
            return True
        else:
            self._logger.error("Error setting nRST.")
            return False

    def init_debug(self):
        self.nrst = 0
        self.clocks(2)
        self.nrst = 1

    def read_chip_id(self):
        self.write(b'\x68')
        return self.read(2)

