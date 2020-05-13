import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import obrada
import data_filter
from measurement import Measurement as M

manual_repair = {
	"FL01" : [
		'2018-11-13 0:0:0.0',
		'2019-02-08 0:0:0.0',
		'2018-02-12 0:0:0.0',
	],
	"FL02" : [
		'2019-04-02 0:0:0.0'
	],
	"FL03" : [
		'2019-04-02 0:0:0.0'
	],
	"FL04" : [],
	"FL05" : [],
	"FL06" : [],
	"FL07" : [
		'2019-04-02 0:0:0.0'
	]
}
# Gets data from data folder

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
	features[feature](data, window)

def Convert_dates(L, y = 'unknown'):
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
def PlotHisto(L, number_of_columns = 50):
	data = pd.DataFrame(columns = ['realvalue'])

	data = []
	for x in L:
		row = {}
		row['realvalue'] = x
		data.append(row)
	data = pd.DataFrame(data)

	data.plot(kind = 'hist', bins = number_of_columns)
	data.plot(kind = 'density')

	plt.show(block = False)

def Plot_data(machine = 'FL01', sensor = obrada.list_sensors['FL01'][2]):
	print(machine, sensor)

	filename = f"data/{machine}/{sensor}.csv"

	file = None
	try:
		file = open(filename, 'r', encoding = 'utf-8-sig')
	except:
		print('Failed to find data')
		return []

	column_names = file.readline().strip('\n').split(';')
	column_names = list(map(lambda s: s.strip('"'), column_names))

	data = pd.read_csv(file, sep = ';', names = column_names)

	x = 'start_timestamp'
	y = 'realvalue'

	data = data[[x, y]]
	data.start_timestamp = pd.to_datetime(data[x], format='%Y-%m-%d %H:%M:%S.%f')
	data.set_index([x], inplace = True)

	return data

def PlotSensor(machine = 'FL01', sensor = obrada.list_sensors['FL01'][0]):

	data = Plot_data(machine, sensor)
	if len(data) == 0:
		return

	data.plot()

	for when in manual_repair[machine]:
		plt.axvline(x = when, color = '0.2', ls = '--')

	plt.legend(['realvalue', 'manual_repair'])
	plt.show(block = False)

def PlotMachine(machine = 'FL01'):

	all_sensors = []
	try:
		all_sensors = obrada.list_sensors['machine']
	except:
		print('Cannot find machine')
		return

	data = {}
	for sensor in all_sensors:
		data[senor] = Plot_data(machine, sensor)

	ax = None

	for when in manual_repair[machine]:
		plt.axvline(x = when, color = '0.2', ls = '--')

	plt.legend(['realvalue', 'manual_repair'])
	plt.show(block = False)

temp = None

# data is list of Measurment-s
def Plot_feature(*, data = [], machine = 'FL01', senors = []):
	if len(data):
		PlotTime(data)

	data = Plot_data(machine, sensor)
	if len(data) == 0:
		return

	data['mean'] = data['realvalue'].rolling(window, min_periods = 1).mean()
	global temp
	if temp:
		temp = data['mean'].plot(ax = temp)
	else:
		temp = data['mean'].plot()

	for when in manual_repair[machine]:
		plt.axvline(x = when, color = '0.2', ls = '--')

	plt.legend(['rolling mean', 'manual_repair'])
	plt.show(block = False)

'''
Plots realvalue data in correspondance to time

examples
PlotTime(machine = 'FL02')
L := list of meausurement
PlotTime(data = L)
PlotTime(machine = 'FL03', sensors = ['lifting_motor_a_max','lifting_motor_V_eff'], feature = 'rol-mean')

'''


def PlotTime(*, data = [], machine = 'FL01', sensors = [], figure = None, kind = None, frmt = None, name = 'unknown', feature = 'basic', window = '10d'):
	to_plot = []

	if not len(data):
		if not len(sensors):
			for sensor in obrada.list_sensors[machine]:
				sensors.append(sensor)
		print('Plotting sensors...')
		for sensor in sensors:
			temp = []
			data_filter.filtered_data(temp, machine, sensor)
			temp = Convert_dates(temp, f'{machine} - {sensor}')
			print(f'{machine} - {sensor}')
			to_plot.append(temp)
	else:
		print('Plotting data...')
		to_plot.append(Convert_dates(data, name, feature))

	args = {k: v for k, v in {
		'ax' : M.get_ax(figure),
		'kind' : kind,
		'frmt' : frmt
	}.items() if v is not None}

	for df in to_plot:
		ApplyFeature(df, feature, window)
		ax = df.plot(**args)
		args['ax'] = ax

	M.refresh()
	print('Finished')

def Plot2d(data, x_min = 0, x_max = 0, y_min = 0, y_max = 0):
	x = [p[0] for p in data]
	y = [p[1] for p in data]

	plt.plot(x, y, 'ro')
	if x_min != x_max:
		plt.xlim(x_min, x_max)
	if y_min != y_max:
		plt.ylim(y_min, y_max)

	plt.show(block = False)

class Manager:
	def __init__(self):
		plt.close('all')
	def get_ax(self, fig):
		if fig not in plt.get_fignums():
			return None
		return plt.figure(fig).get_axes()[0]
	def refresh(self):
		plt.show(block = False)

M = Manager()
