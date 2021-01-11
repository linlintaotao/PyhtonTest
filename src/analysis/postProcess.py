# coding= utf-8
from src.chart.draw import FmiChart


class PostProcess:

    def __init__(self, truthPath, ppPath):
        self.truthPath = truthPath
        self.ppPath = ppPath
        self.postProcessDataList = list()
        self.truthDataList = list()

    def preparePostProcessData(self):
        for file in os.listdir(self.ppPath):
            if file.endswith(('log', "txt", 'nmea')):
                self.postProcessDataList.append(file)

    def prepareTruthData(self):
        for file in os.listdir(self.ppPath):
            if file.endswith(('log', "txt", 'nmea')):
                self.truthDataList.append(file)

    def analysis(self):
        for index in range(len(self.truthDataList)):
            # if  self.truthDataList[index]
            # fmiChart = FmiChart(None, )
            pass

    def makeReport(self):

        pass

    def start(self):

        pass


if __name__ == '__main__':
    pass
