# coding= utf-8
import os
import serial
import serial.tools.list_ports as SerialManager
import time
from src.streams.Ntrip import NtripClient
from src.streams.serialport import SerialPort
from src.streams.filereader import FileWriter

mSerial = None


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
        self.ntrip = NtripClient(mountPoint='Obs')
        self.serial_list = list()
        self.portList = list()
        self.timeStr = ""

    def start(self, powerTest=False):
        self.serial_list = find_serial()

        if len(self.serialList) <= 0:
            return
        if powerTest:
            powerOn()
        for serialName in self.serialList:
            serialEntity = SerialPort(iport=serialName, baudRate=115200, showLog=True)
            try:
                serialEntity.start()
                # 检查是否是板卡使用的串口
                serialEntity.setSupportFmi(checkSerialIsSupport)
                # 测试开关上电
                if powerTest:
                    serialEntity.setCallback(switch)

            except Exception as e:
                print(e)

        self.ntrip.start()

    def sendOrder(self, order):
        for serialEntity in self.serial_list:
            serialEntity.send_data(order)
            pass

    def stop(self):
        self.ntrip.stop()
        for serialPort in self.serial_list:
            if serialPort is not None:
                serialPort.close_serial()


def checkSerialIsSupport(serialUse):
    file = FileWriter(
        serialUse.serialName.split('-')[-1] + '-' + timeStr + ".log", dir=os.path.abspath('../../data'))
    serialUse.setFile(file, timeStr)
    # manager.serial_list.append(serialUse)
    manager.ntrip.register(serialUse)


def switch():
    # 关闭
    mSerial.write(bytes.fromhex("A0 01 00 A1"))
    time.sleep(4)
    # 打开
    mSerial.write(bytes.fromhex("A0 01 01 A2"))


def powerOn():
    if mSerial.is_open:
        mSerial.close()
    mSerial.open()
    # 开
    mSerial.write(bytes.fromhex("A0 01 01 A2"))


def stop():
    mSerial.close()


if __name__ == '__main__':
    mSerial = serial.Serial('/dev/cu.usbserial-1420', 9600)
    manager = Manager()
    find_serial()
    timeStr = time.strftime('%Y%m%d-%H%M%S', time.localtime(time.time()))
    try:
        manager.start()
        manager.sendOrder("AT+READ_PARA\r\n")
    except Exception as e:
        manager.stop()
        stop()
