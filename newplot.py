import csv
import numpy as np #py -m pip install numpy
import datetime
import time
from time import strftime, localtime
import pyqtgraph as pg	#py -m pip install pyQtGraph #py -m pip install pyQt5
from pyqtgraph import QtCore, QtGui
import sys
import os
import itertools

filename=strftime("%Y%m", localtime())+'TemperatureLogFile.csv'
currentmonth = localtime().tm_mon

data=[]
name=[]
linenow=0 #current line number of file
names = {"28FF641D9676E30D": "Air_Outlet", "28FF641D96713188": "Air_Return"}
namehere = []

with open(filename, 'r') as csvfile:
	spamreader = csv.reader(csvfile)
	for row in spamreader:
		data.append(row)
		linenow+=1

dataArray = np.array(list(itertools.zip_longest(*data, fillvalue=0)))
for i in range(2, len(dataArray)):
	namehere.append(names[dataArray[i,0]] if dataArray[i,0] in names else '')
dataArray=np.delete(dataArray,(0),1)
dataArray=np.delete(dataArray,(1),0)


dataArray[dataArray==''] = 0
dataArray = dataArray.astype(np.float)
beginningtime=dataArray[0,0]

dataArray[0] -= beginningtime
dataArray[0] /=3600

class TestClass(QtGui.QMainWindow):
	def __init__(self):
		super(TestClass, self).__init__()
		self.initUI()
		
	
	def initUI(self):
		if (localtime().tm_mon!=currentmonth):
			os.execl(sys.executable, sys.executable, *sys.argv)
		self.setWindowTitle("temperature sensor graph")
		win = QtGui.QWidget()
		self.plt = pg.PlotWidget(name='Plot1')  ## giving the plots names allows us to link their axes together
		self.plt.showGrid(x=True,y=True)
		self.plt.setLabel('left', "Temp", units='C')
		self.plt.setLabel('bottom', "time", units='h')
		self.setCentralWidget(win)
		self.timer = pg.QtCore.QTimer()
		self.curve = self.plt.plot(x=[], y=[])
		self.plt.addLegend()
		# self.plt.addItem(self.label)
		# self.proxy = pg.SignalProxy(self.plt.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
		layout = QtGui.QGridLayout(win)
		layout.addWidget(self.plt, 1, 0)
		self.curve.scene().sigMouseMoved.connect(self.mouseMoved)
		step=linenow//10000
		plots = []
		self.plt.setYRange(2, 60, padding=0)
		for q in range(1,len(dataArray)):
			plots.append(self.plt.plot(dataArray[0, -50000::],dataArray[q, -50000::], pen=(q,9), name = namehere[q-1]))
		
		def update() :
			global dataArray
			global linenow
			global maxlen
			#self.plt.clear()
			csvfile=open(filename)
			# try:
				# self.plt.legend.scene().removeItem(self.plt.legend)
			# except Exception as e:
				# print (e)
			for i, line in enumerate(csvfile):
				if i<=linenow:
					continue
				linenow=i
				dummy=np.array(line.strip('\n').split(','))
				if (len(dummy)>len(dataArray)+1): 
					for j, linee in enumerate(csvfile):
						if j==0:
							dummyy=linee
						else:
							break
					for i in range(len(dataArray), len(dummy)-1):
						ar=np.zeros(len(dataArray[0]), float)
						dataArray=np.append(dataArray, [ar], axis=0)
						namehere.append(names[dummyy[i-1,0]] if dataArray[i-1,0] in names else '')
						plots.append(self.plt.plot(dataArray[0, -50000::], dataArray[i, -50000::], pen=(i,9), name=namehere[i-1]))
				arr=np.zeros((len(dataArray), 1), float)
				for o in range(len(dummy)):
					if (o==0):
						arr[0,0] = (float(dummy[0])-beginningtime)/3600
						continue
					if (o==1):
						continue
					if (dummy[o]==''):
						arr[o-1,0]=0
						continue
					arr[o-1,0] = float(dummy[o])
				dataArray=np.append(dataArray, arr, axis=1)
			#step=linenow//10000
			for q in range(1,len(dataArray)):
				plots[q-1].setData(dataArray[0, -50000::],dataArray[q, -50000::])
				
		self.timer.timeout.connect(update)
		self.timer.start(10)
		
	def mouseMoved(self, evt):
			p = self.plt.plotItem.vb.mapSceneToView(evt)
			self.statusBar().showMessage("Time: {} Temp: {}".format(time.asctime(time.localtime(p.x()*3600+beginningtime)), p.y()))		
## Start Qt event loop.
def main():
    app = QtGui.QApplication(sys.argv)
    ex = TestClass()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()