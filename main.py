# coding= utf-8
# 测试入口
import os
from src.analysis.Analysis import AnalysisTool

if __name__ == '__main__':
    analysisTool = AnalysisTool(os.path.abspath('./data/'))
    analysisTool.read_file()
    analysisTool.analysis()
    print('Hello world')
    pass
