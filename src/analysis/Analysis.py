# coding= utf-8

import os
from datetime import datetime
import time
import pandas as pd
from pip._vendor import chardet
from src.analysis.nmea import GNGGAFrame, GSV
from src.chart.draw import FmiChart
from src.report.word import WordReporter


# 获取文件编码类型
def get_encoding(file):
    # 二进制方式读取，获取字节数据，检测类型
    with open(file, 'rb') as f:
        return chardet.detect(f.read())['encoding']


class AnalysisTool:

    def __init__(self, dir=os.path.abspath('../..') + "/data"):
        self._dir = dir
        self.timeCheck = False
        self.fileList = list()
        self._dataFiles = list()
        self._ggaEntity = list()
        self._GSVEntity = list()

    # 获取当前文件夹下的所有log文件
    def read_file(self):
        for file in os.listdir(self._dir):
            if file.endswith('log'):
                self._dataFiles.append(file)
                self.fileList.append(file)

    def analysis(self, testPower=False):
        records = []
        for fileName in self.fileList:
            self._ggaEntity.clear()
            if ".log" not in fileName:
                continue
            portName = fileName
            dirPath = os.path.join(self._dir, fileName.split('.log')[0])
            if os.path.exists(dirPath) is False:
                os.mkdir(dirPath)

            """
                记录设备信息 固件版本 和开始时间
            """
            startTime, swVersion, testTimes, fixedUseTimeList = self.readConfig(fileName, testPower)

            self.localTime = datetime.now().date() if len(startTime) <= 0 \
                else datetime.strptime(startTime, "%Y%m%d_%H%M%S")

            """
                we put 20 names because it's Feyman-0183 Data, each line has different num with step ','
            """
            # print(self._dir + '/' + fileName)
            fileName = dirPath + '.log'
            self.fmiChar = FmiChart(path=dirPath)
            df = pd.read_table(fileName, sep=',',
                               encoding=get_encoding(fileName),
                               header=None,
                               names=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                      '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'],
                               error_bad_lines=False,
                               warn_bad_lines=False,
                               low_memory=False

                               )

            # self._GSV = df.loc[df['0'].str.contains('GSV')].copy()
            # gsv = GSV(dirPath, df.loc[df['0'].str.contains('GSV')].copy())
            # self._GSVEntity.append(gsv)

            # 删除异常数据
            df = df.drop(index=df.loc[(df['1'].isna())].index)
            df = df.drop(index=df.loc[(df['6'].isna())].index)
            df = df.drop(index=df.loc[(df['6'].astype(str) == '0')].index)

            gga = GNGGAFrame(dirPath,
                             df.loc[(df['0'].astype(str) == '$GNGGA') | (df['0'].astype(str) == '$GPGGA')].copy(),
                             self.localTime)
            self._ggaEntity.append(gga)
            maxNum = len(gga.get_altitude())
            fixNum = len(gga.get_altitude(True))

            self.drawPic(testPower)

            if testPower:
                records.append((portName.split('_')[0], swVersion, str(testTimes), str(len(fixedUseTimeList))))
                self.drawFixUseTime(dirPath, portName.split('_')[0], testTimes, fixedUseTimeList)
            else:
                records.append((portName.split('_')[0], swVersion, str(maxNum), str(round(fixNum * 100 / maxNum, 2))))

            self.drawLine()

        """ 生成word文档"""
        print(records)
        report = WordReporter(self._dir,
                              time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))
        report.setRecords(records, testPower)
        report.build()

    def analysisGSV(self):

        pass

    def readConfig(self, fileName, testPower=False):
        startTime = ''
        swVersion = ''
        testTimes = 0
        path = self._dir + '/' + fileName
        readLimit = 0
        fixed = False
        fixUseTimeList = []
        with open(file=path, errors='ignore') as rf:
            for line in rf.readlines():
                readLimit += 1

                if len(startTime) <= 0 & ("StartTime" in line):
                    startTime = line.split('=')[-1].replace('\n', '')
                    continue

                if len(swVersion) <= 0:
                    if 'Version' in line:
                        swVersion = line.split(':')[-1]

                if testPower is True:
                    if "+++ license activated" in line:
                        testTimes += 1
                    elif ("E,4" in line) & ("GNGGA" in line):
                        if not fixed:
                            fixUseTimeList.append(line.split(',')[1])
                        fixed = True
                    elif "GNGGA" in line:
                        fixed = False
                    continue
                if readLimit > 60:
                    break
        return startTime, swVersion, testTimes, fixUseTimeList

    def drawPic(self, testPower=False):

        for data in self._ggaEntity:
            xList, yList, xFixList, yFixList, fixList = data.get_scatter()
            if len(xFixList) != 0:
                self.fmiChar.drawScatter('ScatterFix', xFixList, yFixList, testPower=testPower)
            # if testPower:
            #     continue
            self.fmiChar.drawScatter('ScatterAll', xList, yList, fixList)

    def drawLine(self, gsv=None):
        self.fmiChar.drawLineChart(self._ggaEntity)
        self.fmiChar.drawCdf(self._ggaEntity, singlePoint=True)

        if gsv is not None:
            self.fmiChar.drawSateCn0(gsv.get_name(), gsv.get_satellites_status())

        # ''' draw only Fix'''
        self.fmiChar.drawCdf(self._ggaEntity, singlePoint=True, onlyFix=True)

    def drawFixUseTime(self, dirPath, name, fixedTimes, fixTimeUseList):
        self.fmiChar.drawFixUseTime(name=name, licenceNum=fixedTimes, timeStrList=fixTimeUseList)


if __name__ == '__main__':
    analysisTool = AnalysisTool()
    analysisTool.read_file()
    analysisTool.analysis(testPower=False)
    # dirPath = os.path.abspath('../..') + "/data"
    # fileName = dirPath + "/nmea0508.log"
    # df = pd.read_table(fileName, sep=',',
    #                    encoding=get_encoding(fileName),
    #                    header=None,
    #                    names=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
    #                           '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'],
    #                    error_bad_lines=False,
    #                    low_memory=False
    #                    )
    # data_GSV = df.loc[df['0'].str.contains('GSV')].copy()
    # gsv = GSV(fileName, df.loc[df['0'].str.contains('GSV')].copy())
    # fmiChar = FmiChart(path=dirPath)
    # # use-splitters
    # fmiChar.drawSateCn0('0508-gsv', gsv.get_satellites_status())
