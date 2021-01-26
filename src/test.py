import serial
from src.streams.serialport import SerialPort
import time
from src.streams.filereader import FileWriter
import os
from threading import Timer
from src.streams.Ntrip import NtripClient

COM1 = "/dev/cu.usbserial-14230"
COMP20 = "/dev/cu.usbserial-00001014"
serialPortPower = None
serialPortP20 = None


def power(port):
    serialPortPower.write(bytes.fromhex("A0 01 01 A2"))
    # close
    time.sleep(5)
    serialPortPower.write(bytes.fromhex("A0 01 00 A1"))


def support():
    for data in list:
        serialPortP20.send_data(data)
        time.sleep(0.1)


def stop():
    serialPortPower.close()
    serialPortP20.close_serial()


if __name__ == '__main__':
    # serialPortPower = serial.Serial(COM1, 9600)
    ntrip = NtripClient(ip='ntrip.mliyadong.com', port=2101, mountPoint='BJMSM4_PolaRx5', user='mosaictest01',
                        password='beijing001')
    serialPortP20 = SerialPort(COMP20, 115200, showLog=True)
    file = FileWriter(
        serialPortP20.getPort().split('/')[-1] + time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())) + ".log",
        os.path.abspath('..') + "/data/")
    serialPortP20.setFile(file, time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))
    # warmResetInterval can delay the action to send AT_WARM_RESET  even gps state is fixed
    serialPortP20.logStateTime(True, warmResetInterval=0)
    serialPortP20.start()
    ntrip.start()
    ntrip.register(serialPortP20)
    try:
        scheduler = Timer(60 * 60 * 28, stop)
        scheduler.start()
        scheduler.join()
    except Exception:
        serialPortP20.close_serial()
        ntrip.stop()
    stop()
