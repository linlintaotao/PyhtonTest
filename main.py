# 测试入口
from src.analysis.Analysis import AnalysisTool

if __name__ == '__main__':
    analysisTool = AnalysisTool()
    analysisTool.read_file()
    analysisTool.analysis()
    pass
