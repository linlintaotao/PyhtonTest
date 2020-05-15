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

    # 获取当前文件夹下的所有png文件
    @staticmethod
    def read_file(dirName, tag='png'):
        picture = list()
        for file in os.listdir(dirName):
            if file.endswith(tag):
                picture.append(file)
        picture.sort()
        return picture

    def setRecords(self, records):
        self._records = records

    def addPng(self, doc):
        for fileName in os.listdir(self._path):
            dirName = os.path.join(self._path, fileName)
            if os.path.isdir(dirName):
                doc.add_paragraph('%s 图例' % fileName.split('-')[0], style='Intense Quote')
                pictures = self.read_file(dirName)
                for picture in pictures:
                    doc.add_picture(dirName + '/' + picture, Inches(6), Inches(4))
                doc.add_paragraph('%s 图例' % fileName.split('-')[0], style='Intense Quote')

    def build(self):
        doc = Document()
        doc.add_heading('日常静态测试', 0)
        doc.add_paragraph('测试报告生成时间：%s' % self._time)
        doc.add_paragraph('基站: Obs_30')

        if self._records is not None:
            table = doc.add_table(rows=1, cols=4)
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = '串口号'
            hdr_cells[1].text = 'SwVersion'
            hdr_cells[2].text = '固定总数'
            hdr_cells[3].text = '固定率'
            for COM, version, fixNum, percent in self._records:
                row_cells = table.add_row().cells
                row_cells[0].text = COM
                row_cells[1].text = version
                row_cells[2].text = fixNum
                row_cells[3].text = percent

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
    word.setRecords(records)
    word.build()
