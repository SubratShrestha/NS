import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui

import collections
import random
import time
import math

file_data = open("./ble/streaming_data.txt", "r").read()
data = file_data.split('\n')


class DynamicPlotter():

    def __init__(self, sampleinterval=0.1, timewindow=10., size=(900, 600)):
        # Data stuff
        self._interval = int(sampleinterval * 1000)
        self._bufsize = int(timewindow / sampleinterval)
        self.databuffer = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Neural Recording Graph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'amplitude', 'V')
        self.plt.setLabel('bottom', 'time', 's')
        self.curve = self.plt.plot(self.x, self.y, pen=(255, 0, 0))
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def getdata(self):
        try:
            if len(data) > 1:
                new = data.pop(0)
                if new != '':
                    return new
            return None
        except Exception as e:
            print(e)
            return None

    def updateplot(self):
        added = 0
        while added < 10:
            sample = self.getdata()
            if sample is not None:
                self.databuffer.append(int(sample))
            added += 1
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)
        self.app.processEvents()

    def run(self):
        self.app.exec_()


if __name__ == '__main__':
    m = DynamicPlotter(sampleinterval=float(1 / 2000), timewindow=float(20000 / 20000))
    m.run()
