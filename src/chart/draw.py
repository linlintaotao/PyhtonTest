# coding= utf-8
# 绘图工具
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pacthes
from datetime import datetime
from src.analysis import Gauss
import math

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

    def drawScatter(self, name, xPos, yPos, fixList=None, useTrue=False):
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
        textInfo = ''
        if fixList is None:
            color = 'green'
            # accuracyItem = 0.02
            errorIn1cm, errorIn2cm = 0, 0
            for i in range(len(xPos)):
                a = abs(xPos[i] - xCenter)
                b = abs(yPos[i] - yCenter)

                error = math.sqrt(a ** 2 + b ** 2)
                if error < 0.02:
                    errorIn1cm += 1
                elif error < 0.05:
                    errorIn2cm += 1
            textInfo = format("Fixed Info: error<0.02m  %d%% ; 0.02<error<0.05m  %d%%" % (
                round(errorIn1cm * 100 / len(xPos), 2),
                round(errorIn2cm * 100 / len(xPos), 2)))
            print(textInfo)

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
        ax.scatter(list(map(lambda x: x - xCenter, xPos)), list(map(lambda y: y - yCenter, yPos)), marker='1', c=color)

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
        ax2 = plt.subplot(212)
        for data in dataframe:
            data.get_sateNum().plot(label=data.get_name())
        ax2.set_ylabel('SateNum', fontsize=10)
        ax2.set_xlabel('local time', fontsize=10)

        ax1 = plt.subplot(211, sharex=ax2)
        for data in dataframe:
            data.get_state().plot(label=data.get_name(), fontsize=9)
        fig.text(0.75, 0.25, WATERMARK, fontsize=35, color='gray', ha='right', va='bottom', alpha=0.2, rotation=30)

        plt.title(r'FixState and sateNums')
        ax1.set_ylabel('FixState', fontsize=10)
        ax1.set_ylim(0, 7)
        plt.grid(True, ls=':', c='lightgray')
        plt.savefig(self._savePath + '/bsateNumAndFixSate.png')
        plt.close(fig)

    # pointTruth [latitude,longitude,altitude]
    # dataTruth
    def drawCdf(self, dataFrameList, dataTruth=None, dataFrame=None, pointTruth=None, singlePoint=False, onlyFix=False):
        nameList = []
        if dataFrame is not None:
            nameList.append(dataFrame.get_name() + '_Fix_' if onlyFix else '_')
            self.drawSingleCdf(dataFrame, nameList, pointTruth=None, onlyFix=onlyFix)
            return

        for dataFram in dataFrameList:
            # if dataFram.get_altitude(onlyFix=True) is None ||
            nameList.append(dataFram.get_name())
            if singlePoint:
                try:
                    self.drawSingleCdf(dataFram, dataFram.get_name(), pointTruth=None, onlyFix=onlyFix)
                except Exception as e:
                    print(e)
                    continue
            else:
                # todo 跟另一个数据对比
                pass

    def drawSingleCdf(self, dataFram, name, pointTruth=None, onlyFix=False):
        n_diffList, e_diffList, u_diffList, fixList, hz_diffList = [], [], [], [], []
        if pointTruth is None:
            pointTruth = dataFram.getPointTruth()

        n_diff = dataFram.get_latitude(onlyFix=onlyFix).apply(lambda x: (x - pointTruth[0]) * D2R * radius)
        e_diff = dataFram.get_longitude(onlyFix=onlyFix).apply(lambda x:
                                                               (x - pointTruth[1]) * D2R * radius *
                                                               np.cos(pointTruth[0]) * D2R)
        u_diff = dataFram.get_altitude(onlyFix=onlyFix).apply(lambda x: x - pointTruth[2])

        n_diffList.append(n_diff)
        e_diffList.append(e_diff)
        u_diffList.append(u_diff)
        hz_diffList.append(np.sqrt(n_diff[:] ** 2 + e_diff[:] ** 2))
        fixList.append(dataFram.get_state(onlyFix=onlyFix).values)
        # self.drawNEU(n_diffList, fixList, onlyFix=onlyFix)
        # self.drawNEU(e_diffList, fixList, onlyFix=onlyFix)
        # self.drawNEU(u_diffList, fixList, onlyFix=onlyFix)

        self.drawNEU(n_diffList, e_diffList, u_diffList, fixList, name, onlyFix=onlyFix)

        self.drawHorizontal(hz_diffList, name, TITLES[3])

    # def drawNEU(self, lineData, title, fixList, name='', onlyFix=False):
    #
    #     fig, anx = plt.subplots(figsize=(16, 8))
    #     xMax, xMin = 0, 0
    #     for i in range(len(lineData)):
    #         data = lineData[i]
    #         # if onlyFix & (len(data)) <= 0:
    #         #     continue
    #
    #         # 获取每个点的解状态
    #         colors = list(map(lambda c: self._fixColor[c.astype(int)], fixList[i]))
    #         """ 获取采集的数据在x轴上的范围 来为不同状态的点加上特定的颜色"""
    #         indexList = list(map(lambda a: a.timestamp(), data.index))
    #         timeMax = max(indexList)
    #         timeMin = min(indexList)
    #
    #         if xMin == 0:
    #             xMin = timeMax
    #         xMax = timeMax if timeMax > xMax else xMax
    #         xMin = timeMin if timeMin < xMin else xMin
    #
    #         ''' 画点 （x= 时间,y= NEU上的误差，c = color）'''
    #         anx.scatter(data.index, data.values, c=colors)
    #
    #     plt.axhline(y=0.2, color='b', linestyle='-.', lw=0.6, label='0.2 m line')
    #     plt.axhline(y=-0.2, color='b', linestyle='-.', lw=.6)
    #     fig.text(0.75, 0.25, WATERMARK, fontsize=25, color='gray', ha='right', va='bottom', alpha=0.4)
    #
    #     anx.set_title(title)
    #     anx.set_ylabel('Differential error / m')
    #     anx.set_xlabel('local time(dd-hh-mm)')
    #     anx.set_xlim(datetime.utcfromtimestamp(xMin), datetime.utcfromtimestamp(xMax))
    #
    #     anx.legend(fontsize='small', ncol=1)
    #     anx.grid(True, ls=':', c='lightgray')
    #     plt.savefig(self._savePath + '/' + name + ('_FIX' if onlyFix else '_All') + '.png')

    def drawNEU(self, n_diff, e_diff, u_diff, fixList, name, onlyFix=False):

        fig, ax = plt.subplots(figsize=(16, 10))
        anx_u = plt.subplot(313)

        xMax, xMin = 0, 0

        for i in range(len(u_diff)):
            data = u_diff[i]

            # 获取每个点的解状态
            colors = list(map(lambda c: self._fixColor[c.astype(int)], fixList[i]))
            """ 获取采集的数据在x轴上的范围 来为不同状态的点加上特定的颜色"""
            indexList = list(map(lambda a: a.timestamp(), data.index))
            timeMax = max(indexList)
            timeMin = min(indexList)

            xMax = timeMax if timeMax > xMax else xMax
            xMin = timeMin if (timeMin < xMin) | (xMin == 0) else xMin

            ''' 画点 （x= 时间,y= NEU上的误差，c = color）'''
            anx_u.scatter(data.index, data.values, c=colors, marker='.')

        anx_e = plt.subplot(312, sharex=anx_u)
        anx_n = plt.subplot(311, sharex=anx_u)
        for i in range(len(n_diff)):
            data = n_diff[i]
            # 获取每个点的解状态
            colors = list(map(lambda c: self._fixColor[c.astype(int)], fixList[i]))
            ''' 画点 （x= 时间,y= NEU上的误差，c = color）'''
            anx_n.scatter(data.index, data.values, c=colors, marker='.')
            # data.plot(label=FILE_NAME_PREFIX[num + 1] + ' ' + dir, lw=0.3)

        for i in range(len(e_diff)):
            data = e_diff[i]
            # 获取每个点的解状态
            colors = list(map(lambda c: self._fixColor[c.astype(int)], fixList[i]))
            ''' 画点 （x= 时间,y= NEU上的误差，c = color）'''
            anx_e.scatter(data.index, data.values, c=colors, marker='.')

        # plt.axhline(y=0.2, color='b', linestyle='-.', lw=0.6, label='0.2 m line')
        # plt.axhline(y=-0.2, color='b', linestyle='-.', lw=.6)
        fig.text(0.75, 0.25, WATERMARK, fontsize=35, color='gray', ha='right', va='bottom', alpha=0.2, rotation=30)

        plt.title('Error line in NEU -' + ("FIXED" if onlyFix else "ALL"))
        # anx.set_title(title)
        anx_n.set_ylabel(' N error / m')
        anx_e.set_ylabel(' E error / m')
        anx_u.set_ylabel(' U error / m')

        anx_u.set_xlim(datetime.utcfromtimestamp(xMin), datetime.utcfromtimestamp(xMax))
        anx_u.set_xlabel('local time(dd-hh-mm)')

        # anx.legend(fontsize='small', ncol=1)
        # anx.grid(True, ls=':', c='lightgray')
        plt.savefig(self._savePath + '/NEU' + ('_FIX' if onlyFix else '_All') + '.png')
        plt.close(fig)

    def drawHorizontal(self, hzData, nameList, title):
        fig, axh = plt.subplots(figsize=(12, 8))
        axh.set_title(title)

        for i in range(len(hzData)):
            hzData[i].hist(cumulative=True, density=True, bins=400, histtype='step', linewidth=2.0,
                           label=nameList[i])
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
        plt.title('Satellite cn0 mean')
        plt.tick_params(labelsize=6)
        fig.text(0.85, 0.5, WATERMARK, fontsize=35, color='gray', ha='right', va='center', alpha=0.2, rotation=30)
        plt.bar(list(map(lambda x: x.get_name(), sateCn0)), list(map(lambda x: x.get_mean_cn0(), sateCn0)))
        ax.set_ylabel('CN0 (db)')
        ax.grid(True, ls=':', c='lightgray')
        fig.savefig(self._savePath + '/Cn0.png')
        plt.close(fig)
