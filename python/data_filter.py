from datetime import datetime as dt
from numpy import inf
import numpy as np
import dataset_loader as dl

def to_date(timestamp):
	return dt.fromtimestamp(timestamp).strftime("%Y-%m-%d")

def to_timestamp(s, is_interval = False):
	if is_interval:
		result = 0.
		if '-' in s:
			if ' ' in s:
				ymd = s.split()[0]
			else:
				ymd = s
			result += sum([float(it) * secs for it, secs in
							zip(ymd.split('-'), (31557600, 2629800, 86400))])
		if ':' in s:
			if ' ' in s:
				hms = s.split()[1]
			else:
				hms = s
			result += sum([float(it) * secs for it, secs in
							zip(hms.split(':'), (3600, 60, 1))])
		return result
	elif ' ' in s and '.' in s:
		return dt.strptime(s, '%Y-%m-%d %H:%M:%S.%f').timestamp()
	elif ' ' in s:
		return dt.strptime(s, '%Y-%m-%d %H:%M:%S').timestamp()
	elif '-' in s:
		return dt.strptime(s, '%Y-%m-%d').timestamp()
	elif ':' in s:
		return dt.strptime(s, '%H:%M:%S').timestamp()

def filtered_data(dest_list, machine, sensor, start = 0, duration = None, end = inf, invert = False, max_val = inf, min_val = -inf):
	"""Filters data from a machine's sensor inside of some interval

	Start, duration and end can be of different types:
	tuple (n, e) where n is int and e is int or float represents n-th
		measurement block, measurements inside blocks are no more than
		e seconds apart from each other
	str time in format "y-m-d H:M:S", "y-m-d" or "H:M:S"
	float number of seconds (timestamp is usually stored as number of seconds)
	int n-th measurement

	Parameters
	----------
	dest_list : list
		List in which the newly read measurements are appended
	machine : str
		The name of the machine
	sensor : str
		The name of the sensor in the machine
	start : tuple, str, float or int
		Start filling at that point, default value: 0
	duration : tuple, str, float or int
		Keep filling for this many points, default value: None
		combination (start, duration) will provide all measures in interval [first_after_start, first_after_start+duration]
	end : tuple, str, float or int
		Keep filling until you reach this point, default value: numpy.inf (float)
	invert : bool
		Invert selection
	max_val : float or int
		Maximum value of measurement's realvalue
	mix_val : float or int
		Minimum value of measurement's realvalue

	Only dest_list, machine and sensor arguments are mandatory.
	If duration is set, the 'end' argument is ignored

	Returns
	-------
	None

	Examples
	--------
	filtered_data(L, "FL01", "lifting_motor_V_eff", (25, 3), (35, 4), max_val=1.5)
	fills list L with data from machine FL01, sensor lifting_motor_V_eff, skips
	the first 24 blocks (startig times of two consecutive measurements in a block
	are no more than 3 seconds apart), and takes next 35 blocks but with different
	distance. Doesn't include measurements with realvalue > 1.5


	filtered_data(L, "FL01", "drive_gear_V_eff", 25, None, '2020-4-20', True)
	fills list L with data from machine FL01, sensor drive_gear_V_eff, takes the
	first 24 measurements and all the measurements after 20th of April 2020
	(date included)
	"""

	amsmf = AMSMFilter(start, duration, end, invert, max_val, min_val)
	get_measurements(dest_list, machine, sensor, predicate = amsmf.predicate)


# Here will get_measurements store measurements to prevent loading files multiple
# times (unless False is passed as keep_loaded argument of the function)
# measurements[machine] = {sensor : measurements_list}
# measurements[machine][sensor] = measurements_list
measurements = {}

# Fills dest_list with all measurements from machine's sensor.csv. By passing
# keep_loaded = True, loaded measurements will be kept in RAM to prevent loading
# from Hard Disk next time
# Assumes that the measurements are split into machine/sensor.csv inside
# dl.ATTR_TREE_PATH directory. If that's not the case, run dl.split_into_attr_tree
# function.
def get_measurements(dest_list, machine, sensor, keep_loaded = True, predicate = lambda m: True):
	global measurements
	if machine in measurements and sensor in measurements[machine]:
		dest_list.extend(filter(predicate, measurements[machine][sensor]))
		if not keep_loaded:
			del measurements[machine][sensor]
		return
	path = '/'.join((dl.ATTR_TREE_PATH, machine, sensor)).replace("//", '/') + ".csv"
	if keep_loaded:
		if machine not in measurements:
			measurements[machine] = {}
		if sensor not in measurements[machine]:
			measurements[machine][sensor] = []
		dl.load_measurements(path, measurements[machine][sensor])
		dest_list.extend(filter(predicate, measurements[machine][sensor]))
	else:
		dl.load_measurements(path, dest_list, predicate)

