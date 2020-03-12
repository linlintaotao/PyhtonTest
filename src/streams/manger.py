# coding= utf-8
import os

# import serial.tools.list_ports as SerialManager
import time
from src.streams.Ntrip import NtripClient
from src.streams.serialport import SerialPort
from src.streams.filereader import FileWriter
from serial.tools import list_ports


def find_serial():
    serialNameList = []
    portList = list(list_ports.comports())
    for i in portList:
        serialPath = list(i)[0]
        if 'Bluetooth' not in serialPath:
            print(serialPath)
            serialNameList.append(serialPath)
    return serialNameList


class Manager:

    def __init__(self):
        self._ntrip = NtripClient(mountPoint='Obs')
        self._serial_list = list()
        self.portList = list()

    def start(self):
        serialList = find_serial()

        if len(serialList) <= 0:
            return False
        for serialName in serialList:

            serial = SerialPort(iport=serialName, baudRate=115200, showLog=True)
            try:
                serial.start()
            except:
                print("can not use seial %s" % serialName)
                continue
            file = FileWriter(
                serialName.split('-')[-1] + '-' + time.strftime('%Y%m%d-%H:%M:%S',
                                                                time.localtime(time.time())) + ".log",
                dir=os.path.abspath('../../data'))
            serial.setFile(file)
            self._serial_list.append(serial)
            self._ntrip.register(serial)

        self._ntrip.start()
        return True


def stop(self):
    for serialPort in self._serial_list:
        if serialPort is not None:
            serialPort.stop()
    self._ntrip.stop()


if __name__ == '__main__':
    manager = Manager()
    manager.start()
