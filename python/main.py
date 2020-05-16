import visual_test as vis
import data_filter as filter
import anomaly_detector as ad
import numpy as np
from numpy import inf
import estimator

list_sensors = filter.list_sensors
list_machines = filter.list_machines

'''
run function
UI calls this function with provided estimator
e - Estimator object that has all the configuration details:
	
	-what should be diagnosed
	ARGUMENTS:
		e - loaded Estimator object from .config file	
		start - float representing global time in seconds for the start of new_data
		end - float representing global time in seconds for the end of new_data
		mode - "Terminal" or "PDF" - representing the exporting mode
		showDetails - if True: show details for each operation, if False: don't
		 
'''

Messages = {

	"RUN_A_CATEGORIZATION": {}

}

def run(e, details = True, mode = "Terminal", start = 0.0, end = 0.0):
	
	if isinstance(start, str):
		start = filter.to_timestamp(start)
	if isinstance(end, str):
		end = filter.to_timestamp(end)
	
	if e.RUN_A_CATEGORIZATION and e.RUN_CATEGORIZATION_ALL_DATA:
		print("-------Categorization of acceleration for all data---------")
		new_data = {}
		load_data(new_data, e.machine_name, e.acc_sensor_list, start = 0, end = inf)
		e.new_data = new_data
		e.category_diagnosis("a", details = details)
		
	if e.RUN_A_CATEGORIZATION and e.RUN_CATEGORIZATION_NEW_DATA:
		print("-------Categorization of acceleration for new data---------")
		new_data = {}
		load_data(new_data, e.machine_name, e.acc_sensor_list, start = start, end = end)
		e.new_data = new_data
		e.category_diagnosis("a", details = details)
		
	if e.RUN_V_CATEGORIZATION and e.RUN_CATEGORIZATION_ALL_DATA:
		print("-------Categorization of velocity for all data---------")
		new_data = {}
		load_data(new_data, e.machine_name, e.vel_sensor_list, start = 0, end = inf)
		e.new_data = new_data
		e.category_diagnosis("v", details = details)
	
	if e.RUN_V_CATEGORIZATION and e.RUN_CATEGORIZATION_NEW_DATA:
		print("-------Categorization of velocity for new data---------")
		new_data = {}
		load_data(new_data, e.machine_name, e.vel_sensor_list, start = start, end = end)
		e.new_data = new_data
		e.category_diagnosis("v", details = details)

	if e.RUN_COMPATIBILITY_LAST_DAY:
		print("------Checking compatibility with last day-----------")
		referent_data = {}
		load_data(referent_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start - 24*60*60, end = start)
		e.referent_data = referent_data
		new_data = {}
		load_data(new_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start, end = end)
		e.new_data = new_data
		e.compatibility_diagnosis(details = details, use_best_data = False)
	
	if e.RUN_COMPATIBILITY_LAST_WEEK:
		print("------Checking compatibility with last week-----------")
		referent_data = {}
		load_data(referent_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start - 7*24*60*60, end = start)
		e.referent_data = referent_data
		new_data = {}
		load_data(new_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start, end = end)
		e.new_data = new_data
		e.compatibility_diagnosis(details = details, use_best_data = False)
	
	if e.RUN_COMPATIBILITY_LAST_N_DAYS:
		print("------Checking compatibility with last", e.REFERENT_LAST_N_DAYS, "days-----------")
		referent_data = {}
		load_data(referent_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start - e.REFERENT_LAST_N_DAYS*24*60*60, end = start)
		e.referent_data = referent_data
		new_data = {}
		load_data(new_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start, end = end)
		e.new_data = new_data
		e.compatibility_diagnosis(details = details, use_best_data = False)
	
	if e.RUN_COMPATIBILITY_BEST_FIT:
		print("------Checking compatibility with best fit------------")
		new_data = {}
		load_data(new_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start, end = end)
		e.new_data = new_data
		e.compatibility_diagnosis(details = details, use_best_data = True)
		
		

def load_data(new_data, machine_name, sensor_list, start, end):
	for cur_sensor in sensor_list:
		new_data[ cur_sensor ] = []
		filter.filtered_data(new_data[ cur_sensor ], machine_name, cur_sensor, start, None, end)


