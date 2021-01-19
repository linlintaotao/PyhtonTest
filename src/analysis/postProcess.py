# coding= utf-8
import os
import pandas as pd
from datetime import datetime
from pip._vendor import chardet
from src.chart.draw import FmiChart
from src.chart.draw import FmiChart
from src.analysis.nmea import GNGGAFrame
from src.report.PpWord import PPReporter
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

"""
analysis data file demo
TruthData-----------------
-----p20a
------data001-------------
------------P20202001.nmea
------data002-------------
------------P20202003.nmea

PostProcess---------------
-----p20a
------data001-------------
------------PP0202001.nmea
------------PP0202002.nmea
------data002-------------
------------PP0202003.nmea
------------PP0202004.nmea
"""


# 获取文件编码类型
def get_encoding(file):
    # 二进制方式读取，获取字节数据，检测类型
    print(file)
    with open(file, 'rb') as f:
        return chardet.detect(f.read())['encoding']


class DataPath:

    def __init__(self, isTruth, key, value):
        self.isTruth = isTruth
        self.key = key
        self.value = value

    def getKey(self):
        return self.key

    def getValue(self):
        return self.value


class NMEAFrame:

    def __init__(self, key, truthFrame):
        self.key = key
        self.truthFrame = truthFrame
        self.PPFrame = []

    def getKey(self):
        return self.key

    def getTruthFrame(self):
        return self.truthFrame

    def appendPPFrame(self, PPFrame):
        self.PPFrame.append(PPFrame)

    def getPPFrameList(self):
        return self.PPFrame


class PostProcess:

    def __init__(self, truthPath, ppPath, savePath):
        self.truthPath = truthPath
        self.ppPath = ppPath
        self.savePath = savePath
        self.postProcessDataList = list()
        self.truthDataList = list()
        self.localTime = datetime.now().date()
        self.nmeaFrameList = []

    @staticmethod
    def prepareNmeaData(path, isTruthData=False):
        nmeaDataList = []

        for dirName in os.listdir(path):
            path_join = os.path.join(path, dirName)
            if os.path.isdir(path_join):
                for name in os.listdir(path_join):
                    if os.path.isdir(os.path.join(path_join, name)):
                        key = name
                        value = []
                        for entity in os.listdir(os.path.join(path_join, name)):
                            if entity.endswith(('log', "txt", 'nmea')):
                                value.append(entity)
                        nmeaDataList.append(DataPath(isTruthData, dirName + os.sep + key, value))
        return nmeaDataList

    def startAnalysis(self):
        self.truthDataList = self.prepareNmeaData(self.truthPath, isTruthData=True)
        self.postProcessDataList = self.prepareNmeaData(self.ppPath, isTruthData=False)

        # 读取真值
        for truthData in self.truthDataList:
            filePath = os.path.join(self.truthPath, truthData.getKey(),
                                    truthData.getValue()[0])
            self.nmeaFrameList.append(NMEAFrame(truthData.getKey(), self.readNmeaFile(filePath)))

        # 读取后处理数据
        for ppData in self.postProcessDataList:
            key = ppData.getKey()
            PPvalueList = ppData.getValue()
            for dataFrame in self.nmeaFrameList:
                if key == dataFrame.getKey():
                    for ppName in PPvalueList:
                        ppPath = os.path.join(self.ppPath, key, ppName)
                        dataFrame.appendPPFrame(self.readNmeaFile(ppPath))
                    break

        # 画图分析结果
        for data in self.nmeaFrameList:
            fmiChart = FmiChart(path=os.path.join(self.ppPath, data.getKey()))
            if len(data.getPPFrameList()) > 0:
                fmiChart.drawCdf(data.getPPFrameList(), data.getTruthFrame())

        self.makeReport()

    def readNmeaFile(self, filePath):
        df = pd.read_table(filePath, sep=',',
                           encoding=get_encoding(filePath),
                           header=None,
                           names=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                  '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'],
                           error_bad_lines=False,
                           warn_bad_lines=False,
                           low_memory=False
                           )
        # 删除异常数据 1 时间 6 解状态
        df = df.drop(index=df.loc[(df['1'].isna())].index)
        df = df.drop(index=df.loc[(df['6'].isna())].index)
        df = df.drop(index=df.loc[(df['6'].astype(str) == '0')].index)

        name = filePath.split('/')[-1]
        gga = GNGGAFrame(name,
                         df.loc[(df['0'].astype(str) == '$GNGGA') | (df['0'].astype(str) == '$GPGGA')].copy(),
                         self.localTime)
        return gga

    def makeReport(self):
        reporter = PPReporter(self.ppPath, time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                              savePath=self.savePath)
        reporter.build()


if __name__ == '__main__':
    os.path.abspath('../../data/truth')
    pp = PostProcess(truthPath=os.path.abspath('../../data/truth'), ppPath=os.path.abspath('../../data/PP'),
                     savePath="")
    pp.startAnalysis()
