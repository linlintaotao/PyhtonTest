# coding= utf-8

import serial
from threading import Thread
import serial.tools.list_ports
import time


class SerialPort:
    def __init__(self, iport, fileWriter=None, baudRate=115200, showLog=False):
        self.zeroCount = 0
        self._port = iport
        self._baudRate = baudRate
        self._showLog = showLog
        self._read_thread = None
        self._entity = None
        self._file = fileWriter
        self.callback = None
        self.supportListener = None
        self.checkedSupportFmi = True
        self.isRunning = True
        self.cycleTime = time.time()
        self.state = 0
        self.coldRsetLimit = 100
        self.warmResetInterval = 0
        self.resetTest = None

    def setCallback(self, callback):
        self.callback = callback

    def logStateTime(self, resetTest, warmResetInterval=0):
        self.resetTest = resetTest
        self.warmResetInterval = warmResetInterval

    def setSupportFmi(self, supportListener):
        self.supportListener = supportListener

    def getSupportFmi(self):
        return self.checkedSupportFmi

    def getPort(self):
        return self._port

    def setFile(self, fileWriter, timeStr):
        self._file = fileWriter
        self._file.write('StartTime =' + timeStr + '\r\n')

    def writeSerialData(self, value):
        if self._file is not None:
            self._file.write(value)

    def is_running(self):
        return self._entity.isOpen() & self.isRunning

    def open_serial(self):
        try:
            self._entity = serial.Serial(self._port, self._baudRate, timeout=3)
        except Exception:
            raise IOError(f'can not open serial{self._port}:{self._baudRate}')

    def close_serial(self):
        self.isRunning = False
        if self._entity is not None:
            self._entity.close()
        if self._file:
            self._file.close()

    def send_data(self, data):
        if self._entity.is_open:
            if type(data) is str:
                data = data.encode()
            try:
                self._entity.write(data)
                self._entity.flush()
            except Exception:
                return
            print("send data", data)

    def read_data(self):
        try:
            data = self._entity.readline()
        except Exception as e:
            print('read_data', e)
            self.isRunning = False
            return
        if self.checkedSupportFmi:
            if (b"\r\n" in data) or (b'$VERSION' in data):
                self.checkedSupportFmi = False
                if self.supportListener is not None:
                    self.supportListener(self._port)

        if len(data) <= 0:
            return None
        # if self._showLog is True:
        #     if self.callback is not None:
        #         self.autoTest(data)
        if self.resetTest:
            # print(data)
            self.autoTest(data)
        if self._file:
            self._file.write(data)

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
        self._read_thread = Thread(target=self.read_thread, daemon=True)
        self._read_thread.start()

    def autoTest(self, data):
        strData = str(data)
        if time.time() - self.cycleTime > 300:
            self.warmStart()
        if '$GNGGA' in strData:
            if 'E,1' in strData and self.state != 1:
                if self.coldRsetLimit <= 0:
                    self.coldRsetLimit = 80
                self.state = 1
                self.writeLog(1)
            elif 'E,5' in strData and self.state != 5:
                self.state = 5
                self.writeLog(5)
            elif 'E,4' in strData and self.state != 4 and self.state != 0:
                self.state = 4
                self.writeLog(4)
                self.warmStart()
            elif 'E,4' in strData and self.state == 0:
                if time.time() - self.cycleTime > 3:
                    self.warmStart()
        elif 'cors up' in strData:
            self._file.write('TIME,cors_up,%d,%d\r\n' % (self.cycleTime, time.time() - self.cycleTime))
        elif 'open error filePath' in strData:
            self.coldReset()
            
    def reset(self):
        self.callback(self._port)

    def warmStart(self):
        self.coldRsetLimit -= 1
        # cold reset after warm reset 80 times
        if self.coldRsetLimit <= 0:
            self.coldReset()
            return
        self.send_data('AT+WARM_RESET\r\n')
        self.cycleTime = time.time()
        self.state = 0
        self._file.write("TIME,warm reset:%d,%s\r\n" % (
            self.cycleTime, time.strftime('%d %H%M%S', time.localtime(time.time())),))

    def coldReset(self):
        self.state = 0
        self.send_data('AT+COLD_RESET\r\n')
        self._file.write("TIME,cold reset:%d,%s\r\n" % (
            time.time(), time.strftime('%d %H%M%S', time.localtime(time.time()))))

    def writeLog(self, state):
        self._file.write("TIME,status:%d,%d,%d\r\n" % (state, self.cycleTime, time.time() - self.cycleTime))
