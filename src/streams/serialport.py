# coding= utf-8

import serial
from threading import Thread
import serial.tools.list_ports


class SerialPort:
    def __init__(self, iport, fileWriter=None, baudRate=115200, showLog=False):
        self._port = iport
        self._baudRate = baudRate
        # self.open_serial()
        self._showLog = showLog
        self._read_thread = None
        self._entity = None
        self._file = fileWriter

    def setFile(self, fileWriter):
        self._file = fileWriter

    def is_running(self):
        return self._entity.isOpen()

    def open_serial(self):
        self._entity = serial.Serial(self._port, self._baudRate, timeout=3)
        if self._entity.isOpen():
            self._entity.close()
        try:
            self._entity.open()
        except:
            # raise IOError(f'can not open serial{self._port}:{self._baudRate}')
            pass

    def close_serial(self):
        self._entity.close()
        if self._file:
            self._file.close()

    def send_data(self, data):
        # print("send data = %s" % str(data))
        self._entity.write(data)

    def read_data(self):
        data = self._entity.readline()
        if len(data) <= 0:
            return None
        if self._showLog is True:
            # print("show log = %s" % data)
            print(data)
            pass
        if self._file:
            self._file.write(data)
        return data

    def notify(self, data):
        try:
            if self._entity.is_open:
                self._entity.write(data)
        except Exception as e:
            # print(e)
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
