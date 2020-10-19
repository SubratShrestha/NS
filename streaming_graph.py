import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import numpy as np
from scipy.interpolate import interp1d
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui


# fig = plt.figure()
# ax1 = fig.add_subplot(1, 1, 1)


# def animate(i):
#     file_data = open("./ble/streaming_data.txt", "r").read()
#     data = file_data.split('\n')
#     while len(data) > 200:
#         data.pop(0)
#     x = []
#     y = []
#     for i, j in enumerate(data):
#         if j != '':
#             x.append(int(i))
#             y.append(int(j))
#     x = np.array(x)
#     y = np.array(y)
#     x_new = np.linspace(x.min(), x.max(), 200)
#     f = interp1d(x, y, kind='quadratic')
#     y_smooth = f(x_new)
#     plt.plot(x_new, y_smooth)
#     plt.scatter(x, y)
#     plt.xlabel('Instance')
#     plt.ylabel('Signal')
#
#     ax1.clear()
#     ax1.plot(x, y)
#
#
# ani = animation.FuncAnimation(fig, animate, frames=60, interval=30)
# plt.show()
##########################################################################
# file_data = open("./ble/streaming_data.txt", "r").read()
# data = file_data.split('\n')
# while len(data) > 115:
#     data.pop(0)
# x = []
# y = []
# for i, j in enumerate(data):
#     if j != '':
#         x.append(int(i))
#         y.append(int(j))
# x = np.array(x)
# y = np.array(y)
# pg.plot(x, y, pen=1, symbolPen=pg.mkPen(color=(0, 0, 255), width=0),
#               symbolBrush=pg.mkBrush(0, 0, 255, 255), symbol='o')
#
# import sys
# if (sys.flags.interactive != 'y') or not hasattr(QtCore, 'PYQT_VERSION'):
#     QtGui.QApplication.instance().exec_()
##########################################################################
import collections
import random
import time
import math

file_data = open("./ble/streaming_data.txt", "r").read()
data = file_data.split('\n')

class DynamicPlotter():

    def __init__(self, sampleinterval=0.1, timewindow=10., size=(600,350)):
        # Data stuff
        self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.app = QtGui.QApplication([])
        self.plt = pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'amplitude', 'V')
        self.plt.setLabel('bottom', 'time', 's')
        self.curve = self.plt.plot(self.x, self.y, pen=(255,0,0))
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def getdata(self):
        new = data.pop(0)
        return new

    def updateplot(self):
        self.databuffer.append( self.getdata() )
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)
        self.app.processEvents()

    def run(self):
        self.app.exec_()

if __name__ == '__main__':

    m = DynamicPlotter(sampleinterval=0.0005, timewindow=.1)
    m.run()