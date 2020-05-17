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
#import importlib; import main; import estimator;
#importlib.reload(estimator); importlib.reload(main); importlib.reload(main.estimator); e=estimator.Estimator("FL04"); main.run(e, start="2019-04-01", end="2019-05-01")
#GOOD EXAMPLE for last n days:
#importlib.reload(estimator); importlib.reload(main); importlib.reload(main.estimator); e=estimator.Estimator("FL01"); main.run(e, start = "2018-04-01", end="2019-05-01")

def run(e, details = True, mode = "Terminal", start = 0.0, end = 0.0):
	with PdfPages('diagnosis.pdf') as pdf:
		plt.rc('text', usetex=True)
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
		
		if e.RUN_COMPATIBILITY_LAST_WEEK:
			print("------Checking compatibility with last week-----------")
			referent_data = {}
			load_data(referent_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start - 7*24*60*60, end = start)
			e.referent_data = referent_data
			new_data = {}
			load_data(new_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start, end = end)
			e.new_data = new_data
			compatibility_pdfgen(pdf, e, "from " + filter.to_date(start) + " until " + filter.to_date(end), " last week", use_best_data = False)
		
		if e.RUN_COMPATIBILITY_LAST_N_DAYS:
			print("------Checking compatibility with last", e.REFERENT_LAST_N_DAYS, "days-----------")
			referent_data = {}
			load_data(referent_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start - e.REFERENT_LAST_N_DAYS*24*60*60, end = start)
			e.referent_data = referent_data
			new_data = {}
			load_data(new_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start, end = end)
			e.new_data = new_data
			compatibility_pdfgen(pdf, e, "from " + filter.to_date(start) + " until " + filter.to_date(end), " last " + str(e.REFERENT_LAST_N_DAYS) + " days")
		
		if e.RUN_COMPATIBILITY_BEST_FIT:
			print("------Checking compatibility with best fit------------")
			new_data = {}
			load_data(new_data, e.machine_name, e.vel_sensor_list + e.acc_sensor_list, start = start, end = end)
			e.new_data = new_data
			e.referent_data = {}
			compatibility_pdfgen(pdf, e, "from " + filter.to_date(start) + " until " + filter.to_date(end), " recommended distribution (from .config) ", use_best_data = True)

#estimator has to be loaded
def compatibility_pdfgen(pdf, e, new_data_stamp, referent_data_stamp, use_best_data = False):
	mu, sigma2, new_data_mu, new_data_sigma2, good_cnt_d, outlier_cnt_d = e.compatibility_diagnosis(details = True, use_best_data = use_best_data)
	
	###TITLE PAGE VELOCITY
	fig, ax = plt.subplots(nrows = 1, ncols = 1)
	ax.axis([0, 10, 0, 10])
	
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.xaxis.set_ticks_position('none')
	ax.yaxis.set_ticks_position('none')
	ax.text(5, 5, "Compatibility check for velocity sensors", ha = 'center', va = 'center', fontsize = 20)	
	ax.text(5, 4, "New data:" + new_data_stamp, ha = 'center', va = 'center', fontsize=10)
	ax.text(5, 3, "Referent data:" + referent_data_stamp, ha = 'center', va = 'center', fontsize=10)
	pdf.savefig(fig)
	plt.close("all")
		
	###MEASUREMENTS
	num_columns = len(e.vel_sensor_list)
	fig, axes = plt.subplots(nrows=1, ncols=num_columns, figsize = (num_columns * 2, 5))
	plt.tight_layout()
	fig.subplots_adjust(top=0.85)
	title = "Velocity sensors"
	fig.suptitle(title, fontsize=14, fontweight='bold')
	
	for ind, cur_sensor in enumerate(e.vel_sensor_list):
		ax = axes[ ind ]
		ax.axis([0, 10, 0, 10])
		
		ax.set_yticklabels([])
		ax.set_xticklabels([])
		ax.xaxis.set_ticks_position('none')
		ax.yaxis.set_ticks_position('none')
		display_compatibility_data(ax, cur_sensor, mu, sigma2, new_data_mu, new_data_sigma2, good_cnt_d, outlier_cnt_d)				

	pdf.savefig(fig)
	plt.close('all')
	
	###PLOTING DATA
	num_columns = 3
	fig, axes = plt.subplots(nrows=1, ncols=num_columns, figsize = (num_columns * 5, 5))
	fig.subplots_adjust(top=0.85)
	fig.subplots_adjust(right=0.95)
	fig.subplots_adjust(left=0.05)

	title = "Distribution for drive sensors (velocity)"
	fig.suptitle(title, fontsize=14, fontweight='bold')
	for ind, cur_sensor in enumerate(e.vel_sensor_list[:3]):
		ax = axes[ ind ]
		ax.set_title(" ".join(cur_sensor.split('_')[:2]))
		if cur_sensor in e.new_data and len(e.new_data[ cur_sensor ]) != 0:
			vis.Plot(filter.measurements_to_numpy_vector(e.new_data[ cur_sensor ]), kind = "density", name = "new", ax = ax)
		if cur_sensor in e.referent_data and len(e.referent_data[ cur_sensor ]) != 0:
			vis.Plot(filter.measurements_to_numpy_vector(e.referent_data[ cur_sensor ]), kind = "density", name = "referent", ax = ax)
	pdf.savefig(fig)
	plt.close("all")
	
