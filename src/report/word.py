# coding= utf-8

from docx import Document
from docx.shared import Inches
import os


class WordReporter:

    def __init__(self, path, time):
        self._time = time
        self._path = path
        self._pic = []
        self._records = None
        self._testPower = False

    # 获取当前文件夹下的所有png文件
    @staticmethod
    def read_file(dirName, tag='png'):
        picture = list()
        for file in os.listdir(dirName):
            if file.endswith(tag):
                picture.append(file)
        picture.sort()
        return picture

    def setRecords(self, records, testPower):
        self._records = records
        self._testPower = testPower

    def addPng(self, doc):
        listfile = os.listdir(self._path)
        listfile.sort()
        for fileName in listfile:
            dirName = os.path.join(self._path, fileName)
            if os.path.isdir(dirName):
                doc.add_paragraph('%s 图例' % fileName, style='Intense Quote')
                pictures = self.read_file(dirName)
                for picture in pictures:
                    doc.add_picture(dirName + '/' + picture, Inches(6), Inches(4))
                doc.add_paragraph('%s 图例' % fileName, style='Intense Quote')

    def build(self):
        doc = Document()
        doc.add_heading('日常静态测试', 0)
        doc.add_paragraph('测试报告生成时间：%s' % self._time)
        doc.add_paragraph('基站: Obs 20C')

        if self._records is not None:
            table = doc.add_table(rows=1, cols=6)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = '串口号'
            hdr_cells[1].text = 'SwVersion'
            hdr_cells[2].text = 'navi_rate'
            hdr_cells[3].text = 'work_mode'
            hdr_cells[4].text = '总数' if self._testPower is not True else 'lisence次数'
            hdr_cells[5].text = '固定率' if self._testPower is not True else '固定次数'

            for COM, version, fixNum, percent, naviRate, workMode in self._records:
                row_cells = table.add_row().cells
                row_cells[0].text = COM
                row_cells[1].text = version
                row_cells[2].text = naviRate
                row_cells[3].text = workMode
                row_cells[4].text = fixNum
                row_cells[5].text = percent

        doc.add_heading('测试结果图例', level=1)
        self.addPng(doc)
        doc.save(self._path + '/' + self._time + 'report.docx')


if __name__ == '__main__':
    records = (
        ('3', '101', 'Spam', 'g'),
        ('7', '422', 'Eggs', 'h'),
        ('4', '631', 'Spam, spam, eggs, and spam', 't')
    )
    word = WordReporter(os.path.abspath('../..') + "/data", "12345678")
    word.setRecords(records, testPower=False)
    word.build()
