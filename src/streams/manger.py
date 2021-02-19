# coding= utf-8
import os
import threading

import serial
import serial.tools.list_ports as SerialManager
import time
from src.streams.Ntrip import NtripClient
from src.streams.serialport import SerialPort
from src.streams.filereader import FileWriter
from threading import Thread

mSerial = None

powerSerial = '/dev/cu.usbserial-14230'
fixedSerialList = []

switchOff = True


def find_serial():
    serialNameList = []
    portList = list(SerialManager.comports())
    for i in portList:
        serialPath = list(i)[0]
        if 'Bluetooth' not in serialPath:
            serialNameList.append(serialPath)
    return serialNameList


class Manager:
    _instance_lock = threading.Lock()

    def __init__(self, dir=os.path.abspath('../..') + "/data/"):
        self.dir = dir
        self.ntrip = NtripClient(mountPoint='Obs_20C')
        # self.ntrip = NtripClient(ip='lab.ntrip.qxwz.com', port=8002, user="stmicro0010", password='50fcc29',
        #                          mountPoint='SH_GALILEO')
        self.serial_list = list()
        self.portList = list()
        self.timeStr = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
        self.mSerial = None
        self.serialInUseNum = 0

    @classmethod
    def instance(cls, *arg, **kwargs):
        if not hasattr(Manager, "_instance"):
            with Manager._instance_lock:
                if not hasattr(Manager, "_instance"):
                    Manager._instance = Manager(*arg, **kwargs)

        return Manager._instance

    def start(self, powerTest=False):

        serial_name_list = find_serial()
        if len(serial_name_list) <= 0:
            return
        if powerTest:
            self.powerOn()

        for serialName in serial_name_list:

            if serialName in ['COM8', 'COM6', 'COM1'] or serialName == powerSerial:
                continue
            serialEntity = SerialPort(iport=serialName, baudRate=115200, showLog=True)
            try:
                serialEntity.start()
                # 检查是否是板卡使用的串口
                serialEntity.setSupportFmi(self.checkSerialIsSupport)
                # 测试开关上电
                if powerTest:
                    serialEntity.setCallback(self.checkSerialIsFixed)
            except Exception as e:
                print(e)
                continue
            self.serial_list.append(serialEntity)
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

    def serialList(self):
        return self.serial_list

    def getDir(self):
        return self.dir

    def powerOn(self):
        if self.mSerial is not None:
            return
        self.mSerial = serial.Serial(powerSerial, 9600)
        if self.mSerial.is_open:
            self.mSerial.close()
        self.mSerial.open()

        if switchOff:
            # close
            self.mSerial.write(bytes.fromhex("A0 01 00 A1"))
        else:
            # 开
            self.mSerial.write(bytes.fromhex("A0 01 01 A2"))

    def close_unSupport(self):
        time.sleep(30)
        for serial_entity in self.serial_list:
            if not serial_entity.getSupportFmi():
                continue
            if serial_entity.is_running():
                serial_entity.close_serial()

    def checkSerialIsSupport(self, port):
        print(port)
        for serial_entity in self.serial_list:
            print(port, serial_entity.getPort())
            if port == serial_entity.getPort():
                self.serialInUseNum += 1
                file = FileWriter(
                    serial_entity.getPort().split('/')[-1] + '_' + Manager.instance().timeStr + ".log",
                    Manager.instance().getDir())
                serial_entity.setFile(file, Manager.instance().timeStr)
                # if not self:
                serial_entity.send_data("AT+READ_PARA\r\n")
                Manager.instance().ntrip.register(serial_entity)

    def checkSerialIsFixed(self, port):

        if port not in fixedSerialList:
            fixedSerialList.append(port)
            if len(fixedSerialList) == self.serialInUseNum:
                self.switch()
                fixedSerialList.clear()

    def switch(self):
        if switchOff:
            # 打开
            self.mSerial.write(bytes.fromhex("A0 01 01 A2"))
            time.sleep(5)
            # 关闭
            self.mSerial.write(bytes.fromhex("A0 01 00 A1"))
        else:
            # 关闭
            self.mSerial.write(bytes.fromhex("A0 01 00 A1"))
            time.sleep(5)
            # 打开
            self.mSerial.write(bytes.fromhex("A0 01 01 A2"))


if __name__ == '__main__':
    # mSerial = serial.Serial(powerSerial, 9600)
    manager = Manager().instance()
    timeStr = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
    manager.start(powerTest=True)
