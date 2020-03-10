# coding= utf-8
# 测试入口

import os
from src.analysis.Analysis import AnalysisTool
import sys

if __name__ == '__main__':
    print(sys.path)

    for path in sys.path:
        sys.path.append(path)

    analysisTool = AnalysisTool(os.path.abspath('./data/'))
    analysisTool.read_file()
    analysisTool.analysis()
    print('Hello world')
    pass
