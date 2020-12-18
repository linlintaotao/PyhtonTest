# coding= utf-8

import os
from datetime import datetime
import time
import pandas as pd
from pip._vendor import chardet
from src.analysis.nmea import GNGGAFrame, GSV
from src.chart.draw import FmiChart
from src.report.word import WordReporter

from pandas.plotting import register_matplotlib_converters
from src.analysis import gnss_distance

register_matplotlib_converters()


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
            if file.endswith(('log', "txt", 'nmea')):
                self._dataFiles.append(file)
                self.fileList.append(file)
        return self.fileList

    def analysis(self, testPower=False):
        records = []
        cepResultList = []
        for fileName in self.fileList:
            self._ggaEntity.clear()
            if not fileName.endswith(('log', "txt", 'nmea')):
                continue
            portName = fileName
            endtag = "." + fileName.split('.')[-1]
            dirPath = os.path.join(self._dir, fileName.split(endtag)[0])
            if os.path.exists(dirPath) is False:
                os.mkdir(dirPath)

            """
                记录设备信息 固件版本 和开始时间
            """
            startTime, swVersion, testTimes, fixedUseTimeList, naviRate, workMode, status, rtkDiff, GPIMU = self.readConfig(
                fileName, testPower)

            self.localTime = datetime.now().date() if len(startTime) <= 0 \
                else datetime.strptime(startTime, "%Y%m%d_%H%M%S")

            """
                we put 20 names because it's Feyman-0183 Data, each line has different num with step ','
            """
            # print(self._dir + '/' + fileName)
            fileName = dirPath + endtag
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
            if maxNum == 0:
                continue
            fixNum = len(gga.get_altitude(True))

            cepInfo = self.drawPic(testPower)

            cepResultList.append((portName.split('_')[0], cepInfo))
            if testPower:
                records.append((portName.split('_')[0], swVersion, str(testTimes), str(len(fixedUseTimeList))))
                self.drawFixUseTime(dirPath, portName.split('_')[0], testTimes, fixedUseTimeList)
            else:
                records.append((portName.split('_')[0], swVersion, str(maxNum), str(round(fixNum * 100 / maxNum, 2)),
                                naviRate, workMode, status, rtkDiff, GPIMU))

            self.drawLine()

        """ 生成word文档"""
        print(records)
        report = WordReporter(self._dir,
                              time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))
        report.setRecords(records, testPower)
        report.setCepResult(cepResultList)
        report.build()

    def analysisGSV(self):

        pass

    def readConfig(self, fileName, testPower=False):
        startTime = ''
        swVersion = ''
        testTimes = 0
        path = self._dir + '/' + fileName
        fixed = False
        navi_rate = ''
        fixUseTimeList = []
        work_mode = ''
        heartBeat = False
        rtkDiff = ''
        GPIMUTIMES = 0
        timeDelay = False
        with open(file=path, errors='ignore') as rf:
            for line in rf.readlines():
                if "GPIMU" in line:
                    GPIMUTIMES += 1

                if len(startTime) <= 0 and ("StartTime" in line):
                    startTime = line.split('=')[-1].replace('\n', '')
                    continue

                if len(swVersion) <= 0:
                    if 'Version' in line:
                        swVersion = line.split('Version:')[-1]

                if len(navi_rate) <= 0:
                    if 'Navi Rate' in line:
                        navi_rate = line.split(':')[-1]

                if len(work_mode) <= 0:
                    if 'Work Mode' in line:
                        work_mode = line.split(':')[-1]

                if 'HeartBeat' in line:
                    heartBeat = True

                if len(rtkDiff) <= 0:
                    if 'Rtk Diff' in line:
                        rtkDiff = line.split(':')[-1]

                if 'time match navi' in line:
                    timeDelay = True

                if testPower is True:
                    if "+++ license" in line:
                        testTimes += 1
                    elif ("E,4" in line) and ("GNGGA" in line):
                        if not fixed:
                            fixUseTimeList.append(line.split(',')[1])
                        fixed = True
                    elif "GNGGA" in line:
                        fixed = False
                    continue

        status = heartBeat and timeDelay
        return startTime, swVersion, testTimes, fixUseTimeList, navi_rate, work_mode, status, rtkDiff, GPIMUTIMES

    def drawPic(self, testPower=False):
        cepInfo = None
        for data in self._ggaEntity:
            xList, yList, xFixList, yFixList, fixList = data.get_scatter()
            if len(xFixList) != 0:
                self.fmiChar.drawScatter('ScatterFix', xFixList, yFixList, testPower=testPower)

            self.fmiChar.drawScatter('ScatterAll', xList, yList, fixList)
            self.fmiChar.drawSingleCdf(data, data.get_name(), pointTruth=None)
            cepInfo = self.fmiChar.drawSingleCdf(data, data.get_name(), pointTruth=None, onlyFix=True)
            print(cepInfo)
        return cepInfo

    def drawLine(self, gsv=None):
        self.fmiChar.drawLineChart(self._ggaEntity)
        # self.fmiChar.drawCdf(self._ggaEntity, singlePoint=True)
        # self.fmiChar.drawSingleCdf()
        if gsv is not None:
            self.fmiChar.drawSateCn0(gsv.get_name(), gsv.get_satellites_status())

        # ''' draw only Fix'''
        # self.fmiChar.drawCdf(self._ggaEntity, singlePoint=True, onlyFix=True)

    def drawFixUseTime(self, dirPath, name, fixedTimes, fixTimeUseList):
        self.fmiChar.drawFixUseTime(name=name, licenceNum=fixedTimes, timeStrList=fixTimeUseList)


