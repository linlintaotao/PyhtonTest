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
from threading import Timer

mSerial = None
powerSerial = '/dev/cu.usbserial-14230'
fixedSerialList = []
switchOff = True
manager = None

resetTestList = []  # 'COM30', 'COM88'


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
        # self.ntrip = NtripClient(mountPoint='Obs_20C')

        self.ntrip = NtripClient(ip='ntrips.feymani.cn', port=2102, user="feyman-user", password='123456',
                                 mountPoint='Obs_yd')
        # self.ntrip = NtripClient(ip='219.142.87.107', port=81, user="feyman-user", password='123456',
        #                         mountPoint='Obs_yd')
        self.ntrip.setDir(self.dir)
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
            baudrate = 115200
            if serialName in ['COM100']:
                baudrate = 460800
            serialEntity = SerialPort(iport=serialName, baudRate=baudrate, showLog=True)
            try:
                serialEntity.start()
                # 检查是否是板卡使用的串口
                serialEntity.setSupportFmi(self.checkSerialIsSupport)
                if serialName in resetTestList:
                    serialEntity.logStateTime(True, warmResetInterval=0)
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
        for serial_entity in self.serial_list:
            print(port, serial_entity.getPort())
            if port == serial_entity.getPort():
                self.serialInUseNum += 1
                tag = "RESET_TEST_" if port in resetTestList else ""
                file = FileWriter(
                    serial_entity.getPort().split('/')[-1] + '_' + tag + Manager.instance().timeStr + ".log",
                    Manager.instance().getDir())
                serial_entity.setFile(file, Manager.instance().timeStr)
                # if not self:
                serial_entity.send_data("AT+READ_PARA\r\n")
                Manager.instance().ntrip.register(serial_entity)
                serial_entity.writeSerialData(Manager.instance().ntrip.getInfo())
                break

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


def stop():
    print("================stop")
    if manager is not None:
        manager.stop()


if __name__ == '__main__':
    # mSerial = serial.Serial(powerSerial, 9600)
    manager = Manager().instance()
    timeStr = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
    manager.start(powerTest=False)
    scheduler = Timer(60 * 10, stop)
    scheduler.start()
    scheduler.join()
