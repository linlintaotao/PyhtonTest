# coding= utf-8
# 绘图工具
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pacthes
from datetime import datetime
from src.analysis import Gauss
import math
import pandas as pd

accuracyItems = [0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 100, 1000]
WATERMARK = "By FMI Tech"
radius = 6371000
D2R = 0.017453292519943295

TITLES = [r' north differential errors in $meters$',
          r' east differential errors in $meters$',
          r' up differential errors in $meters$',
          r' horizontal differential errors in $meters$']


class FmiChart:

    def __init__(self, path='', name=''):
        self._name = name
        self._savePath = path
        self._fixColor = ['black', 'black', 'red', 'gray', 'green', 'blue', 'yellow']
        self._resultInfo = ""

    ''' 获取绘图的最小精度 0.01~ 1000 (m)'''

    def get_accuracy(self, axis):
        accuracyItem = round(axis / 10, 2)
        for i in range(len(accuracyItems)):
            if accuracyItem < accuracyItems[i]:
                accuracyItem = accuracyItems[i]
                return accuracyItem
        return accuracyItems[-1]

    def getResultInfo(self):
        return self._resultInfo

    ''' 画测试结果的结果点位图 
        name : 测试的数据来源
        xpos : x轴坐标
        ypos : y轴坐标
        fixList  : fixList
    '''

    def drawScatter(self, name, xPos, yPos, fixList=None, useTrue=False, testPower=False):
        if len(xPos) <= 0:
            return
        xMax, xMin, yMax, yMin = max(xPos), min(xPos), max(yPos), min(yPos)

        if useTrue:
            xCenter, yCenter = Gauss.LatLon2XY(40.09500333, 116.21050922)
        else:
            xCenter, yCenter = np.mean(xPos), np.mean(yPos)

        axis = max([abs(xMax - xCenter),
                    abs(xMin - xCenter),
                    abs(yMax - yCenter),
                    abs(yMin - yCenter)]) * 1.1

        fig, ax = plt.subplots(figsize=[10, 8])

        ''' 根据解状态匹配对应的颜色 '''

        if fixList is None:
            color = 'green'
            textInfo = 'Scatter FIXED'
        else:
            color = list(map(lambda c: self._fixColor[c.astype(int)], fixList))
            textInfo = 'Scatter All'

        accuracyItem = self.get_accuracy(axis)

        '''画提示网格和圆'''
        for i in range(7):
            mid = round(accuracyItem * i, 2)
            circle = pacthes.Circle((0, 0), mid, fill=False, ls='--', color='lightgray', gid=str(mid))
            if i != 0:
                ax.annotate(str(mid), xy=(accuracyItem * (i - 1), 0), xytext=(mid, 0), ha='right', color='blue')
            ax.add_patch(circle)
        fig.text(0.75, 0.25, WATERMARK, fontsize=35, color='gray', ha='right', va='bottom', alpha=0.2, rotation=30)

        '''画点'''
        ax.scatter(list(map(lambda x: xCenter - x, xPos)), list(map(lambda y: y - yCenter, yPos)), marker='1', c=color)

        ax.set_xlim(-axis, axis)
        ax.set_ylim(-axis, axis)
        plt.xlabel(r'points x (m)')
        plt.ylabel(r'points y (m)')
        plt.title(textInfo)
        plt.axis('equal')
        plt.grid(True, ls=':', c='lightgray')
        plt.savefig(self._savePath + '/' + name + '.png')
        plt.close(fig)

    def drawLineChart(self, dataframe):
        fig, ax = plt.subplots(figsize=[12, 8])

        ax3 = plt.subplot(313)
        for data in dataframe:
            data.getdAge().plot(label=data.get_name())
        ax3.set_ylabel('dAge', fontsize=10)
        ax3.set_xlabel('local time', fontsize=10)

        ax2 = plt.subplot(312)
        for data in dataframe:
            data.get_sateNum().plot(label=data.get_name())
        ax2.set_ylabel('SateNum', fontsize=10)

        ax1 = plt.subplot(311, sharex=ax2)
        for data in dataframe:
            data.get_state().plot(label=data.get_name(), fontsize=9)
        ax1.set_ylabel('FixState', fontsize=10)
        ax1.set_ylim(0, 7)

        fig.text(0.75, 0.25, WATERMARK, fontsize=35, color='gray', ha='right', va='bottom', alpha=0.2, rotation=30)

        plt.title(r'FixState & sateNums & dAge')
        plt.grid(True, ls=':', c='lightgray')
        plt.savefig(self._savePath + '/bsateNumAndFixSate.png')
        plt.close(fig)

    # pointTruth [latitude,longitude,altitude]
    # dataTruth
    def drawCdf(self, dataFrameList, dataTruth=None, singlePoint=False, pointTruth=None, onlyFix=False):

        cdfInfoList = []

        if singlePoint:
            for dataFram in dataFrameList:
                self.drawSingleCdf(dataFram, dataFram.get_name(), pointTruth=pointTruth, onlyFix=onlyFix)
        else:

            fig, ax = plt.subplots(4, 1, sharex=True, figsize=(12, 8))
            for dataFram in dataFrameList:
                dtN = pd.merge(dataTruth.get_latitude(), dataFram.get_latitude(), left_index=True, right_index=True,
                               how='outer')
                dtN = dtN.dropna()
                dtNorthDiff = (dtN['2_y'] - dtN['2_x']) * D2R * radius
                ax[0].plot(dtNorthDiff.index, dtNorthDiff.values, lw=1, label=dataFram.get_name())
                ax[0].legend(fontsize='small', ncol=1)
                dtE = pd.merge(dataTruth.get_longitude(), dataFram.get_longitude(), left_index=True, right_index=True,
                               how='outer')
                dtE = dtE.dropna()
                dtEarthDiff = (dtE['4_y'] - dtE['4_x']) * D2R * radius * np.cos(dtE['4_x'] * D2R)
                ax[1].plot(dtEarthDiff, lw=1, label=dataFram.get_name())

                dtU = pd.merge(dataTruth.get_altitude(), dataFram.get_altitude(), left_index=True, right_index=True,
                               how='outer')
                dtU = dtU.dropna()
                dtU = dtU['9_y'] - dtU['9_x']
                ax[2].plot(dtU, lw=1)
                hzDiff = np.sqrt(dtNorthDiff[:] ** 2 + dtEarthDiff[:] ** 2)
                ax[3].plot(hzDiff, lw=1)
                fixPercent = pd.Series([dataFram.getFixPercent()], index=['FixPercent'])
                cdfInfo = hzDiff.describe(percentiles=[.68, .95, .997]).append(fixPercent)
                print(type(cdfInfo))
                cdfInfoList.append((dataFram.get_name(), cdfInfo))

            indexList = list(map(lambda a: a.timestamp(), dataTruth.get_latitude().index))
            ax[3].set_xlim(datetime.utcfromtimestamp(min(indexList)), datetime.utcfromtimestamp(max(indexList)))
            ax[3].set_xlabel('local time(dd-hh-mm)')
            ax[3].set_ylabel('H error /m', fontsize='small')
            ax[2].set_ylabel('U error /m', fontsize='small')
            ax[1].set_ylabel('E error /m', fontsize='small')
            ax[0].set_ylabel('N error /m', fontsize='small')
            ax[0].set_title(f'Postprocess Vs {dataTruth.get_name()} in NEUH /m ', fontsize='small')
            plt.savefig(self._savePath + '/PP_Result.png')
            return cdfInfoList
            # plt.show()

    def drawSingleCdf(self, dataFram, name, pointTruth=None, onlyFix=False):
        if pointTruth is None:
            pointTruth = dataFram.getPointTruth()

        n_diff = dataFram.get_latitude(onlyFix=onlyFix) \
            .apply(lambda x: (x - pointTruth[0]) * D2R * radius)
        e_diff = dataFram.get_longitude(onlyFix=onlyFix) \
            .apply(lambda x: (x - pointTruth[1]) * D2R * radius * np.cos(pointTruth[0] * D2R))
        u_diff = dataFram.get_altitude(onlyFix=onlyFix) \
            .apply(lambda x: x - pointTruth[2])

        if onlyFix & (len(n_diff) <= 0 | len(e_diff) <= 0 | len(u_diff) <= 0):
            return

        hz_diff = np.sqrt(n_diff[:] ** 2 + e_diff[:] ** 2)
        fixList = dataFram.get_state(onlyFix=onlyFix).values
        self.drawNEU(n_diff, e_diff, u_diff, fixList, name, onlyFix=onlyFix)
        self.drawHorizontal(hz_diff, name, TITLES[3])
        if onlyFix:
            return hz_diff.describe(percentiles=[.68, .95, .997])
        return None

    def drawHorizontalLineWithTruth(self, data, truth):

        pass

    def drawNEU(self, n_diff, e_diff, u_diff, fixList, name=None, onlyFix=False):

        fig, ax = plt.subplots(figsize=(16, 10))
        anx_u = plt.subplot(313)
        xMax, xMin = 0, 0
        # 获取每个点的解状态
        colors = list(map(lambda c: self._fixColor[c.astype(int)], fixList))
        """ 获取采集的数据在x轴上的范围 来为不同状态的点加上特定的颜色"""
        indexList = list(map(lambda a: a.timestamp(), u_diff.index))
        timeMax = max(indexList)
        timeMin = min(indexList)

        xMax = timeMax if timeMax > xMax else xMax
        xMin = timeMin if (timeMin < xMin) | (xMin == 0) else xMin

        ''' 画点 （x= 时间,y= NEU上的误差，c = color）'''
        anx_u.scatter(u_diff.index, u_diff.values, c=colors, marker='.')

        if xMin == xMax:
            return

        anx_e = plt.subplot(312, sharex=anx_u)
        anx_n = plt.subplot(311, sharex=anx_u)

        ''' 画点 （x= 时间,y= NEU上的误差，c = color）'''
        anx_n.scatter(n_diff.index, n_diff.values, c=colors, marker='.')

        ''' 画点 （x= 时间,y= NEU上的误差，c = color）'''
        anx_e.scatter(e_diff.index, e_diff.values, c=colors, marker='.')

        fig.text(0.75, 0.25, WATERMARK, fontsize=35, color='gray', ha='right', va='bottom', alpha=0.2, rotation=30)

        plt.title('Error line in NEU -' + ("FIXED" if onlyFix else "ALL"))
        anx_n.set_ylabel(' N error / m')
        anx_e.set_ylabel(' E error / m')
        anx_u.set_ylabel(' U error / m')

        anx_u.set_xlim(datetime.utcfromtimestamp(xMin), datetime.utcfromtimestamp(xMax))
        anx_u.set_xlabel('local time(dd-hh-mm)')
        plt.savefig(self._savePath + '/NEU' + ('_FIX' if onlyFix else '_All') + '.png')
        plt.close(fig)

    def drawHorizontal(self, hzData, nameList, title):
        fig, axh = plt.subplots(figsize=(12, 8))
        axh.set_title(title)

        hzData.hist(cumulative=True, density=True, bins=400, histtype='step', linewidth=2.0,
                    label=nameList)
        plt.axhline(y=.95, color='b', linestyle='-.', lw=0.6, label='95% line')
        plt.axhline(y=.68, color='b', linestyle='-.', lw=0.6, label='68% line')
        fig.text(0.75, 0.25, WATERMARK, fontsize=35, color='gray', ha='right', va='center', alpha=0.2, rotation=30)
        axh.set_xlabel('Horizontal error (m)')
        axh.set_ylabel('Likelihood of occurrence')

        axh.legend(fontsize='small', ncol=1)
        axh.grid(True, ls=':', c='lightgray')
        fig.savefig(self._savePath + '/acdf.png')
        plt.close(fig)

    def drawSateCn0(self, name, sateCn0):
        fig, ax = plt.subplots(figsize=(12, 8))
        plt.title(f'{name} Satellite cn0 mean')
        plt.tick_params(labelsize=6)
        fig.text(0.85, 0.5, WATERMARK, fontsize=35, color='gray', ha='right', va='center', alpha=0.2, rotation=30)
        plt.bar(list(map(lambda x: x.get_name(), sateCn0)), list(map(lambda x: x.get_mean_cn0(), sateCn0)))
        plt.xticks(rotation=-45)
        ax.set_ylabel('CN0 (db)')
        ax.grid(True, ls=':', c='lightgray')
        fig.savefig(self._savePath + f'/{name}.png')
        plt.close(fig)

    def drawFixUseTime(self, name, licenceNum, timeStrList):
        fig, ax = plt.subplots(figsize=(12, 8))
        plt.title(f' fixed use Time(s) ')
        useTimeList = []
        lastTime = -1
        useTimeTotal = 0
        for strTime in timeStrList:
            strTime = float(strTime)
            timeSeconds = (strTime // 10000) * 3600 + ((strTime % 10000) // 100) * 60 + strTime % 100
            fixedTime = abs(timeSeconds - lastTime)
            if fixedTime >= 80000:
                fixedTime = abs(timeSeconds + 86400 - lastTime)
            useTime = abs(fixedTime) if lastTime != -1 else 0
            useTimeTotal += useTime
            useTimeList.append(useTime)
            lastTime = timeSeconds

        if len(useTimeList) > 0:
            print("useTime = ", useTimeTotal / len(useTimeList))
        plt.xticks(np.arange(0, len(useTimeList), step=1))
        plt.plot(list(range(len(useTimeList))), useTimeList)
        ax.set_ylabel('use time (s)')
        fig.savefig(self._savePath + f'/{name}_testPower.png')
        plt.close(fig)
