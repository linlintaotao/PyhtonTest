# coding= utf-8

import serial
from threading import Thread
import serial.tools.list_ports
import time

maxCount = 1e4


class SerialPort:
    def __init__(self, iport, fileWriter=None, baudRate=115200, showLog=False):
        self.zeroCount = 0
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
        self.supportListener = None
        self.checkedSupportFmi = True
        self.isRunning = True

    def setCallback(self, callback):
        self.callback = callback

    def setSupportFmi(self, supportListener):
        self.supportListener = supportListener

    def getSupportFmi(self):
        return self.checkedSupportFmi

    def getPort(self):
        return self._port

    def setFile(self, fileWriter, timeStr):
        self._file = fileWriter
        self._file.write('StartTime =' + timeStr + '\r\n')

    def is_running(self):
        return self._entity.isOpen() & self.isRunning

    def open_serial(self):
        try:
            self._entity = serial.Serial(self._port, self._baudRate, timeout=3)
            # if self._entity.isOpen():
            #     self._entity.close()
            # self._entity.open()
        except:
            raise IOError(f'can not open serial{self._port}:{self._baudRate}')

    def close_serial(self):
        self.isRunning = False
        if self._entity is not None:
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
        try:
            data = self._entity.readline()
        except Exception as e:
            print(e)
            self.isRunning = False
            return
        if self.checkedSupportFmi:
            if (b"\r\n" in data) or (b'$VERSION' in data):
                self.checkedSupportFmi = False
                self.supportListener(self._port)

        if len(data) <= 0:
            return None
        if self._showLog is True:
            # print(str(data))
            if self.callback is not None:
                self.autoTest(data)
        if self._file:
            # print("write data = %s" % str(data))
            self._file.write(data)
        # return data

    def notify(self, data):
        try:
            if self._entity.is_open & self.isRunning:
                self._entity.write(data)
        except Exception as e:
            print(e)
            pass

    def read_thread(self):
        while self._entity.is_open & self.isRunning:
            self.read_data()

    def start(self):
        if self._entity is None:
            self.open_serial()
        if self._read_thread is None:
            self._read_thread = None
        self._read_thread = Thread(target=self.read_thread)
        self._read_thread.start()

    def autoTest(self, data):
        strData = str(data)

        if '+++ license activated' in strData:
            self.connectTimes = 0
            self.fixCount = 5
            self.zeroCount = 0

        elif ('GNGGA' in strData) & ('E,0' in strData):
            self.zeroCount += 1
            if self.zeroCount > 200:
                self._file.write("zero >200 Restart")
                self.reset()

        elif 'E,4' in strData:
            # self.connectTimes += 1
            # if self.connectTimes > self.fixCount:
            self.reset()

    def reset(self):
        self.zeroCount = 0
        self.connectTimes = 0
        self.fixCount = maxCount
        self.callback()

    def warmStart(self):
        self.send_data('AT+WARM_RESET\r\n')
        timeNow = time.strftime('%H:%M:%S', time.localtime(time.time()))
        self.sendTimes += 1
        self._file.write("Warm Restart Time= %s : %d\r\n" % (timeNow, self.sendTimes))
        self.connectTimes = 0
