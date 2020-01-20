#
import os
from datetime import datetime, timedelta
import pandas as pd
from pip._vendor import chardet
from src.analysis.nmea import GNGGAFrame, GSV
from src.chart.analysisChart import FmiChart


class AnalysisTool:

    def __init__(self, dir=os.path.abspath('../../data/')):
        self._dir = dir
        self.localTime = datetime.now().date()
        self.timeCheck = False
        self._dataFiles = list()
        self._ggaEntity = list()
        self._GSVEntity = list()

    # 获取当前文件夹下的所有文件
    def read_file(self, tag='txt'):
        for file in os.listdir(self._dir):
            if file.endswith(tag):
                self._dataFiles.append(file)

    # 获取文件编码类型
    def get_encoding(self, file):
        # 二进制方式读取，获取字节数据，检测类型
        with open(file, 'rb') as f:
            return chardet.detect(f.read())['encoding']

    def analysis(self):
        for file in self._dataFiles:
            '''
                we put 20 names because it's NMEA-0183 Data, each line has different num with step ','  
            '''
            df = pd.read_table(self._dir + '/' + file, sep=',',
                               encoding=self.get_encoding(self._dir + '/' + file),
                               header=None,
                               names=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                                      '11', '12', '13', '14', '15', '16', '17', '18', '19', '20'],
                               error_bad_lines=False)

            self._GSV = df.loc[df['0'].str.contains('GSV')].copy()
            gsv = GSV(file, self._GSV)
            gga = GNGGAFrame(file, df.loc[df['0'] == '$GNGGA'].copy(),
                             self.localTime)
            self._ggaEntity.append(gga)
            self._GSVEntity.append(gsv)

        self.drawPic()

    def analysisGSV(self):

        pass

    def drawPic(self):
        fmiChar = FmiChart(path=self._dir + '/')
        pointTruth = [40.064109, 116.228165, 54.6]
        fmiChar.drawLineChart(self._ggaEntity)
        fmiChar.drawCdf(self._ggaEntity, pointTruth=pointTruth, singlePoint=True)
        for data in self._ggaEntity:
            x, y, z = data.get_scatter()
            fmiChar.drawScatter(data.get_name(), x, y)
        for gsv in self._GSVEntity:
            fmiChar.drawSateCn0(gsv.get_name(), gsv.get_satellites_status())


if __name__ == '__main__':
    analysisTool = AnalysisTool()
    analysisTool.read_file()
    analysisTool.analysis()