###other sensors
	num_columns = 3
	fig, axes = plt.subplots(nrows=1, ncols=num_columns, figsize = (num_columns * 5, 5))
	fig.subplots_adjust(top=0.85)
	fig.subplots_adjust(right=0.95)
	fig.subplots_adjust(left=0.05)

	title = "Distribution for other sensors (velocity)"
	fig.suptitle(title, fontsize=14, fontweight='bold')
	for ind, cur_sensor in enumerate(e.vel_sensor_list[3:]):
		ax = axes[ ind ]
		ax.set_title(" ".join(cur_sensor.split('_')[:2]))
		if cur_sensor in e.new_data and len(e.new_data[ cur_sensor ]) != 0:
			vis.Plot(filter.measurements_to_numpy_vector(e.new_data[ cur_sensor ]), kind = "density", name = "new", ax = ax)
		if cur_sensor in e.referent_data and len(e.referent_data[ cur_sensor ]) != 0:
			vis.Plot(filter.measurements_to_numpy_vector(e.referent_data[ cur_sensor ]), kind = "density", name = "referent", ax = ax)
	pdf.savefig(fig)
	plt.close("all")
	
	###TITLE PAGE ACCELERATION
	fig, ax = plt.subplots(nrows = 1, ncols = 1)
	ax.axis([0, 10, 0, 10])
	
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.xaxis.set_ticks_position('none')
	ax.yaxis.set_ticks_position('none')
	ax.text(5, 5, "Compatibility check for acceleration sensors", ha = 'center', va = 'center', fontsize = 20)	
	ax.text(5, 4, "New data: " + new_data_stamp, ha = 'center', va = 'center', fontsize=10)
	ax.text(5, 3, "Referent data:" + referent_data_stamp, ha = 'center', va = 'center', fontsize=10)
	pdf.savefig(fig)
	plt.close("all")
		
	###MEASUREMENTS
	num_columns = len(e.acc_sensor_list)
	fig, axes = plt.subplots(nrows=1, ncols=num_columns, figsize = (num_columns * 2, 5))
	plt.tight_layout()
	fig.subplots_adjust(top=0.85)
	title = "Acceleration sensors"
	fig.suptitle(title, fontsize=14, fontweight='bold')
	
	for ind, cur_sensor in enumerate(e.acc_sensor_list):
		ax = axes[ ind ]
		ax.axis([0, 10, 0, 10])
		
		ax.set_yticklabels([])
		ax.set_xticklabels([])
		ax.xaxis.set_ticks_position('none')
		ax.yaxis.set_ticks_position('none')
		display_compatibility_data(ax, cur_sensor, mu, sigma2, new_data_mu, new_data_sigma2, good_cnt_d, outlier_cnt_d)				

	pdf.savefig(fig)
	plt.close('all')
	
	###PLOTING DATA
	num_columns = 3
	fig, axes = plt.subplots(nrows=1, ncols=num_columns, figsize = (num_columns * 5, 5))
	fig.subplots_adjust(top=0.85)
	fig.subplots_adjust(right=0.95)
	fig.subplots_adjust(left=0.05)

	title = "Distribution for drive sensors (acceleration)"
	fig.suptitle(title, fontsize=14, fontweight='bold')
	for ind, cur_sensor in enumerate(e.acc_sensor_list[:3]):
		ax = axes[ ind ]
		ax.set_title(" ".join(cur_sensor.split('_')[:2]))
		if cur_sensor in e.new_data and len(e.new_data[ cur_sensor ]) != 0:
			vis.Plot(filter.measurements_to_numpy_vector(e.new_data[ cur_sensor ]), kind = "density", name = "new", ax = ax)
		if cur_sensor in e.referent_data and len(e.referent_data[ cur_sensor ]) != 0:
			vis.Plot(filter.measurements_to_numpy_vector(e.referent_data[ cur_sensor ]), kind = "density", name = "referent", ax = ax)
	pdf.savefig(fig)
	plt.close("all")
	
