import dataset_loader as dl
import measurement as ms
from random import shuffle
import generate_output as go

MAX_DIFF = 60

list_eff_sensors = [
	"drive_gear_V_eff",
	"drive_motor_V_eff",
	"drive_wheel_V_eff",
	"idle_wheel_V_eff",
	"lifting_gear_V_eff",
	"lifting_motor_V_eff",
]	

list_debug_sensors = [
	"drive_gear_V_eff",
	"drive_wheel_V_eff"
]

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
	for cur_sensor in list_eff_sensors:
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
	
	if machine_name == "debug-machine":
		print("Ignored timeblocks:", go.generate_output_data(sensor_data, list_debug_sensors, output_data))
	else:
		print("Ignored timeblocks:", go.generate_output_data(sensor_data, list_eff_sensors, output_data))
	#generate_output now has output_data loaded
	
	print("Timeblocks loaded:", len(output_data))
	export_to_csv(machine_name, "-all-sensors", output_data)
	
shared_data = {}

if __name__ == "__main__":
	load_machine("FL01")
	#check_time_compatibility("FL01", list_eff_sensors)
  #dl.split_into_attr_tree("data-full.csv", "data", ["machine_name", "sensor_type"])
  #randomize_blocks('data/FL01/drive_gear_a_max.csv')
  # dodati loadanje i spremanje poretka u file i iz njega (npr randomize provoditi samo na onima

