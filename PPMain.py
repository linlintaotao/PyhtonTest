import os
import sys
from src.analysis.postProcess import PostProcess


def start(argv):
    if len(argv) <= 1:
        return
    pp = PostProcess(truthPath=os.path.join(argv[1], 'Truth'), ppPath=os.path.join(argv[1], 'PP'))
    pp.startAnalysis()


if __name__ == '__main__':
    start(sys.argv)
    print(sys.argv)
    print("hello python")
