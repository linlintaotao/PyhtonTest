from docx import Document
from docx.shared import Inches, Pt
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os


class PPReporter:

    def __init__(self, ppPath, time, savePath=None):
        self.ppPath = ppPath
        self.time = time
        self.savePath = savePath

    def createTable(self):
        return

    def addPng(self, doc):
        for dirPath in os.listdir(self.ppPath):
            path_join = os.path.join(self.ppPath, dirPath)
            if os.path.isdir(path_join):
                for path in os.listdir(path_join):
                    resultPath = os.path.join(path_join, path)
                    if os.path.isdir(resultPath):
                        doc.add_paragraph('>>> %s:%s 图例 >>>' % (dirPath, path), style='Intense Quote')
                        for file in os.listdir(resultPath):
                            if file.endswith('png'):
                                doc.add_picture(os.path.join(resultPath, file))
                        doc.add_paragraph('<<< %s:%s 图例 <<<' % (dirPath, path), style='Intense Quote')

    def build(self):
        doc = Document()
        doc.add_heading('后处理版本测试', 0)
        doc.add_paragraph('测试报告生成时间：%s' % self.time)

        self.addPng(doc)
        doc.save(self.savePath + '/ppResult.docx')


if __name__ == '__main__':
    pp = PPReporter(os.path.abspath('../../data/PP'), time="0001")
    pp.build()
