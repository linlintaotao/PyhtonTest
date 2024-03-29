# coding= utf-8

import datetime
import socket
from base64 import b64encode
from queue import Queue
from threading import Thread
from time import sleep
from src.observer.publish import Publisher
from src.streams.filereader import FileWriter
import os


class NtripClient(Publisher):
    # 40.06410906, 116.2281654, 54

    def __init__(self, ip='ntrips.feymani.cn', port=2102, user='feyman-user', password="123456", mountPoint='',
                 latitude=40.06410906, longitude=116.2281654, altitude=54.6):
        Publisher.__init__(self)
        '''
        parameters
        '''
        self._ip = ip
        self._port = port
        self._user = user
        self._password = password
        self._mountPoint = mountPoint
        self.setPosition(latitude, longitude)
        self._height = altitude
        self.read_thread = None
        self.check_thread = None
        self._reconnectLimit = 0
        '''
        state
        '''
        self._isRunning = False
        self._reconnect = False
        self._stopByUser = False
        '''
        data
        '''
        self._data = Queue()
        self._socket = None
        self.dir = None
        self.fileLog = None

    def setPosition(self, lat, lon):
        self.flagN = "N"
        self.flagE = "E"
        if lon > 180:
            lon = (lon - 360) * -1
            self.flagE = "W"
        elif 0 > lon >= -180:
            lon = lon * -1
            self.flagE = "W"
        elif lon < -180:
            lon = lon + 360
            self.flagE = "E"
        else:
            self.lon = lon
        if lat < 0:
            lat = lat * -1
            self.flagN = "S"
        self.lonDeg = int(lon)
        self.latDeg = int(lat)
        self.lonMin = (lon - self.lonDeg) * 60
        self.latMin = (lat - self.latDeg) * 60

    def setDir(self, dir):
        self.dir = dir

    def getInfo(self):
        return f'Ntrip=%s:%s\r\n' % (self._ip, self._mountPoint)

    def set_mount_info(self, mnt):
        user = b64encode((self._user + ":" + str(self._password)).encode('utf-8')).decode()
        mountPointString = "GET /%s HTTP/1.1\r\n" \
                           "User-Agent: %s\r\n" \
                           "Authorization: Basic %s\r\n" % (
                               mnt, "NTRIP FMIPythonClient/1.0", user)
        mountPointString += "\r\n"
        # print(mountPointString)
        _mount_info = mountPointString.encode('utf-8')
        return _mount_info

    def getGGAString(self):
        now = datetime.datetime.utcnow()
        ggaString = "GPGGA,%02d%02d%04.2f,%02d%011.8f,%1s,%03d%011.8f,%1s,1,05,0.19,0,M,%5.3f,M,," % \
                    (now.hour, now.minute, now.second, self.latDeg, self.latMin, self.flagN, self.lonDeg, self.lonMin,
                     self.flagE, self._height)
        checksum = self.check_sum(ggaString)
        ggaStr = "$%s*%s\r\n" % (ggaString, checksum)
        # print('sendGGAString', ggaStr)
        return ggaStr.encode()

    def check_sum(self, stringToCheck):
        xsum_calc = 0
        for char in stringToCheck:
            xsum_calc = xsum_calc ^ ord(char)
        return "%02X" % xsum_calc

    def start(self, startCheck=True):
        if startCheck is True:
            self.start_check()
        if self._isRunning is True:
            return
        self._reconnect = False

        if self.fileLog is None:
            self.fileLog = FileWriter(f'Cors_%s.dat' % self._mountPoint, self.dir)

        try:
            if self._socket is not None:
                self._socket.close()

            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self._ip, self._port))
            self._isRunning = True
            if self.read_thread is not None:
                self.read_thread = None
            self.read_thread = Thread(target=self.receive_data, daemon=True)
            self.read_thread.start()
            self._socket.send(self.set_mount_info(self._mountPoint))
            self._socket.send(self.getGGAString())

        except Exception as e:
            self._isRunning = False
            print("start exp", e)

    def stop(self):
        self._isRunning = False
        self._stopByUser = True
        self.unregisterAll()
        if self._socket is not None:
            self._socket.close()

    def receive_data(self):

        while self._isRunning:
            try:
                data = self._socket.recv(1024)
                if len(data) <= 0:
                    self._reconnectLimit += 1
                else:
                    self._reconnectLimit = 0
                    # 通知所有的串口进行刷新
                    self.notifyAll(data)
                    if self.fileLog is not None:
                        self.fileLog.write(data)
                # print(data)
                sleep(0.3)
            except Exception as e:
                self._reconnect = True
                self._reconnectLimit += 5
                print('receive_data =', e)
                break

    def reconnect(self):
        self._isRunning = False
        self._reconnectLimit = 0
        self._socket.close()
        sleep(3)
        self.start(startCheck=False)

    def check(self):
        while self._stopByUser is False:
            self._reconnectLimit += 1
            if (self._reconnectLimit > 5) | self._reconnect is True:
                self.reconnect()
            try:
                if self._isRunning:
                    self._socket.send(self.getGGAString())
            except Exception as e:
                print('check', e)
            sleep(10)

    def start_check(self):
        if self.check_thread is not None:
            self.check_thread = None
        self.check_thread = Thread(target=self.check, daemon=True)
        self.check_thread.start()


if __name__ == '__main__':
    ntrip = NtripClient(ip='lab.ntrip.qxwz.com', port=8002, user="stmicro0010", password='50fcc29', mountPoint='', )
    ntrip.start()
