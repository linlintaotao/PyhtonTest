# coding= utf-8
# 观察者模式

class Publisher:

    def __init__(self):
        self._observers = []
        self._data = None

    def register(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)
        print(self._observers)

    def unregister(self, observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            print('Failed to remove observer')

    def notifyAll(self, data):
        if data is not None:
            self._data = data
        for obs in self._observers:
            obs.notify(self._data)