###other sensors
	num_columns = 3
	fig, axes = plt.subplots(nrows=1, ncols=num_columns, figsize = (num_columns * 5, 5))
	fig.subplots_adjust(top=0.85)
	fig.subplots_adjust(right=0.95)
	fig.subplots_adjust(left=0.05)

	title = "Distribution for other sensors (acceleration)"
	fig.suptitle(title, fontsize=14, fontweight='bold')
	for ind, cur_sensor in enumerate(e.acc_sensor_list[3:]):
		ax = axes[ ind ]
		ax.set_title(" ".join(cur_sensor.split('_')[:2]))
		if cur_sensor in e.new_data and len(e.new_data[ cur_sensor ]) != 0:
			vis.Plot(filter.measurements_to_numpy_vector(e.new_data[ cur_sensor ]), kind = "density", name = "new", ax = ax)
		if cur_sensor in e.referent_data and len(e.referent_data[ cur_sensor ]) != 0:
			vis.Plot(filter.measurements_to_numpy_vector(e.referent_data[ cur_sensor ]), kind = "density", name = "referent", ax = ax)
	pdf.savefig(fig)
	plt.close("all")

def display_compatibility_data(ax, cur_sensor, mu_d, sigma2_d, new_data_mu_d, new_data_sigma2_d, good_cnt_d, outlier_cnt_d):
	###INSERT TEST DATA HERE###
	disp_name = ' '.join(cur_sensor.split('_')[:2])
	disp_mu_ref = " NA"
	disp_std_ref = " NA"
	disp_var_ref = " NA"
	disp_mu_new = " NA"
	disp_std_new = " NA"
	disp_var_new = " NA"
	disp_good_cnt = " NA"
	disp_all_cnt = " NA"
	disp_percentage = " NA"
	percentage = -1
	if cur_sensor in mu_d: 
		disp_mu_ref = str(round(mu_d[ cur_sensor ].flat[ 0 ], 2))
	if cur_sensor in sigma2_d:
		disp_std_ref = str(round(np.sqrt(sigma2_d[ cur_sensor ].flat[ 0 ]), 2))
		disp_var_ref = str(round(sigma2_d[ cur_sensor ].flat[ 0 ], 2))
	if cur_sensor in new_data_mu_d:
		disp_mu_new = str(round(new_data_mu_d[ cur_sensor ].flat[ 0 ], 2))
	if cur_sensor in new_data_sigma2_d:
		disp_std_new = str(round(np.sqrt(new_data_sigma2_d[ cur_sensor ].flat[ 0 ]), 2))
		disp_var_new = str(round(new_data_sigma2_d[ cur_sensor ].flat[ 0 ], 2))
	if cur_sensor in good_cnt_d and cur_sensor in outlier_cnt_d:
		disp_good_cnt = str(good_cnt_d[ cur_sensor ])
		disp_all_cnt = str(good_cnt_d[ cur_sensor ] + outlier_cnt_d[ cur_sensor ])
		percentage = int(good_cnt_d[ cur_sensor ] / (good_cnt_d[ cur_sensor ] + outlier_cnt_d[ cur_sensor ]) * 100)
		disp_percentage = str(percentage) + "\%"
	disp_status = ""
	color = ""
	
	if percentage == -1:
		disp_status = "NO DATA"
		color = "grey"
	elif percentage >= 90:
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
	ax.text(0.5, 8, r'$\mu_{ref} = $ ' + disp_mu_ref, ha = 'left', va = 'center', fontsize=10)
	ax.text(0.5, 7.5, r'$\sigma_{ref} = $ ' + disp_std_ref, ha = 'left', va = 'center', fontsize=10)
	ax.text(0.5, 7, r'$\sigma_{ref}^{2} = $ ' + disp_var_ref, ha = 'left', va = 'center', fontsize=10)	
	
	ax.text(0.5, 6, r'$\mu_{new} = $ ' + disp_mu_new, ha = 'left', va = 'center', fontsize=10)
	ax.text(0.5, 5.5, r'$\sigma_{new} = $ ' + disp_std_new, ha = 'left', va = 'center', fontsize=10)
	ax.text(0.5, 5, r'$\sigma_{new}^{2} = $ ' + disp_var_new, ha = 'left', va = 'center', fontsize=10)	
	
	details = r"\noindent $good_{cnt} / all_{cnt}$\newline" + disp_good_cnt + " / " + disp_all_cnt + " = " + disp_percentage
	ax.text(0.5, 4, details, ha = 'left', va = 'top', fontsize=10)	
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
