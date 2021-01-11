import serial
from src.streams.serialport import SerialPort
import time
from src.streams.filereader import FileWriter
import os
from threading import Timer

COM1 = "/dev/cu.usbserial-14230"
COM2 = "/dev/cu.usbserial-14210"
serialPortPower = None
serialPortP20 = None

list = ["AT+NAVI_RATE=5\r\n",
        "AT+IMU_ANGLE=180,0,0\r\n",
        "AT+LEVEL_ARM=0.3,-1,2.2\r\n",
        "AT+GPGGA=UART1,5\r\n",
        "AT+GPRMC=UART1,5\r\n",
        "AT+WORK_MODE=13\r\n",
        "AT+DR_TIME=0\r\n",
        "AT+ALIGN_VEL=3\r\n",
        "AT+RTK_DIFF=5\r\n",
        "AT+SAVE_ALL\r\n",
        "AT+WARM_RESET\r\n"]


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
    serialPortPower = serial.Serial(COM1, 9600)
    serialPortP20 = SerialPort(COM2, 115200, showLog=True)
    file = FileWriter(
        serialPortP20.getPort().split('/')[-1] + time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())) + ".log",
        os.path.abspath('..') + "/data/")
    serialPortP20.setFile(file, time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))
    serialPortP20.setCallback(power)
    serialPortP20.start()
    power('')
    scheduler = Timer(60 * 60 * 18, stop)
    scheduler.start()
    scheduler.join()
    stop()
