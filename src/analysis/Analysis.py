# coding= utf-8

import os
from datetime import datetime, timedelta
import pandas as pd
from pip._vendor import chardet
from src.analysis.nmea import GNGGAFrame, GSV
from src.chart.draw import FmiChart


class AnalysisTool:

    def __init__(self, dir=os.path.abspath('..') + "/data"):
        self._dir = dir
        self.localTime = datetime.now().date()
        self.timeCheck = False
        self.fileList = list()
        self._dataFiles = list()
        self._ggaEntity = list()
        self._GSVEntity = list()

    # 获取当前文件夹下的所有log文件
    def read_file(self, tag='log'):
        for file in os.listdir(self._dir):
            if file.endswith(tag):
                self._dataFiles.append(file)
                self.fileList.append(file)

    # 获取文件编码类型
    def get_encoding(self, file):
        # 二进制方式读取，获取字节数据，检测类型
        with open(file, 'rb') as f:
            return chardet.detect(f.read())['encoding']

    def analysis(self):
        for fileName in self.fileList:
            dirPath = os.path.join(self._dir, fileName.split('.log')[0])
            if os.path.exists(dirPath) is False:
                os.mkdir(dirPath)
            """
                记录设备信息 boot版本 固件版本 和开始时间
            """
            configText = self.readConfig(fileName)

            """
                we put 20 names because it's Feyman-0183 Data, each line has different num with step ','
            """
            print(self._dir + '/' + fileName)
            fileName = dirPath + '.log'
            df = pd.read_table(fileName, sep=',',
                               encoding=self.get_encoding(fileName),
                               header=None,
                               names=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                      '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'],
                               error_bad_lines=False,
                               low_memory=False
                               )
            # 删除异常数据
            df = df.drop(index=df.loc[(df['1'].isna())].index)
            # self._GSV = df.loc[df['0'].str.contains('GSV')].copy()
            # gsv = GSV(dirPath, df.loc[df['0'].str.contains('GSV')].copy())
            gga = GNGGAFrame(dirPath,
                             df.loc[(df['0'].astype(str) == '$GNGGA') | (df['0'].astype(str) == '$GPGGA')].copy(),
                             self.localTime)
            self._ggaEntity.append(gga)
            # self._GSVEntity.append(gsv)
        self.drawPic("dirPath")
        """ 生成word文档"""

    def analysisGSV(self):

        pass

    def readConfig(self, fileName):
        writeLog = ''
        path = self._dir + '/' + fileName
        readLimit = 0
        with open(file=path) as rf:
            for line in rf.readlines():
                readLimit += 1
                if ("StartTime" in line) | ('' in line) | ('' in line) | ('' in line) | ('' in line):
                    writeLog += line
                if readLimit > 30:
                    break
        rf.close()
        return writeLog

    def drawPic(self, dirPath):

        fmiChar = FmiChart(path=dirPath)
        fmiChar.drawLineChart(self._ggaEntity)
        fmiChar.drawCdf(self._ggaEntity, singlePoint=True)
        # for gsv in self._GSVEntity:
        #     fmiChar.drawSateCn0(gsv.get_name(), gsv.get_satellites_status())
        for data in self._ggaEntity:
            xList, yList, xFixList, yFixList, fixList = data.get_scatter()
            fmiChar.drawScatter('ScatterFix', xFixList, yFixList)
            fmiChar.drawScatter('ScatterAll', xList, yList, fixList)
            print(len(xFixList))
            print(len(xList))
        # ''' draw only Fix'''
        fmiChar.drawCdf(self._ggaEntity, singlePoint=True, onlyFix=True)


if __name__ == '__main__':
    analysisTool = AnalysisTool()
    analysisTool.read_file()
    analysisTool.analysis()
