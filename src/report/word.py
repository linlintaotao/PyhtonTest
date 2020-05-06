# coding= utf-8

from docx import Document
from docx.shared import Inches
import os
import math


class WordReporter:

    def __init__(self, name, path, time):
        self._name = name
        self._time = time
        self._path = path
        self._pic = []
        self._fixNum = 0
        self._collectNum = 0
        self._bootVersion = None
        self._swVersion = None

    # 获取当前文件夹下的所有png文件
    @staticmethod
    def read_file(dirName, tag='png'):
        picture = list()
        for file in os.listdir(dirName):
            if file.endswith(tag):
                picture.append(file)
        picture.sort()
        return picture

    def setBootVersion(self, bootVersion):
        self._bootVersion = bootVersion

    def setSwVersion(self, softwareVersion):
        self._swVersion = softwareVersion

    def setFixAndAllPoints(self, fixNum, allNum):
        self._fixNum = fixNum
        self._collectNum = allNum

    def start(self):
        for fileName in os.listdir(self._path):
            dirName = os.path.join(self._path, fileName)
            print(dirName)
            if os.path.isdir(dirName):
                pictures = self.read_file(dirName)
                self.build(fileName, dirName, pictures)

    def build(self, fileName, dirName, pictures):
        doc = Document()
        doc.add_paragraph(fileName + ' 1h静态测试')
        doc.add_paragraph('测试设备：%s' % self._name)
        doc.add_paragraph('测试时间：%s' % self._time)
        if self._bootVersion is not None:
            doc.add_paragraph('Boot version：%s' % self._bootVersion)
        if self._swVersion is not None:
            doc.add_paragraph(' SW  version：%s' % self._swVersion)
        if self._collectNum is not 0:
            doc.add_paragraph('固定数：%d ,采集总数：%d ,固定率：%0.1f' % (self._fixNum, self._collectNum,
                                                              round(self._fixNum / self._collectNum * 100, 2)))
        doc.add_paragraph('测试误差：0~0.02m 占比 94% ,0.02~0.05m 占比 5%')
        doc.add_paragraph('基站距离 42km')

        doc.add_paragraph('测试结果图例')
        for picture in pictures:
            doc.add_picture(dirName + '/' + picture, Inches(6), Inches(4))

        doc.save(self._path + '/' + fileName + '.docx')
        pass


if __name__ == '__main__':
    word = WordReporter('P20-8130', os.path.abspath('..') + "/data", '20200416')
    # word.setBootVersion('RTK v.1.3.0.ss0415-1400-auto-rtk-mode_min23_50_wraw-base-931d43')
    word.setSwVersion('RTK v.1.3.0.ss0416-1055-auto-rtk-mode_min23_50_wraw-base-fd9815')
    word.setFixAndAllPoints(48658, 49750)
    word.start()
