import data_filter as df
import dataset_loader as dl
import variables_loader as vl
from estimator import Estimator
import main
from os import listdir
import os.path
from sys import exit

try: # importing now to avoid nasty surprises later
	import matplotlib
	import pandas
	import numpy
except:
	print("Please make sure matplotlib, pandas and numpy modules are installed.")
	exit()


PROMPT = '>'

# end_ts is upper bound of the interval that can be input by user
def input_time_interval(end_ts):
	interval_options = [
		"last 1 day",
		"last n days",
		"last 1 week",
		"last n weeks",
		"all data",
		"enter custom time intervals",
	]
	interval_option = select("Select time interval for analysis:", interval_options)
	if interval_option == 6:
		print("Please enter start time in format \"y-m-d\" or \"y-m-d H:M:S\"")
		start_ts = input_date()
		print("Please enter end time")
		end_ts = input_date()
		if end_ts < start_ts: end_ts, start_ts = start_ts, end_ts
	elif interval_option == 5:
		start_ts = 0.0
	else:
		if interval_option in (2, 4):
			print("Enter n:")
			n = input_int(2048)
		else:
			n = 1
		if interval_option < 3:
			start_ts = end_ts - n * (24 * 3600.0)
		else:
			start_ts = end_ts - n * (7 * 24 * 3600.0)
	return start_ts, end_ts

def input_date():
	timestamp = None
	while timestamp is None:
		try:
			timestamp = df.to_timestamp(input(PROMPT))
		except KeyboardInterrupt:
			exit()
		except:
			print(
				"Error! Please enter a time in format \"y-m-d\" or \"y-m-d H:M:S\""
			)
	return timestamp

def input_int(entries_count):
	selected = None
	while selected is None:
		try:
			selected = int(input(PROMPT))
			if selected not in range(1, entries_count + 1):
				selected = None
				raise ValueError
		except KeyboardInterrupt:
			exit()
		except:
			print(
				"Error! Please enter an integer in range [1, " + str(entries_count) + "]"
			)
	return selected
	
def select(hint, options):
	print(hint)
	for i, option in enumerate(options):
		print(i+1, ") ", str(option), sep = "")
	return input_int(len(options))

def welcome_screen():
	options = [
		"Run diagnosis",
		"Add data"
	]
	run = (
		run_diagnosis_screen,
		add_data_screen
	)
	while True:
		run[select("Welcome! Select an action.", options) - 1]()

def run_diagnosis_screen():
	
	# EXPORT DETAILS PROMPT
	export = select("How do you want diagnosis to be exported?", ["PDF", "In terminal"])
	export = ("PDF", "Terminal")[export - 1] # convert to correct argument for main.run()
	
	# SELECTING ESTIMATOR CONFIGURATION
	ext = "config" # file extension without leading '.'
	CONFIG_DIR_PATH = "config/"
	config_confirmed = False
	while not config_confirmed:
		ests = [] # every time a config is rejected, load again so user can copy in meantime
		while not (os.path.isdir(CONFIG_DIR_PATH) and ests):
			while not os.path.isdir(CONFIG_DIR_PATH):
				print("Please enter the name of config files' directory")
				CONFIG_DIR_PATH = input(PROMPT)
			ests = [it[:-len(ext) - 1] for it in listdir(CONFIG_DIR_PATH) if it.endswith(ext)]
		est = select("Please select estimator:", ests)
		print("Settings for estimator", ests[est - 1])
		if not CONFIG_DIR_PATH.endswith('/'): CONFIG_DIR_PATH += '/'
		file_path = CONFIG_DIR_PATH + ests[est - 1] + '.' + ext
		with open(file_path, 'r', encoding="utf-8") as config_file:
			print(config_file.read())
		config_confirmed = select("\nTake this estimator?", ["Yes", "No"]) == 1
	
	# PRINT DETAILS PROMPT
	verbose = select("Show details?", ["Yes, show details", "No"]) == 1
	
	# SELECTING MACHINE
	machines = [it for it in df.list_machines if "debug" not in it]
	machine = machines[select("Select machine:", machines) - 1]
	
	# LOADING MEASUREMENTS, FINDING THE LAST TIMESTAMP
	print("Loading the measurements, please wait.")
	try:
		end_ts = 0 # last timestamp in dataset
		for sensor in df.list_sensors[machine]:
				temp = []
				df.get_measurements(temp, machine, sensor)
				end_ts = max(temp[-1].end_timestamp, end_ts)	
	except:
		print("Error loading files. Make sure the directory structure is correct" )
		exit()
	end_ts = int(end_ts) - end_ts % (3600*24) + 3600.0 * 24
	print()
		
	# LOADING ESTIMATOR CONFIGURATION
	estimator = Estimator(machine)
	vl.load_estimator(file_path, estimator)
	
	# SELECTING INTERVAL
	start_ts, end_ts = input_time_interval(end_ts)
	print(vars(estimator), start_ts, end_ts, export, verbose)
	main.run(estimator, verbose, export, start_ts, end_ts)

def add_data_screen():
	print("Please enter path to the file with all measurements.")
	while True:
		try:
			src_path = input(PROMPT)
			if not os.path.isfile(src_path) or not src_path.endswith('csv'):
				raise IOError
			dl.split_into_attr_tree(src_path, dl.ATTR_TREE_PATH, ["machine_name", "sensor_type"], True)
			break
		except KeyboardInterrupt:
			exit()
		except:
			print("Error loading the file, please try again.")

if __name__ == "__main__":
	welcome_screen()