def 

#######NEPOTREBNO KASNIJE
CUR_MACHINE = "FL01"
CUR_SENSOR = "drive_gear_V_eff"

mu = 0
Sigma2 = []
epsilon = 0
F1 = 0
estimated = False

'''
Usage:
call select() function to select which machine and sensor you are about to use
-displaying functions
-estimate function
'''

def select(machine_name = "", sensor = ""):
	global CUR_MACHINE, CUR_SENSOR, mu, Sigma2, epsilon, F1, estimated, list_machines, list_sensors
	if machine_name == "":
		print("Select machine:")
		for ind, name in enumerate(list_machines):
			print("[", ind + 1, "] ", name, sep = "")
		ind = int(input())
		CUR_MACHINE = list_machines[ ind - 1 ]
		print("Select sensor:")
		for ind, name in enumerate(list_sensors[ CUR_MACHINE ]):
			print("[", ind + 1, "] ", name, sep = "")
		ind = int(input())
		CUR_SENSOR = list_sensors[ CUR_MACHINE ][ ind - 1 ]
	else:	
		CUR_MACHINE = machine_name
		CUR_SENSOR = sensor
	mu = 0
	Sigma2 = []
	F1 = 0
	estimated = False
	print("Selected:", CUR_MACHINE, CUR_SENSOR)

def dispSelectedInfo():
	global CUR_MACHINE, CUR_SENSOR, mu, Sigma2, epsilon, F1, estimated
	print("Selected ", CUR_MACHINE, CUR_SENSOR)	
		
def plotAllMeasurementsTimeline():
	global CUR_MACHINE, CUR_SENSOR, mu, Sigma2, epsilon, F1, estimated
	dispSelectedInfo()
	vis.Plot(machine = CUR_MACHINE, sensors = [CUR_SENSOR])

def plotMeasurementsDistribution(start = 0, duration = None, end = inf):
	global CUR_MACHINE, CUR_SENSOR, mu, Sigma2, epsilon, F1, estimated
	meas_list = []
	dispSelectedInfo()
	filter.filtered_data(meas_list, CUR_MACHINE, CUR_SENSOR, start, duration, end)
	meas_v = filter.measurements_to_numpy_vector(meas_list)
	vis.Plot(meas_v, kind = 'hist', bins = 100)


###EXAMPLE FUNCTIONS
def run_category_diagnosis():
	print("Please select machine to be category diagnosed and sensor to be plotted")
	select()
	plotAllMeasurementsTimeline()
	estim = estimator.Estimator(CUR_MACHINE)
	new_data = {}
	for cur_sensor in list_sensors[ CUR_MACHINE ]:
		new_data[ cur_sensor ] = []
		filter.filtered_data(new_data[ cur_sensor ], CUR_MACHINE, cur_sensor)
	estim.new_data = new_data
	estim.category_diagnosis("v")
	estim.category_diagnosis("a")
	
def run_compatibility_diagnosis():
	print("Please select machine to be compatibility diagnosed and sensor to be plotted")
	select()
	plotAllMeasurementsTimeline()
	estim = estimator.Estimator(CUR_MACHINE)
	new_data = {}
	referent_data = {}
	for cur_sensor in list_sensors[ CUR_MACHINE ]:
		new_data[ cur_sensor ] = []
		filter.filtered_data(new_data[ cur_sensor ], CUR_MACHINE, cur_sensor, start = "2019-03-15", end = "2019-04-01")
		referent_data[ cur_sensor ] = []
		filter.filtered_data(referent_data[ cur_sensor ], CUR_MACHINE, cur_sensor, start = "2019-06-01", end = "2019-07-01")
		
	vis.Plot(filter.measurements_to_numpy_vector(referent_data[ CUR_SENSOR ]), kind = "density")
	vis.Plot(filter.measurements_to_numpy_vector(new_data[ CUR_SENSOR ]), kind = "density")
	estim.new_data = new_data
	estim.referent_data = referent_data
	estim.compatibility_diagnosis(use_best_data = False)
	
if __name__ == "__main__":
	#run_velocity_diagnosis()
	run()
