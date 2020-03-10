# coding= utf-8
# 测试入口

import os
import sys

# for path in sys.path:
#     sys.path.append(path)

sys.path.append("\\Users\\lintao\\PycharmProjects//PyhtonTest")
sys.path.append("\\usr\\local\\Cellar\\python\\3.7.5\\Frameworks\\Python.framework\\Versions\\3.7\\lib\\python37.zip")
sys.path.append("\\usr\\local\\Cellar\\python\\3.7.5\\Frameworks\\Python.framework\\Versions\\3.7\\lib\\python3.7")
sys.path.append("\\usr\\local\\Cellar\\python\\3.7.5\\Frameworks\\Python.framework\\Versions\\3.7\\lib\\python3.7\\lib-dynload")
sys.path.append("\\Users\\lintao\\Library\\Python\\3.7\\lib\\python\\site-packages")
sys.path.append("\\usr\\local\\lib\\python3.7\\site-packages")
from src.analysis.Analysis import AnalysisTool

if __name__ == '__main__':
    print(sys.path)
    #
    # analysisTool = AnalysisTool(os.path.abspath('.\\data\\'))
    # analysisTool.read_file()
    # analysisTool.analysis()
    print('Hello world')
    pass
