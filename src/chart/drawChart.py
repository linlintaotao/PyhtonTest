# 绘图工具
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as pacthes
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, BoundaryNorm
from datetime import timedelta, datetime

accuracyItems = [0.01, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 100, 1000]
WATERMARK = "By FMI Tech"
radius = 6371000
D2R = 0.017453292519943295

TITLES = [r'RTK north differential errors in $meters$',
          r'RTK east differential errors in $meters$',
          r'RTK up differential errors in $meters$',
          r'RTK horizontal differential errors in $meters$']


class FmiChart:

    def __init__(self, path=''):
        self._savePath = path
        self._fixColor = ['black', 'black', 'red', 'gray', 'green', 'blue', 'yellow']

    ''' 获取绘图的最小精度 0.01~ 1000 (m)'''

    def get_accuracy(self, axis):
        accuracyItem = round(axis / 10, 2)
        for i in range(len(accuracyItems)):
            if accuracyItem < accuracyItems[i]:
                accuracyItem = accuracyItems[i]
                return accuracyItem
        return accuracyItems[-1]

    ''' 画测试结果的结果点位图 
        name : 测试的数据来源
        xpos : x轴坐标
        ypos : y轴坐标
        onlyFix  : 是否只统计固定解
    '''

    def drawScatter(self, name, xPos, yPos, onlyFix=True):
        xMax, xMin, yMax, yMin = max(xPos), min(xPos), max(yPos), min(yPos)
        xCenter, yCenter = np.mean(xPos), np.mean(yPos)
        axis = max([abs(xMax - xCenter),
                    abs(xMin - xCenter),
                    abs(yMax - yCenter),
                    abs(yMin - yCenter)]) * 1.1

        fig, ax = plt.subplots(figsize=[10, 8])
        accuracyItem = self.get_accuracy(axis)

        '''画提示网格和圆'''
        for i in range(3):
            mid = round(accuracyItem * i, 2)
            print(mid)
            circle = pacthes.Circle((0, 0), mid, fill=False, ls='--', color='lightgray', gid=str(mid))
            if i != 0:
                ax.annotate(str(mid), xy=(accuracyItem * (i - 1), 0), xytext=(mid, 0), ha='right', color='blue')
            ax.add_patch(circle)
        fig.text(0.85, 0.5, WATERMARK, fontsize=40, color='gray', ha='right', va='center', alpha=0.2, rotation=30)
        ''' 根据解状态匹配对应的颜色 '''
        if onlyFix:
            color = 'green'
        else:
            color = list(map(lambda c: self._fixColor[c.astype(int)], onlyFix))
        '''画点'''
        ax.scatter(list(map(lambda x: x - xCenter, xPos)), list(map(lambda y: y - yCenter, yPos)), marker='1', c=color)
        ax.set_xlim(-axis, axis)
        ax.set_ylim(-axis, axis)
        plt.xlabel(r'points x (m)')
        plt.ylabel(r'points y (m)')
        plt.title('%s Scatter View' % name)
        plt.legend()
        plt.axis('equal')
        plt.grid(True, ls=':', c='lightgray')
        plt.savefig(self._savePath + name + '.png')
        # plt.show()

    def drawLineChart(self, dataframe):
        fig = plt.subplots(figsize=[16, 8])
        ax2 = plt.subplot(212)
        for data in dataframe:
            data.get_sateNum().plot(label=data.get_name())
        ax2.set_ylabel('SateNum', fontsize=10)
        ax2.set_xlabel('local time', fontsize=10)

        ax1 = plt.subplot(211, sharex=ax2)
        for data in dataframe:
            data.get_fixState().plot(label=data.get_name(), fontsize=9)
        plt.title(r'FixState and sateNums')
        ax1.set_ylabel('FixState', fontsize=10)
        plt.legend()
        plt.grid(True, ls=':', c='lightgray')
        plt.savefig(self._savePath + 'sateNumAndFixSate.png', loc="low")
        # plt.show()

    # pointTruth [latitude,longitude,altitude]
    # dataTruth
    def drawCdf(self, dataFrameList, dataTruth=None, pointTruth=None, singlePoint=False):
        n_diffList, e_diffList, u_diffList, hz_diffList = [], [], [], []
        nameList, fixList = [], []
        for dataFram in dataFrameList:
            nameList.append(dataFram.get_name())
            n_diff, e_diff, u_diff = [], [], []
            if singlePoint:
                n_diff = dataFram.get_latitude().apply(lambda x: (x - pointTruth[0]) * D2R * radius)
                e_diff = dataFram.get_longitude().apply(lambda x:
                                                        (x - pointTruth[1]) * D2R * radius *
                                                        np.cos(pointTruth[0]) * D2R)
                u_diff = dataFram.get_altitude().apply(lambda x: x - pointTruth[2])
                hz_diffList.append(np.sqrt(n_diff[:] ** 2 + e_diff[:] ** 2))
            else:
                # todo
                pass
            n_diffList.append(n_diff)
            e_diffList.append(e_diff)
            u_diffList.append(u_diff)
            fixList.append(dataFram.get_fixState().values)
        self.drawNEU(n_diffList, nameList, TITLES[0], fixList, name='north')
        self.drawNEU(e_diffList, nameList, TITLES[1], fixList, name='east')
        self.drawNEU(u_diffList, nameList, TITLES[2], fixList, name='up')
        self.drawHorizontal(hz_diffList, nameList, TITLES[3])

    def drawNEU(self, lineData, nameList, title, fixList, name=''):
        fig, anx = plt.subplots(figsize=(16, 8))
        xMax, xMin = 0, 0
        for i in range(len(lineData)):
            data = lineData[i]
            # 获取每个点的解状态
            colors = list(map(lambda c: self._fixColor[c.astype(int)], fixList[i]))
            """ 获取采集的数据在x轴上的范围 来为不同状态的点加上特定的颜色"""
            timeMax = max(list(map(lambda a: a.timestamp(), data.index)))
            timeMin = min(list(map(lambda a: a.timestamp(), data.index)))
            if xMin == 0:
                xMin = timeMax
            xMax = timeMax if timeMax > xMax else xMax
            xMin = timeMin if timeMin < xMin else xMin

            ''' 画点 （x= 时间,y= NEU上的误差，c = color）'''
            anx.scatter(data.index, data.values, c=colors)

        plt.axhline(y=0.2, color='b', linestyle='-.', lw=0.6, label='0.2 m line')
        plt.axhline(y=-0.2, color='b', linestyle='-.', lw=.6)
        fig.text(0.75, 0.25, WATERMARK, fontsize=25, color='gray', ha='right', va='bottom', alpha=0.4)

        anx.set_title(title)
        anx.set_ylabel('Differential error / m')
        anx.set_xlabel('local time(dd-hh-mm)')
        anx.set_xlim(datetime.utcfromtimestamp(xMin), datetime.utcfromtimestamp(xMax))

        anx.legend(fontsize='small', ncol=1)
        anx.grid(True, ls=':', c='lightgray')
        plt.savefig(self._savePath + name + '.png')
        # plt.show()

    def drawHorizontal(self, hzData, nameList, title):
        fig, axh = plt.subplots(figsize=(16, 8))
        axh.set_title(title)

        for i in range(len(hzData)):
            hzData[i].hist(cumulative=True, density=True, bins=400, histtype='step', linewidth=2.0,
                           label=nameList[i])
        plt.axhline(y=.95, color='b', linestyle='-.', lw=0.6, label='95% line')
        plt.axhline(y=.68, color='b', linestyle='-.', lw=0.6, label='68% line')
        fig.text(0.75, 0.25, WATERMARK, fontsize=25, color='gray', ha='right', va='center', alpha=0.4)
        axh.set_xlabel('Horizontal error (m)')
        axh.set_ylabel('Likelihood of occurrence')

        axh.legend(fontsize='small', ncol=1)
        axh.grid(True, ls=':', c='lightgray')
        fig.savefig(self._savePath + 'cdf.png')
        # plt.show()

    def drawSateCn0(self, name, sateCn0):
        fig, ax = plt.subplots(figsize=(16, 8))
        plt.title('Satellite cn0 mean')
        plt.tick_params(labelsize=6)
        fig.text(0.85, 0.5, WATERMARK, fontsize=40, color='gray', ha='right', va='center', alpha=0.2, rotation=30)
        plt.bar(list(map(lambda x: x.get_name(), sateCn0)), list(map(lambda x: x.get_mean_cn0(), sateCn0)))
        ax.set_ylabel('CN0 (db)')
        ax.grid(True, ls=':', c='lightgray')
        fig.savefig(self._savePath + name + 'Cn0.png')
        # plt.show()
