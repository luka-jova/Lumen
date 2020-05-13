import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('ggplot')
plt.close('all')
import obrada
import matplotlib

RECOMMENDED_MATPLOTLIB_BACKEND = "TkAgg"
if matplotlib.get_backend() != RECOMMENDED_MATPLOTLIB_BACKEND:
	print("Setting up backend to TkAgg")
	matplotlib.use(RECOMMENDED_MATPLOTLIB_BACKEND)


'''
	!!!
	User functions:
	Plot(machine, sensor) - plots machine with x-axis being start_timestamp
	Plot_rolling_mean(machine, sensor, window) - same but adds rolling mean
	Plot2d(matrix, xmin, xmax, ymin, ymax) - plots points
					....................
						 optional
'''
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

def Plot(machine = 'FL01', sensor = obrada.list_sensors['FL01'][0]):

	data = Plot_data(machine, sensor)
	if len(data) == 0:
		return

	data.plot()

	for when in manual_repair[machine]:
		plt.axvline(x = when, color = '0.2', ls = '--')

	plt.legend(['realvalue', 'manual_repair'])
	plt.show(block = False)

temp = None
#ako se nista ne pokaze samo pokreni komandu opet
# Plot rolling window mean of some machine and sensor
# Can plot multiple machines / sensors on same graph if called multiple times in a row
def Plot_rolling_mean(machine = 'FL01', sensor = obrada.list_sensors['FL01'][0], window = '10d'):

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
	date format in '%Y-%m-%d %H:%M:%S.%f'
	example:
	"2017-11-30" or
	"2019-10-25 23:02:03.5"
'''
def Trim_data(start_date, end_date, data):
	data = data[(start_date < data.index) & (data.index < end_date)]
	return data

# Displays distribution of realvalues in given date range for machine and sensor
def Distribution(start_date, end_date, machine = 'FL02', sensor = obrada.list_sensors['FL02'][0]):
	data = Trim_data(start_date, end_date, Plot_data(machine, sensor))
	if len(data) == 0:
		return

	# odjebi datume
	data.sort_values(by = ['realvalue'], inplace = True)
	data.reset_index(drop = True, inplace = True)

	data.plot(kind = 'density')
	data.plot(kind = 'hist', bins = 100)

	plt.show(block = False)

def Close():
	plt.close('all')

def Show():
	plt.show(block = False)

'''
	plots list of 2d points
	ex. data = [[1, 2], [3, 1], [2, 1]]
	can be called multiple times
	if window is not terminated old points will stay
'''


def Plot2d(data, x_min = 0, x_max = 0, y_min = 0, y_max = 0, args = 'xk'):
	x = data[:, 0]
	y = data[:, 1]
	if 'o' in args:
		plt.plot(x, y, args, mfc="none", markersize = 10)
	else:
		plt.plot(x, y, args)
	if x_min != x_max:
		plt.xlim(x_min, x_max)
	if y_min != y_max:
		plt.ylim(y_min, y_max)

	plt.show(block = False)

