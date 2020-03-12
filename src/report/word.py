# coding= utf-8

from docx import Document
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
        doc.add_paragraph('P20 每日静态测试')
        doc.add_paragraph('测试设备：%s' % self._name)
        doc.add_paragraph('测试时间：%s' % self._time)
        if self._bootVersion is not None:
            doc.add_paragraph('Boot version：%s' % self._bootVersion)
        if self._swVersion is not None:
            doc.add_paragraph(' SW  version：%s' % self._swVersion)
        if self._collectNum is not 0:
            doc.add_paragraph('固定数：%d ,采集总数：%d ,固定率：%0.1f' % (self._fixNum, self._collectNum,
                                                              float(self._fixNum / self._collectNum)))
        doc.add_paragraph('测试结果图例')
        for picture in pictures:
            doc.add_picture(dirName + '/' + picture)

        doc.save(self._path + '/' + fileName + '.docx')
        pass


if __name__ == '__main__':
    word = WordReporter('P20', '../../data/', '20200310-20200311')
    # word.setBootVersion('1.0.1.1')
    # word.setSwVersion('12121')
    # word.setFixAndAllPoints(50, 100)
    word.start()
