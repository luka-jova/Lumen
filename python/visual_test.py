import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from datetime import datetime
import obrada
import data_filter
from measurement import Measurement
import matplotlib

matplotlib.use('TkAgg')


# u test.py su primjeri nekih poziva

'''
get_ax(figure)
get_fig(figure)
'''

'''

Pass data to Plot
1* give directly as
	list of measurements or
	1d list, np.array .... or
	2d list  np.array .... (array of points)
ex. Plot(data = [1, 2, 3, 4])
	Plot(data = [[1, 2], [1, 0], [3, 2]])
	----------------
2* specify machine and list of sensors to Plot
	Plot(machine = 'FL02') - plots all sensors of FL02
	Plot(machine = 'FL02', sensors = ['idle_wheel_V_eff', 'drive_wheel_a_max'])

additional arguments:
	figure	- label
	name	- give name to current data
	feature - 'rol-mean', 'rol-skew', 'rol-std'
			- this is used for plotting sensors or list of measurements
	window  - size of rolling window for rolling features (default is '10d' meaning 10 days)
	kind = 'scatter', 'hist', 'line', 'density' ...
	legend - True or False

	additional arguments for:
		* kind = 'scatter':
			s - size of points (ex. s = 10)
			marker - type of marker (ex. marker = 'x', marker = 'o', marker = 'v'...)
			color - self explanatory
		* kind = 'hist'
			bins - number of bins in histogram
			color - ...
		* kind = default or 'line'
			ls - linestyle (ex. ls = '--', ls = '-.')
			color ...
		* kind = 'hexbin'      used for visualizing density of 2d data (in someway similiar to scatter)
			gridsize - number of hex in row / column_names
		* kind = 'density'     visualizes histogram with line
		 	ls
			color

calls:
Plot(machine = 'FL03', feature = 'rol-mean')
Plot(machine = 'FL02', sensors = ['drive_motor_V_eff', 'drive_gear_V_eff'], feature = 'rol-skew')
Plot(data = [3, 2, 2.3, 3.1, 3.2, 1.2, 4, 5, 4.2], kind = 'hist', bins = 3)
Plot(data = [3, 2, 2.3, 3.1, 3.2, 1.2, 4, 5, 4.2], kind = 'density', ls = '--', name = 'function of distribution')
'''


'''
PlotCon
'''

manual_repair = data_filter.manual_repair

# Gets data from data folder

def PlotC(X, Y, Z):
	'''delta = 0.025
	x = np.arange(-3.0, 3.0, delta)
	y = np.arange(-2.0, 2.0, delta)
	X, Y = np.meshgrid(x, y)
	Z1 = np.exp(-X**2 - Y**2)
	Z2 = np.exp(-(X - 1)**2 - (Y - 1)**2)
	Z = (Z1 - Z2) * 2
	'''
	fig, ax = plt.subplots()
	CS = ax.contour(X, Y, Z)

	ax.clabel(CS, CS.levels, inline=True, fontsize=10)
	M.refresh()

def RollingMean(data, window = '10d'):
	orig = data.columns[0]
	feat = orig + ' - rolling mean'
	data[feat] = data[orig].rolling(window).mean()
	data.drop(columns = orig, inplace = True)

def RollingSkweness(data, window = '10d'):
	orig = data.columns[0]
	feat = orig + ' - rolling skew'
	data[feat] = data[orig].rolling(window).skew()
	data.drop(columns = orig, inplace = True)

def RollingStandardDeviation(data, window = '10d'):
	orig = data.columns[0]
	feat = orig + ' - rolling std'
	data[feat] = data[orig].rolling(window).std()
	data.drop(columns = orig, inplace = True)

features = {
	'basic'    : lambda x, y: None,
	'rol-mean' : RollingMean,
	'rol-skew' : RollingSkweness,
	'rol-std'  : RollingStandardDeviation
}

def ApplyFeature(data, feature, window):
	if len(data.columns) > 1:
		data.set_index(data.columns[0], inplace = True)
		features[feature](data, window)
		data.reset_index(inplace = True)
	else:
		features[feature](data, window)

