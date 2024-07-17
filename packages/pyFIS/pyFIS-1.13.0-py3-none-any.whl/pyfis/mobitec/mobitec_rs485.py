"""
Copyright (C) 2023 Julian Metzler

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import serial
import time

from ..utils.base_serial import BaseSerialPort
from ..utils.utils import debug_hex


class MobitecRS485:
    """
    mobitec RS485 protocol
    """
    
    def __init__(self, port, address, debug = False, exclusive = True):
        self.address = address
        self.debug = debug
        if isinstance(port, serial.Serial) or isinstance(port, BaseSerialPort):
            self.port = port
        else:
            self.port = serial.Serial(port, baudrate=4800, timeout=2.0, exclusive=exclusive)
    
    def checksum(self, data):
        checksum = self.address
        for byte in data:
            checksum += byte
        checksum %= 0x100
        if checksum == 0xFF:
            return (0xFE, 0x01)
        else:
            return (checksum, 0x00)
    
    def send_frame(self, data):
        # Sends data, adds start/stop bytes and checksum
        frame = [0xFF, self.address]
        frame += data
        frame += self.checksum(data)
        frame.append(0xFF)
        if self.debug:
            print("TX: " + debug_hex(frame, readable_ascii=False, readable_ctrl=False))
        self.port.write(frame)
    
    def send_text(self, x, y, font, text):
        data = [0xA2, 0xD2, x, 0xD3, y, 0xD4, font]
        data += text.encode('ascii')
        return self.send_frame(data)
