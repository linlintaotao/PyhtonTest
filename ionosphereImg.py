import datetime
import os
from datetime import datetime
from io import BytesIO
import requests
from PIL import Image

IONOS_PATH = "http://www.trimbleionoinfo.com/Images.svc/TEC"


class DownloadIonosphere:

    def __init__(self):
        self.isRunning = True
        self.filePath = None
        self.url = "http://www.trimbleionoinfo.com/Images.svc/TEC"

    def queryTrimblePic(self, url):
        try:
            self.filePath = os.path.join(os.path.abspath('.'),
                                         'TEC' + os.sep + datetime.utcnow().strftime('%Y%m%d'))
            if not os.path.exists(path=self.filePath):
                os.makedirs(self.filePath)
            # 图片URL
            req = requests.get(url)
            # 使用BytesIO接口
            image = Image.open(BytesIO(req.content))
            name = datetime.utcnow().strftime("%Y%m%d-%H")
            fileName = name + '.' + image.format.lower()
            with open(os.path.join(self.filePath, fileName), 'wb') as f:
                f.write(req.content)

        except Exception as e:
            print("query", e)

    def start(self) -> None:
        # print("down load pic")
        self.queryTrimblePic(self.url)

    def stop(self):
        self.isRunning = False


if __name__ == '__main__':
    pass