def Convert_measurements(L, y = 'unknown'):
	res = pd.DataFrame(columns = ('timestamp', 'value'))

	data = []
	for m in L:
		row = {}
		row['timestamp'] = m['start_timestamp'].strip('"')
		row[y] = m.realvalue
		data.append(row)

	data = pd.DataFrame(data)
	data.timestamp = pd.to_datetime(data['timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
	data.set_index(['timestamp'], inplace = True)

	return data

# list of numbers
def Plot1d(to_plot, **kwargs):
	args = {k: v for k, v in {
		'ax' 		: M.get_ax(kwargs.get('figure', None)),
		'kind'		: kwargs.get('kind', 'scatter'),
		'color' 	: kwargs.get('color', None),
		's'     	: kwargs.get('s', None),
		'ls'     	: kwargs.get('ls', None),
		'marker'    : kwargs.get('marker', None),
		'bins'		: kwargs.get('bins', None),
		'legend' 	: kwargs.get('legend', None)
	}.items() if v is not None}

	feature = kwargs.get('feature', 'basic')
	window 	= kwargs.get('window', 10)
	fig 	= kwargs.get('figure', None)

	for data in to_plot:
		ApplyFeature(data, feature, window)
		line = ''
		if args['kind'] in ['density', 'hist']:
			data.plot(**args)
			line = 'data.plot(**args)'
		else:
			data['y'] = 0
			if not 's' in args:
				args['s'] = 30
			line = 'data.plot(x = data.columns[0], y = data.columns[1], **args)'
			ax = data.plot(x = data.columns[0], y = data.columns[1], **args)
			args['ax'] = ax
		if fig:
			M.addplot(fig, line, data, args)
	plt.show(block = False)

def Plot2d(to_plot, **kwargs):
	args = {k: v for k, v in {
		'ax' 		: M.get_ax(kwargs.get('figure', None)),
		'kind'		: kwargs.get('kind', 'scatter'),
		'color' 	: kwargs.get('color', None),
		's'     	: kwargs.get('s', None),
		'ls'     	: kwargs.get('ls', None),
		'marker'    : kwargs.get('marker', None),
		'gridsize'	: kwargs.get('gridsize', None),
		'legend' 	: kwargs.get('legend', None)
	}.items() if v is not None}

	feature = kwargs.get('feature', 'basic')
	window 	= kwargs.get('window', 10)
	fig 	= kwargs.get('figure', None)

	if args['kind'] == 'hexbin':
		if not 'gridsize' in args:
			args['gridsize'] = 15
	for data in to_plot:
		ApplyFeature(data, feature, window)
		line = 'data.plot(x = data.columns[0], y = data.columns[1],  **args)'
		ax = data.plot(x = data.columns[0], y = data.columns[1],  **args)
		if fig:
			M.addplot(fig, line, data, args)
		args['ax'] = ax

def PlotTime(to_plot, **kwargs):#show_repair = True, figure = None, name = 'unknown', feature = 'basic', window = '10d', ls = None):

	args = {k: v for k, v in {
		'ax' 		: M.get_ax(kwargs.get('figure', None)),
		's'     	: kwargs.get('s', None),
		'color' 	: kwargs.get('color', None),
		'kind'		: kwargs.get('kind', 'line'),
		'ls' 		: kwargs.get('ls', None),
		'legend' 	: kwargs.get('legend', None)
	}.items() if v is not None}

	feature = kwargs.get('feature', 'basic')
	window 	= kwargs.get('window', '10d')
	fig 	= kwargs.get('figure', None)

	for data in to_plot:
		ApplyFeature(data, feature, window)
		if args['kind'] == 'scatter':
			data.reset_index(inplace = True)
			args['x'] = data.columns[0]
			args['y'] = data.columns[1]
		ax = data.plot(**args)
		line = 'data.plot(**args)'
		if fig:
			M.addplot(fig, line, data, args)
		args['ax'] = ax

#repair = 'what machine'
#repair = 'FL01'

def Plot(data = [], machine = None, sensors = [], **kwargs):

	data = data.copy()


	to_plot = []
	datatype = None

	if machine:
		datatype = "TIME"
		if not len(sensors):
			for sensor in obrada.list_sensors[machine]:
				sensors.append(sensor)
		print('Plotting sensors...')
		for sensor in sensors:
			temp = []
			data_filter.filtered_data(temp, machine, sensor)
			temp = Convert_measurements(temp, f'{machine} - {sensor}')
			print(f'{machine} - {sensor}')
			to_plot.append(temp)
	elif len(data):
		name = kwargs.get('name', 'unknown')
		print('Plotting data...')
		if isinstance(data, list) and isinstance(data[0], Measurement):
			datatype = "TIME"
			to_plot.append(Convert_measurements(data, name))
		else:
			data = pd.DataFrame(data)
			if len(data.columns) == 1:
				data.columns = [name]
				datatype = '1d'
			elif len(data.columns):
				data.columns = ['x', name]
				datatype = '2d'
			else:
				print('Cannot recognize data type')
				return
			to_plot.append(data)
	else:
		print('There is no data to plot')

	if datatype == "TIME":
		PlotTime(to_plot, **kwargs)
	elif datatype == '1d':
		Plot1d(to_plot, **kwargs)
	elif datatype == '2d':
		Plot2d(to_plot, **kwargs)

	kind = kwargs.get('kind', None)
	if machine and kind != 'scatter':
		for when in manual_repair[machine]:
			plt.axvline(x=when, color="black", linestyle="--")

	M.refresh()

def ax(fig):
	return M.get_ax(fig)
def fig(fig):
	return M.get_fig(fig)

class OneFig:

	label = ''
	plot_history = []
	text_history = []

	def __init__(self, fig):
		self.label = fig
		self.plot_history = []
		self.text_history = []

	def addplot(self, line, data, args):
		self.plot_history.append([line, data.copy(), args.copy()])
	def addtext(self, text):
		line = 'ax.plt(x, y, text, transform = ax.transAxes, **args)'
	def load(self, ax):
		for line, data, args in self.plot_history:
			args['ax'] = ax
			eval(line)
		for text in self.text_history:
			args = {}
			x = .25
			y = .25
			#eval(line)

# fig - label
# figure - real Figure object

class Manager:
	fignum = {}
	figdata = {}

	def __init__(self):
		plt.close('all')

	def makefig(self, fig):
		L = [0] + plt.get_fignums()
		if not fig:
			fig = 1
			while fig in self.fignum:
				fig += 1
		self.figdata[fig] = OneFig(fig)
		self.fignum[fig] = L[-1] + 1

	def get_ax(self, fig):
		if self.fignum.get(fig, None) not in plt.get_fignums():
			self.makefig(fig)
			return None
		return plt.figure(self.fignum.get(fig, fig)).get_axes()[0]
	def get_fig(self, fig):
		if fig not in self.fignum:
			return None
		return plt.figure(self.fignum[fig])

	def addplot(self, fig, line, data, args):
		try:
			self.figdata[fig].addplot(line, data, args)
		except:
			print(f'Figure named {fig} does not exist.')

	def addtext(self, fig, text):
		try:
			self.figdata[fig].addtext(text)
		except:
			print(f'Figure named {fig} does not exist.')

	def load(self, fig, ax):
		try:
			self.figdata[fig].load(ax)
		except:
			print(f'Figure named {fig} does not exist.')

	def refresh(self):
		for title in self.fignum:
			self.get_fig(title).canvas.set_window_title(title)
		plt.show(block = False)

M = Manager()

def Merge(L):
	n = len(L)
	m = len(L[0])

	fig, axs = plt.subplots(n, m, tight_layout = True)
	for i in range(n):
		for j in range(m):
			if L[i][j] != 't':
 				M.load(L[i][j], axs[i, j])
			else:
				axs[i, j].axis('off')
	plt.show(block = False)

	return (fig, axs)


# -------------------------

# -------------------------
