# coding= utf-8
# 测试入口

import os
import sys

for path in sys.path:
    sys.path.append(path)

from src.analysis.Analysis import AnalysisTool

if __name__ == '__main__':
    print(sys.path)

    analysisTool = AnalysisTool(os.path.abspath('./data/'))
    analysisTool.read_file()
    analysisTool.analysis()
    print('Hello world')
    pass
