# coding= utf-8
import os

import serial.tools.list_ports as SerialManager
import time
from src.streams.Ntrip import NtripClient
from src.streams.serialport import SerialPort
from src.streams.filereader import FileWriter


class Manager:

    def __init__(self):
        self._ntrip = NtripClient(mountPoint='Obs20')
        self._serial_list = list()
        self.port = ''

    def find_serial(self):
        portList = list(SerialManager.comports())
        # just for test
        for i in portList:
            line = list(i)
            print(line)
            print(line[0])
            self.port = line[0]
        return 'Bluetooth' not in self.port

    def start(self):
        file = FileWriter(
            self.port.split('/')[-1] + '-' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) + ".log",
            dir=os.path.abspath('../../data'))
        serial = SerialPort(iport=self.port, fileWriter=file, baudRate=115200, showLog=True)
        self._serial_list.append(serial)
        self._ntrip.register(serial)
        for serial in self._serial_list:
            serial.start()
        self._ntrip.start()

    def stop(self):
        pass


if __name__ == '__main__':
    manager = Manager()
    isFound = manager.find_serial()
    if isFound is True:
        manager.start()
