# coding= utf-8
import os
import serial
import serial.tools.list_ports as SerialManager
import time
from src.streams.Ntrip import NtripClient
from src.streams.serialport import SerialPort
from src.streams.filereader import FileWriter


def find_serial():
    serialNameList = []
    portList = list(SerialManager.comports())
    for i in portList:
        serialPath = list(i)[0]
        print(serialPath)
        if 'Bluetooth' not in serialPath:
            serialNameList.append(serialPath)
    return serialNameList


class Manager:

    def __init__(self):
        self._ntrip = NtripClient(mountPoint='Obs_yf')
        self._serial_list = list()
        self.portList = list()

    def start(self):
        serialList = find_serial()

        if len(serialList) <= 0:
            return False

        start()

        timeStr = time.strftime('%Y%m%d-%H:%M:%S', time.localtime(time.time()))
        serialName = '/dev/cu.usbserial-1420'
        serial = SerialPort(iport=serialName, baudRate=115200, showLog=True)
        try:
            serial.start()
            serial.setCallback(switch)

        except:
            pass

        file = FileWriter(
            serialName.split('-')[-1] + '-' + timeStr + ".log", dir=os.path.abspath('../../data'))
        serial.setFile(file, timeStr)
        #
        self._serial_list.append(serial)
        self._ntrip.register(serial)
        self._ntrip.start()

        return True

    def sendOrder(self, order):
        for serialEnetity in self._serial_list:
            serialEnetity.send_data(order)
            pass

    def stop(self):
        for serialPort in self._serial_list:
            if serialPort is not None:
                serialPort.stop()
        self._ntrip.stop()


def switch():
    # if self.mSerial.is_open:
    #     self.mSerial.close()
    # self.mSerial.open()
    mSerial.write(bytes.fromhex("A0 01 00 A1"))
    time.sleep(4)
    mSerial.write(bytes.fromhex("A0 01 01 A2"))


mSerial = serial.Serial('/dev/cu.usbserial-1410', 9600)


def start():
    # mSerial = serial.Serial('/dev/cu.usbserial-1410', 9600)
    # mSerial.open()
    # 开
    mSerial.write(bytes.fromhex("A0 01 01 A2"))
    # 关
    # self.mSerial.write(bytes.fromhex("A0 01 00 A1"))


def stop():
    mSerial.close()


if __name__ == '__main__':
    manager = Manager()
    find_serial()
    # manager.autoClose()
    try:
        manager.start()
        manager.sendOrder("AT+READ_PARA\r\n")
    except Exception as e:
        manager.stop()
