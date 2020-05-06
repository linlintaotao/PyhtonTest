# coding= utf-8
# 测试入口
import os
from src.streams.manger import Manager
from src.report.word import WordReporter
from src.analysis.Analysis import AnalysisTool
from threading import Timer

manager = None

def startAnalysis():
    if manager is not None:
        manager.stop()

    analysis = AnalysisTool()
    analysis.read_file()
    analysis.analysis()
    buildReport()
    print('Test is Finished success')


def buildReport():
    word = WordReporter()
    word.start()


if __name__ == '__main__':
    manager = Manager()
    manager.start()
    Timer(3600 * 12, startAnalysis).start()
