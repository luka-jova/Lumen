import dataset_loader as dl
from data_filter import get_measurements
import measurement as ms
from random import shuffle
from numpy import corrcoef
import generate_output as go
import os, os.path

MAX_DIFF = 30
DATA_TREE_PATH = "data"

list_V_sensors = [
	"drive_gear_V_eff",
	"drive_motor_V_eff",
	"drive_wheel_V_eff",
	"idle_wheel_V_eff",
	"lifting_gear_V_eff",
	"lifting_motor_V_eff"
]


list_a_sensors = [
	"drive_gear_a_max",
	"drive_motor_a_max",
	"drive_wheel_a_max",
	"idle_wheel_a_max",
	"lifting_gear_a_max",
	"lifting_motor_a_max"
]

list_debug_sensors = [
	"drive_gear_V_eff",
	"drive_wheel_V_eff"
]

list_sensors = {
	"FL01": list_V_sensors + list_a_sensors,
	"FL02": list_V_sensors + list_a_sensors,
	"FL03": list_V_sensors + list_a_sensors,
	"FL04": list_V_sensors + list_a_sensors,
	"FL05": list_V_sensors + list_a_sensors,
	"FL06": list_V_sensors + list_a_sensors,
	"FL07": list_V_sensors + list_a_sensors,
	"debug-machine": list_debug_sensors
}

MAX_DIFF = 60
# max_diff is maximum distance between starting time of
# two measurements that can be in the same batch (in seconds)
def separate_by_time(measurements_list, max_diff = MAX_DIFF):
	batches = []
	previous_timestamp = -max_diff - 1
	for measurement in measurements_list:
		if measurement.start_timestamp - previous_timestamp > max_diff:
			batches.append([])
		previous_timestamp = measurement.start_timestamp
		batches[-1].append(measurement)
	return batches

#display function for checking time compatibility for time blocks between different sensors
def check_time_compatibility(machine_name, sensor_list):
	for cur_sensor in sensor_list:
		if not cur_sensor in sensor_data:
			load_sensor(machine_name, cur_sensor)
	for i in range(10):
		for cur_sensor in sensor_list:
			print(sensor_data[ cur_sensor ][ i ][ 0 ].start_timestamp, sensor_data[ cur_sensor ][ i ][ -1 ].start_timestamp, sep = " - ")
		print("---")
	for cur_sensor in sensor_list:
		print(len(sensor_data[ cur_sensor ]))

#sensor_data is a dictionary where
#	key = sensor_name
#	val = list of time blocks for key, containing measurements
sensor_data = {}

#load all eff_sensors for machine_name
def load_machine(machine_name):
	for cur_sensor in list_sensors[ machine_name ]:
		load_sensor(machine_name, cur_sensor)

#load sensor_name for machine_name in sensor_data
def load_sensor(machine_name, sensor_name):
	tmp = []
	cur_path = "data/" + machine_name + "/" + sensor_name + ".csv"
	dl.load_measurements(cur_path, tmp)
	sensor_data[ sensor_name ] = separate_by_time(tmp)

#debug data
def load_debug_data():
	load_sensor("debug-machine", "drive_gear_V_eff")
	load_sensor("debug-machine", "drive_wheel_V_eff")

#export a matrix data to csv file called machine_name + filename
def export_to_csv(machine_name, filename, data):
	with open(machine_name + filename + ".csv", 'w') as pd:
		for cur_row in data:
			pd.write(','.join([str(i) for i in cur_row]))
			pd.write("\n")

#it is sufficient to call this function export_data_for_machine with a machine_name and it will:
#1) load data for the machine_name
#2) separate all sensors into timeblocks
#3) synchronise timeblocks by ignoring the dangling ones (similiar to sweep line for now)
#4) take effective (average for now) value for each timeblock
#5) export all data to csv file where each row consists of: [start_timestamp end_timestamp eff_val1 eff_val2 ...]
###where eff_vali represents effective value for i-th sensor in time interval [start_timestamp, end_timestamp]
#Result: .csv file with data for machine_name, prints number of ignored timeblocks
def export_data_for_machine(machine_name):
	if machine_name == "debug-machine":
		load_debug_data()
	else:
		load_machine(machine_name)
	#machine is now loaded, all its sensors are loaded in sensor_data dictionary

	output_data = []

	print("Ignored timeblocks:", go.generate_output_data(sensor_data, list_sensors[ machine_name ], output_data))
	#generate_output has loaded the list output_data

	print("Timeblocks loaded:", len(output_data))
	export_to_csv(machine_name, "-all-sensors", output_data)

def find_pearson_correlations(machine, sensors, desired_corr_list, max_corr_time_dist, min_corr_coeff):
	"""Calculates linear (Pearson's) correlation between pairs of sensors on a machine
	
	Parameters
	----------
	machine : str
		machine for which the correlations are calculated
	sensors : list[str]
		names of sensors whose correlation is calculated
	desired_corr_list : list
		list in which are stored tuples (coeff, machine, sensor1, sensor2, number of entries)
		where abs(coeff) > min_corr_coeff
	max_corr_time_dist : int or float
		maximum time difference between measurements of same index in sample
	min_corr_coef : float
		value in range [0, 1], determines high correleation (what will be stored in
		desired_corr_list)
		
	Returns
	-------
	None
	
	Example
	-------
	# Determines correlation between all sensors for each machine, saves results
	# whose absolute value of correlation coefficient is higher than 0.85 in csv file
	data = []
	for machine in list_sensors:
		if "debug" in machine: continue
		find_pearson_correlations(machine, list_sensors[machine], data, 3, 0.85)
	data.sort()
	with open("pearson.csv", 'w', encoding="utf-8") as fout:
		fout.write("Coefficient;machine;sensor1;sensor2;number of entries\n")
		fout.write('\n'.join([';'.join([str(cell) for cell in line]) for line in data]))
	"""
	measurements_j = []
	get_measurements(measurements_j, machine, sensors[0])
	for i in range(len(sensors) - 1):
		measurements_i = measurements_j
		for j in range(len(sensors) - 1, i, -1):
			measurements_j = []
			get_measurements(measurements_j, machine, sensors[j])
			print("\nCorrelating", sensors[i], "and", sensors[j], "from", machine)
			datasets = [[], []]
			k, l = 0, 0
			while k < len(measurements_i) and l < len(measurements_j):
				dist = measurements_i[k].end_timestamp - measurements_j[l].end_timestamp
				if abs(dist) < max_corr_time_dist:
					datasets[0].append(measurements_i[k].realvalue)
					datasets[1].append(measurements_j[l].realvalue)
					k += 1
					l += 1
				elif dist < 0:
					k += 1
				else:
					l += 1
			if len(datasets[0]) < 3:
				print("Not enough data to correlate")
				continue

			corr_coeff = corrcoef(*datasets)[0][1]
			if min_corr_coeff < abs(corr_coeff):
				print("############## HIGH CORRELATION ###############")
				desired_corr_list.append((corr_coeff, machine, sensors[i], sensors[j], len(datasets[0])))
			print("Correlation based on", len(datasets[0]), "corr_coeff =: ", corr_coeff)
		

if __name__ == "__main__":
	load_machine("FL01")
	
