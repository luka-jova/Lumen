import visual_test as vis
import data_filter as filter
import anomaly_detector as ad
import numpy as np
from numpy import inf
import estimator

##temporarily
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

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
#shell call:
#importlib.reload(estimator); importlib.reload(main); importlib.reload(main.estimator); e=estimator.Estimator("FL04"); main.run(e, start="2019-04-01", end="2019-05-01")

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
		out = e.category_diagnosis("a", details = details)
		print(out)
		
	if e.RUN_A_CATEGORIZATION and e.RUN_CATEGORIZATION_NEW_DATA:
		print("-------Categorization of acceleration for new data---------")
		new_data = {}
		load_data(new_data, e.machine_name, e.acc_sensor_list, start = start, end = end)
		e.new_data = new_data
		out = e.category_diagnosis("a", details = details)
		print(out)
		
	if e.RUN_V_CATEGORIZATION and e.RUN_CATEGORIZATION_ALL_DATA:
		print("-------Categorization of velocity for all data---------")
		new_data = {}
		load_data(new_data, e.machine_name, e.vel_sensor_list, start = 0, end = inf)
		e.new_data = new_data
		out = e.category_diagnosis("v", details = details)
		print(out)
	
	if e.RUN_V_CATEGORIZATION and e.RUN_CATEGORIZATION_NEW_DATA:
		print("-------Categorization of velocity for new data---------")
		new_data = {}
		load_data(new_data, e.machine_name, e.vel_sensor_list, start = start, end = end)
		e.new_data = new_data
		out = e.category_diagnosis("v", details = details)
		print(out)

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
		print(len(referent_data), len(new_data))
		print(start, end, e.REFERENT_LAST_N_DAYS)
		print(len(referent_data["FL04"]))
		mu, sigma2, new_data_mu, new_data_sigma2, good_cnt_d, outlier_cnt_d = e.compatibility_diagnosis(details = details, use_best_data = False)
		print(mu, sigma2, new_data_mu, new_data_sigma2, good_cnt_d, outlier_cnt_d, sep="\n-------------\n")
		
		with PdfPages('diagnosis.pdf') as pdf:
			plt.rc('text', usetex=True)
			num_columns = len(e.vel_sensor_list)
			fig, axes = plt.subplots(nrows=1, ncols=num_columns, figsize = (num_columns * 2, 5))
			fig.subplots_adjust(top=0.85)
			title = r"\noindent Compatibility check \newline start: " + filter.to_date(start) + ", end: " + filter.to_date(end) + r"\newline"
			title += " Referent data is last " + str(e.REFERENT_LAST_N_DAYS) + " days"
			fig.suptitle(title, fontsize=14, fontweight='bold')
			
			for ind, cur_sensor in enumerate(e.vel_sensor_list):
				ax = axes[ ind ]
				ax.axis([0, 10, 0, 10])
				display_compatibility_data(ax, cur_sensor, mu, sigma2, new_data_mu, new_data_sigma2, good_cnt_d, outlier_cnt_d)				

			pdf.savefig(fig)
			plt.close('all')
		print("pokrenuto\n" + str(plt.get_fignums()))
		
	
	if e.RUN_COMPATIBILITY_BEST_FIT:
		print("------Checking compatibility with best fit------------")
		new_data = {}
		load_data(new_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start, end = end)
		e.new_data = new_data
		e.compatibility_diagnosis(details = details, use_best_data = True)
		

def display_compatibility_data(ax, cur_sensor, mu_d, sigma2_d, new_data_mu_d, new_data_sigma2_d, good_cnt_d, outlier_cnt_d):
	disp_name = ' '.join(cur_sensor.split('_')[:2])
	disp_mu_ref = str(round(mu_d[ cur_sensor ].flat[ 0 ], 2))
	disp_std_ref = str(round(np.sqrt(sigma2_d[ cur_sensor ].flat[ 0 ]), 2))
	disp_var_ref = str(round(sigma2_d[ cur_sensor ].flat[ 0 ], 2))
	disp_mu_new = str(round(new_data_mu_d[ cur_sensor ].flat[ 0 ], 2))
	disp_std_new = str(round(np.sqrt(new_data_sigma2_d[ cur_sensor ].flat[ 0 ]), 2))
	disp_var_new = str(round(new_data_sigma2_d[ cur_sensor ].flat[ 0 ], 2))
	disp_good_cnt = str(good_cnt_d[ cur_sensor ])
	disp_all_cnt = str(good_cnt_d[ cur_sensor ] + outlier_cnt_d[ cur_sensor ])
	percentage = int(good_cnt_d[ cur_sensor ] / (good_cnt_d[ cur_sensor ] + outlier_cnt_d[ cur_sensor ]) * 100)
	disp_percentage = str(percentage) + "\%"
	disp_status = ""
	color = ""
	
	if percentage >= 90:
		color = "green"
		disp_status = "GOOD FIT"
	elif percentage >= 50:
		color = "yellow"
		disp_status = "PARTIAL FIT"
	else:
		color = "red"
		disp_status = "BAD FIT"
	
	
	ax.text(5, 9.5, disp_name, fontsize=10,  bbox={'facecolor': "grey", 'alpha': 0.5, 'pad': 10}, 
		horizontalalignment = "center", verticalalignment = "top")
	ax.text(0.5, 8, r'$\mu_{ref} = $ ' + disp_mu_ref, ha = 'left', va = 'center')
	ax.text(0.5, 7.5, r'$\sigma_{ref} = $ ' + disp_std_ref, ha = 'left', va = 'center')
	ax.text(0.5, 7, r'$\sigma_{ref}^{2} = $ ' + disp_var_ref, ha = 'left', va = 'center')	
	
	ax.text(0.5, 6, r'$\mu_{new} = $ ' + disp_mu_new, ha = 'left', va = 'center')
	ax.text(0.5, 5.5, r'$\sigma_{new} = $ ' + disp_std_new, ha = 'left', va = 'center')
	ax.text(0.5, 5, r'$\sigma_{new}^{2} = $ ' + disp_var_new, ha = 'left', va = 'center')	
	
	details = r"\noindent $good_{cnt} / all_{cnt}$\newline" + disp_good_cnt + " / " + disp_all_cnt + " = " + disp_percentage
	ax.text(0.5, 4, details, ha = 'left', va = 'top')	
	ax.text(5, 1, disp_status, fontsize=10,  bbox={'facecolor': color, 'alpha': 0.5, 'pad': 10}, 
		horizontalalignment = "center", verticalalignment = "bottom")
	
def load_data(new_data, machine_name, sensor_list, start, end):
	for cur_sensor in sensor_list:
		new_data[ cur_sensor ] = []
		filter.filtered_data(new_data[ cur_sensor ], machine_name, cur_sensor, start, None, end)


################################################################################NEPOTREBNO KASNIJE
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
