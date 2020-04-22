# coding= utf-8

import serial
from threading import Thread
import serial.tools.list_ports
import time

maxCount = 1e4


class SerialPort:
    def __init__(self, iport, fileWriter=None, baudRate=115200, showLog=False):
        self._port = iport
        self._baudRate = baudRate
        self._showLog = showLog
        self._read_thread = None
        self._entity = None
        self._file = fileWriter
        self.connectTimes = 0
        self.sendTimes = 0
        self.serialDemo = []
        self.callback = None
        self.fixCount = maxCount

    def setCallback(self, callback):
        self.callback = callback

    def getPort(self):
        return self._port

    def setFile(self, fileWriter, timeStr):
        self._file = fileWriter
        self._file.write('StartTime =' + timeStr + '\r\n')

    def is_running(self):
        return self._entity.isOpen()

    def open_serial(self):
        self._entity = serial.Serial(self._port, self._baudRate, timeout=3)
        if self._entity.isOpen():
            self._entity.close()
        try:
            self._entity.open()
        except:
            raise IOError(f'can not open serial{self._port}:{self._baudRate}')
            pass

    def close_serial(self):
        self._entity.close()
        if self._file:
            self._file.close()

    def send_data(self, data):
        if self._entity.is_open:
            print("send data = %s" % str(data))
            if type(data) is str:
                data = data.encode()
            self._entity.write(data)

    def read_data(self):
        data = self._entity.readline()
        if len(data) <= 0:
            return None
        if self._showLog is True:
            print(data)
            self.autoTest(data)
            pass
        if self._file:
            self._file.write(data)
        return data

    def notify(self, data):
        try:
            if self._entity.is_open:
                self._entity.write(data)
        except Exception as e:
            print(e)
            pass

    def read_thread(self):
        while self._entity.is_open:
            self.read_data()

    def start(self):
        if self._entity is None:
            self.open_serial()

        if self._read_thread is None:
            self._read_thread = None
        self._read_thread = Thread(target=self.read_thread)
        self._read_thread.start()

    def autoTest(self, data):

        if '+++ license activated' in str(data):
            self.connectTimes = 0
            self.fixCount = 50

        if ('E,9' in str(data)) | ('E,4' in str(data)):
            self.connectTimes += 1
            if self.connectTimes > self.fixCount:
                self.connectTimes = 0
                self.fixCount = maxCount
                self.callback()

    # def switch(self):
    #     # if self.mSerial.is_open:
    #     #     self.mSerial.close()
    #     # self.mSerial.open()
    #     self.mSerial.write(bytes.fromhex("A0 01 00 A1"))
    #     time.sleep(2)
    #     self.mSerial.write(bytes.fromhex("A0 01 01 A2"))
    #     # self.mSerial.close()

    def warmStart(self):
        self.send_data('AT+WARM_RESET\r\n')
        timeNow = time.strftime('%H:%M:%S', time.localtime(time.time()))
        self.sendTimes += 1
        self._file.write("Warm Restart Time= %s : %d\r\n" % (timeNow, self.sendTimes))
        self.connectTimes = 0

    def __del__(self):
        self._entity.close()
        self._read_thread.stop()