if __name__ == '__main__':
    analysisTool = AnalysisTool()
    analysisTool.read_file()
    analysisTool.analysis(testPower=False)

    # latTrue = 30.45872751
    # lonTrue = 114.404825

    # 4003.9262877, N, 11613.7479358, E, 4, 12, 0.63, 44.586, M, -9.102
    # 4003.9298348,N,11613.7673410,E,4,12,0.65,44.854,M,-9.101
    # $GPGGA,103836.40,4003.9193890,N,11613.9090428,E,4,12,0.58,44.693,M,-9.093,M,0.4,0000*5A
    # $GPGGA, 103836.40, 4003.9193890, N, 11613.9090428, E, 4, 12, 0.58, 44.693, M, -9.093, M, 0.4, 0000 * 5
    # $GPGGA,105009.40,4003.9075392,N,11613.9133669,E,4,12,0.62,44.737,M,-9.093,M,0.4,0000*51
    if False:

        '''
        A.   13.258
        B.   7.934
        C.   12.579
        '''

        # latTrue = gnss_distance.formate(4003.9075392)
        # lonTrue = gnss_distance.formate(11613.9133669)

        # latTrue = gnss_distance.DmsToDdd('30°27′31.419036″')
        # lonTrue = gnss_distance.DmsToDdd('114°24′17.37″')
        # altitude = 13.258

        # latTrue = gnss_distance.DmsToDdd('30°27′28.7538″')
        # lonTrue = gnss_distance.DmsToDdd('114°24′17.191794″')
        # altitude = 7.934

        latTrue = gnss_distance.DmsToDdd('30°27′20.766114″')
        lonTrue = gnss_distance.DmsToDdd('114°24′08.382822″')
        altitude = 12.579

        pointTruth = [latTrue, lonTrue, altitude]

        dirPath = os.path.abspath('../..') + "/data"
        fileName = dirPath + "/postProcess.log"
        df = pd.read_table(fileName, sep=',',
                           encoding=get_encoding(fileName),
                           header=None,
                           names=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                  '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'],
                           error_bad_lines=False,
                           low_memory=False
                           )

        dirPath = fileName.split('.log')[0]
        if os.path.exists(dirPath) is False:
            os.mkdir(dirPath)

        fmiChar = FmiChart(path=dirPath)

        # 删除异常数据
        df = df.drop(index=df.loc[(df['1'].isna())].index)
        df = df.drop(index=df.loc[(df['6'].isna())].index)
        df = df.drop(index=df.loc[(df['6'].astype(str) == '0')].index)

        gga = GNGGAFrame(dirPath,
                         df.loc[(df['0'].astype(str) == '$GNGGA') | (df['0'].astype(str) == '$GPGGA')].copy(),
                         datetime.now().date())
        xList, yList, xFixList, yFixList, fixList = gga.get_scatter()
        if len(xFixList) != 0:
            fmiChar.drawScatter('ScatterFix', xFixList, yFixList, testPower=False, useTrue=True,
                                latTrue=latTrue, lon=lonTrue)
        fmiChar.drawScatter('ScatterAll', xList, yList, fixList, useTrue=True,
                            latTrue=latTrue, lon=lonTrue)

        fmiChar.drawCdf(dataFrameList=None, dataFrame=gga, pointTruth=pointTruth, singlePoint=True)
        fmiChar.drawCdf(dataFrameList=None, dataFrame=gga, pointTruth=pointTruth, singlePoint=True, onlyFix=True)
        ggaList = [gga]
        fmiChar.drawLineChart(ggaList)

    # gsv = GSV(fileName, df.loc[df['0'].str.contains('GSV')].copy())
    # data_GSV = df.loc[df['0'].str.contains('GSV')].copy()
    # # use-splitters
    # fmiChar.drawSateCn0('0508-gsv', gsv.get_satellites_status())
