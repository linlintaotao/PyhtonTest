# coding= utf-8
# 测试入口
import os
import time
import sys

from src.streams.manger import Manager
from src.analysis.Analysis import AnalysisTool
from threading import Timer

from src.zipmanager import make_zip

manager = None
powerTest = False
timeStr = ""


def startAnalysis():
    analysis = AnalysisTool(dir=os.path.join(os.path.abspath('.'), "data"))
    analysis.read_file()
    analysis.analysis(testPower=powerTest)
    buildReport()
    print('Test is Finished success')


def buildReport():
    # 获取路径
    report_dir = os.path.abspath('.') + "/data/"
    # 调用打包方法
    make_zip(report_dir, os.path.join(os.path.abspath('.'), timeStr + "_dailyReport.zip"))


def close_useless_port():
    if manager is not None:
        manager.close_unSupport()


def stop():
    if manager is not None:
        manager.stop()


def test(argv):
    if len(argv) <= 1:
        return
    useHour= int(argv[1])
    global timeStr, manager
    try:
        timeStr = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
        dirPath = os.path.join(os.path.abspath('.'), "data")
        if os.path.exists(dirPath) is False:
            os.mkdir(dirPath)

        manager = Manager.instance(dir=dirPath)

        manager.start(powerTest=powerTest)
        stop_useless_port = Timer(30, close_useless_port)
        stop_useless_port.start()

        scheduler = Timer(60 * 60 * useHour, stop)
        scheduler.start()
        scheduler.join()
    except Exception as e:
        print(e)
        stop()
    startAnalysis()


if __name__ == '__main__':


    test(sys.argv)
