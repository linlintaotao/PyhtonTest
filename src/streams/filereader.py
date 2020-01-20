#
import os


class FileWriter:

    def __init__(self, name, dir=''):
        """
          self._path 文件记录的地址
          self._name 文件的名字
        """
        self._dir = dir
        self._name = name
        self._path = os.path.join(dir, name)
        print(self._path)
        self._entity = None
        self.state = False
        self.open()

    def open(self):
        try:
            self._entity = open(self._path, 'wb')
            print('open file')
            self.state = True
        except Exception as e:
            print(f'open file %s error %s' % (self._name, e))
            if self._entity is not None:
                self._entity.close()

    def write(self, data):
        print('write data = %s' % data)
        if self.state is True:
            self._entity.write(data)
            self._entity.flush()

    def close(self):
        if self._entity is not None:
            self.state = False
            self._entity.flush()
            self._entity.close()
