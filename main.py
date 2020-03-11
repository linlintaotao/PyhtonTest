# coding= utf-8
# 测试入口

import os
import sys
import sys

print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend([WORKING_DIR_AND_PYTHON_PATHS])
from src.analysis.Analysis import AnalysisTool

if __name__ == '__main__':
    analysisTool = AnalysisTool(os.path.abspath('./data/'))
    # analysisTool.read_file()
    # analysisTool.analysis()
    print('Hello world')
    pass
