# -*- coding: utf-8 -*-

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
from src.utils.visualize_fix_time import analysisLogFile

register_matplotlib_converters()


# 获取文件编码类型
def get_encoding(file):
    # 二进制方式读取，获取字节数据，检测类型
    with open(file, 'rb') as f:
        data = f.read()[0:1024]
        return chardet.detect(data)['encoding']


class AnalysisTool:

    def __init__(self, dir=os.path.abspath('../..') + "/data"):
        self._dir = dir
        self.timeCheck = False
        self.fileList = list()
        self._dataFiles = list()
        self._ggaEntity = list()
        self._GSVEntity = list()
        self._tmpPath = self._dir + "/tmp"
        self.resetTesFile = list()

    # 获取当前文件夹下的所有log文件
    def read_file(self):
        for file in os.listdir(self._dir):
            if file.endswith(('log', "txt", 'nmea')):
                print("==>" + file)
                self._dataFiles.append(file)
                self.fileList.append(file)
                if file.__contains__("RESET_TEST"):

                    self.resetTesFile.append(self._dir + "/" + file)
        self.fileList.sort()
        return self.fileList

    def analysis(self, testPower=False):
        records = []
        cepResultList = []
        for fileName in self.fileList:
            self._ggaEntity.clear()
            try:
                # if True:
                if not fileName.endswith(('log', "txt", 'nmea', 'gga')):
                    continue
                portName = fileName
                endtag = "." + fileName.split('.')[-1]
                dirPath = os.path.join(self._dir, fileName.split(endtag)[0])
                if os.path.exists(dirPath) is False:
                    os.mkdir(dirPath)
                if os.path.exists(self._tmpPath) is False:
                    os.mkdir(self._tmpPath)
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
                fileName = self._tmpPath + "/" + fileName
                self.fmiChar = FmiChart(path=dirPath)
                df = pd.read_table(fileName, sep=',',
                                   # encoding=get_encoding(fileName),
                                   encoding='unicode_escape',
                                   header=None,
                                   names=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                          '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'],
                                   error_bad_lines=False,
                                   warn_bad_lines=False,
                                   low_memory=False
                                   )

                # 删除异常数据
                df = df.drop(index=df.loc[(df['1'].isna())].index)
                df = df.drop(index=df.loc[(df['2'].isna())].index)
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
                    records.append(
                        (portName.split('_')[0], swVersion, str(maxNum), f'%.2f' % (int(10000 * fixNum / maxNum) / 100),
                         naviRate, workMode, status, rtkDiff, GPIMU))

                self.drawLine()
            except Exception as e:
                print(e)
                pass

        self.parseResetLogFile()

        """ 生成word文档"""
        print(records)
        report = WordReporter(self._dir, time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))
        report.setRecords(records, testPower)
        report.setCepResult(cepResultList)
        report.build()

    def parseResetLogFile(self):
        if len(self.resetTesFile) <= 0:
            return None
        try:
            for fileName in self.resetTesFile:
                endtag = "." + fileName.split('.')[-1]
                dirPath = os.path.join(self._dir, fileName.split(endtag)[0])
                analysisLogFile(fileName, dirPath)
        except Exception as e:
            print(e)

    def analysisGSV(self):

        pass

    def readConfig(self, fileName, testPower=False):
        startTime = ''
        swVersion = ''
        testTimes = 0
        path = self._dir + '/' + fileName
        tmp = self._tmpPath + '/' + fileName
        fixed = False
        navi_rate = ''
        fixUseTimeList = []
        work_mode = ''
        heartBeat = False
        rtkDiff = ''
        GPIMUTIMES = 0
        timeDelay = False
        with open(file=path, errors='ignore') as rf:
            readLines = rf.readlines()
        with open(tmp, 'w', errors='ignore') as fw:
            for line in readLines:
                if "GPIMU" in line:
                    GPIMUTIMES += 1
                if len(startTime) <= 0 and ("StartTime" in line):
                    startTime = line.split('=')[-1].replace('\n', '')
                    continue
                if len(swVersion) <= 0:
                    if 'Version' in line:
                        swVersion = line.split('Version:')[-1]
                        swVersion = swVersion.strip('\r\n')
                if len(navi_rate) <= 0:
                    if 'Navi Rate' in line:
                        navi_rate = line.split(':')[-1]
                if len(work_mode) <= 0:
                    if 'Work Mode' in line:
                        work_mode = line.split(':')[-1]
                if 'HeartBeat' in line or 'BROM' in line:
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
                if 'GGA' in line:
                    fw.write(line)
        status = heartBeat and timeDelay
        return startTime, swVersion, testTimes, fixUseTimeList, navi_rate, work_mode, status, rtkDiff, GPIMUTIMES

    def drawPic(self, testPower=False):
        useTruth = False
        # pointTruth = [40.06419307, 116.22812422, 54.593] if useTruth else None
        # pointTruth = [40.06410843, 116.22816529, 53.916] if useTruth else None
        pointTruth = [40.0641088, 116.2281659, 53.916] if useTruth else None
        cepInfo = None
        for data in self._ggaEntity:
            xList, yList, xFixList, yFixList, fixList = data.get_scatter()
            if len(xFixList) != 0:
                self.fmiChar.drawScatter('ScatterFix', xFixList, yFixList, useTrue=useTruth, testPower=testPower)

            self.fmiChar.drawScatter('ScatterAll', xList, yList, fixList, useTrue=useTruth)
            self.fmiChar.drawSingleCdf(data, data.get_name(), pointTruth=pointTruth)
            cepInfo = self.fmiChar.drawSingleCdf(data, data.get_name(), pointTruth=pointTruth,
                                                 onlyFix=True)
            print(cepInfo)
        return cepInfo

    def drawLine(self, gsv=None):
        self.fmiChar.drawLineChart(self._ggaEntity)
        if gsv is not None:
            self.fmiChar.drawSateCn0(gsv.get_name(), gsv.get_satellites_status())

    def drawFixUseTime(self, dirPath, name, fixedTimes, fixTimeUseList):
        self.fmiChar.drawFixUseTime(name=name, licenceNum=fixedTimes, timeStrList=fixTimeUseList)


if __name__ == '__main__':
    analysisTool = AnalysisTool(dir=os.path.abspath('../..') + "/data")
    analysisTool.read_file()
    analysisTool.analysis(testPower=False)
