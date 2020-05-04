import dataset_loader as dl
import measurement as ms
from random import shuffle
import generate_output as go
#import numpy as np
import os, os.path
#from scipy import stats

MAX_DIFF = 30
DATA_TREE_PATH = "data"

list_V_sensors = [
	"drive_gear_a_max",
	"drive_motor_a_max",
	"drive_wheel_a_max",
	"idle_wheel_a_max",
	"lifting_gear_a_max",
	"lifting_motor_a_max"
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

def load_shared_data():
  with open('prog_data.txt', 'r') as pd:
    path, ordering = pd.readline().strip().split(':')
    ordering = [int(i) for i in ordering.split(',')]
    shared_data[path] = ordering
    
def save_shared_data():
  with open('prog_data.txt', 'w') as pd:
    for key in shared_data:
      pd.write(':'.join([key, ','.join([str(i) for i in shared_data[key]])]))

def randomize_blocks(path):
  ms = []
  dl.load_measurements(path, ms)
  temp = separate_by_time(ms)
  shared_data[path] = list(range(len(temp)))
  shuffle(shared_data[path])

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
#	 key = sensor_name
#  val = list of time blocks for key, containing measurements 
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
	
shared_data = {}
path_measurements_map = {}

def get_measurements(path, keep_loaded):
    if path in path_measurements_map:
        if keep_loaded:
            return path_measurements_map[path]
        else:
            return path_measurements_map.pop(path)
    else:
        if keep_loaded:
            path_measurements_map[path] = []
            dl.load_measurements(path, path_measurements_map[path])
            return path_measurements_map[path]
        else:
            temp = []
            dl.load_measurements(path, temp)
            return temp

def get_sensor_csv(dir_path, acc, filename_contains = ""):
    if not dir_path.endswith('/'): dir_path += '/'
    files = os.listdir(dir_path)
    for p in files:
        if os.path.isfile(dir_path + p):
            if p.endswith('.csv') and filename_contains in p:
                acc.append(dir_path + p)
        else:
            acc.append([])
            get_sensor_csv(dir_path + p, acc[-1], filename_contains)

def find_correlations(paths, desired_corr_list, max_corr_time_dist, min_corr_coeff, keep_loaded):
	measurements_j = get_measurements(paths[0], keep_loaded)
	for i in range(len(paths) - 1):
		measurements_i = measurements_j
		for j in range(len(paths) - 1, i, -1):
		      measurements_j = get_measurements(paths[j], keep_loaded)
		      print("Correlating", paths[i], "and", paths[j])
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

		      corr_coeff, pvalue = stats.pearsonr(*datasets)
		      if min_corr_coeff < abs(corr_coeff):
		          print("############## IMPORTANT ###############")
		          desired_corr_list.append((corr_coeff, paths[i], paths[j]))
		      print("Correlation based on", len(datasets[0]), "corr_coeff =: ", corr_coeff)

if __name__ == "__main__":
	load_machine("FL01")
  #dl.split_into_attr_tree("data-full.csv", "data", ["machine_name", "sensor_type"])
  #randomize_blocks('data/FL01/drive_gear_a_max.csv')
  # dodati loadanje i spremanje poretka u file i iz njega (npr randomize provoditi samo na onima
  #dl.split_into_attr_tree("IoT_and_predictive_maintenance-full.csv", DATA_TREE_PATH, ["machine_name", "sensor_type"])
  #apaths, vpaths = [], []
  #get_sensor_csv(DATA_TREE_PATH, apaths, "a_max")
  #interesting_correlations = []
  #for machine_paths in apaths:
  #    find_correlations(machine_paths, interesting_correlations, 3, 0.7, True)
  #with open("corr.csv", 'w') as corr_file:
  #    corr_file.write('"corr_coeff";"path1";"path2"\n')
  #    for corr_coeff, path1, path2 in sorted(interesting_correlations):
  #        print(corr_coeff, path1, path2)
  #        corr_file.write(str(corr_coeff) + ';' + '"' + path1 + '"' + ';' + '"' + path2 + '"\n')
    # randomize_blocks('data/FL01/drive_gear_a_max.csv')
    # dodati loadanje i spremanje poretka u file i iz njega (npr randomize provoditi samo na onima
