# coding= utf-8
# 测试入口

import os
import sys
from src.analysis.Analysis import AnalysisTool
from src.streams.manger import Manager


def startTest():
    manager = Manager()
    manager.start()


if __name__ == '__main__':
    startTest()

    # analysisTool = AnalysisTool(os.path.abspath('./data/'))
    # analysisTool.read_file()
    # analysisTool.analysis()
    print('Test is Finished')
    pass