# removes reference to the loaded measurement list, allowing gc to free memory
def remove_measurements(machine, sensor):
	global measurements
	if machine in measurements and sensor in measurements[machine]:
		del measurements[machine][sensor]

# clears the measurements dict
def clear_all_measurements():
	global measurements
	for machine in measurements:
		measurements[machine].clear()
	measurements.clear()

def in_range(prev_timestamp, curr_timestamp, range_s):
	return curr_timestamp - prev_timestamp <= range_s

# A machine's sensor's measurement filter
class AMSMFilter:

	def __init__(self, start = 0, duration = None, end = inf, invert = False, max_val = inf, min_val = -inf):
		if type(start) is str:
			self.start = to_timestamp(start)
		else:
			self.start = start
		if type(duration) is str:
			self.duration = to_timestamp(duration, True)
		else:
			self.duration = duration
		if type(end) is str:
			self.end = to_timestamp(end)
		else:
			self.end = end
		self.invert = invert
		self.max_val = max_val
		self.min_val = min_val
		self.reset_counters()

	def reset_counters(self):
		self.n = 0 # number of processed blocks
		self.prev_timestamp = 0
		if type(self.start) is tuple:
			self.bs = 0 # number of processed blocks with start tuple's max distance
			self.prev_timestamp = min(self.prev_timestamp, -2 * self.start[1])
		if self.duration is None and type(self.end) is tuple:
			self.be = 0 # number of processed blocks with end tuple's max distance
			self.prev_timestamp = min(self.prev_timestamp, -2 * self.start[1])
		if type(self.duration) is tuple:
			self.ba = 0 # number of accepted blocks with duration tuple's max distance
			self.pat = -2 * self.duration[1] # previously accepted timestamp
		if type(self.duration) is float:
			self.fat = None # first accepted timestamp
		if self.duration is not None:
			self.na = 0 # number of accepted measurements

	def predicate(self, m):
		self.n += 1
		if type(self.start) is tuple:
			self.bs += (m.start_timestamp - self.prev_timestamp > self.start[1])
		if self.duration is None and type(self.end) is tuple:
			self.be += (m.start_timestamp - self.prev_timestamp > self.end[1])
		if m.realvalue <= self.max_val and m.realvalue >= self.min_val:
			if (type(self.start) is int  and self.n >= self.start
				or type(self.start) is float and m.start_timestamp >= self.start
				or type(self.start) is tuple and self.bs >= self.start[0]):
				if self.duration is None:
					result = (type(self.end) is int  and self.n <= self.end
						or type(self.end) is float and m.start_timestamp <= self.end
						or type(self.end) is tuple and self.be <= self.end[0])
					self.prev_timestamp = m.start_timestamp
					return result != self.invert
				else:
					result = (type(self.duration) is int and self.na + 1 <= self.duration
						or type(self.duration) is float and
							(self.fat is None or m.start_timestamp - self.fat <= self.duration)
						or type(self.duration) is tuple and
							self.ba + (m.start_timestamp - self.pat > self.duration[1]) <= self.duration[0])
					if result:
						if type(self.duration) is tuple:
							self.ba += (m.start_timestamp - self.pat > self.duration[1])
							self.pat = m.start_timestamp
						self.na += 1
						if type(self.duration) is float and self.fat is None:
							self.fat = m.start_timestamp
					self.prev_timestamp = m.start_timestamp
					return result != self.invert
		self.prev_timestamp = m.start_timestamp
		return self.invert

def measurements_to_numpy_vector(src_list):
	"""Creates numpy.ndarray containing measurement.realvalue values of all
	all elements in the source list.

	Parameters
	----------
	src_list : list containing only measurements objects
		source list

	Returns
	-------
	numpy.ndarray
	"""
	return np.array([it.realvalue for it in src_list])
	
manual_repair = {
	"FL01" : [
		'2018-11-13 0:0:0.0',
		'2019-02-08 0:0:0.0',
		'2019-02-14 0:0:0.0', ##chosen end date
	],
	"FL02" : [
		'2019-04-08 0:0:0.0' #end date
	],
	"FL03" : [
		'2019-04-08 0:0:0.0', #end date
		'2019-04-05 0:0:0.0'
	],
	"FL04" : [],
	"FL05" : [],
	"FL06" : [],
	"FL07" : [
		'2019-04-08 0:0:0.0'
	]
}

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

list_machines = ["FL01", "FL02", "FL03", "FL04", "FL05", "FL06", "FL07", "debug-machine"]

def getRepairs(machine_name):
	return manual_repairs[ machine_name ]

