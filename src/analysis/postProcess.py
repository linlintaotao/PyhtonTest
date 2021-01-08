# coding= utf-8

class PostProcess:

    def __init__(self, truthPath, ppPath):
        self.truthPath = truthPath
        self.ppPath = ppPath
        self.analysisDataList = list()

    def preparePostProcessData(self):
        for file in os.listdir(self.ppPath):
            if file.endswith(('log', "txt", 'nmea')):
                self.analysisDataList.append(file)

    def prepareTruthData(self):

        pass

    def analysis(self):

        pass

    def makeReport(self):

        pass

    def start(self):

        pass


if __name__ == '__main__':
    pass
