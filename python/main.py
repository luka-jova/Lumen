import visual_test as vis
import data_filter as filter
import anomaly_detector as ad
from datetime import datetime as dt
import numpy as np
from numpy import inf
import estimator
from os import listdir

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
	if isinstance(start, str):
		start = filter.to_timestamp(start)
	if isinstance(end, str):
		end = filter.to_timestamp(end)
		
	pdfs = ests = [it for it in listdir(".") if it.endswith(".pdf")]
	filename = str(len(pdfs) + 1) + "_diagnosis_" + e.machine_name + "-" + filter.to_date_for_filename(start) + "-" + filter.to_date_for_filename(end) + ".pdf"
	
	with PdfPages(filename) as pdf:
		plt.rc('text', usetex=True)
		
		fig, ax = plt.subplots(nrows = 1, ncols = 1)
		ax.axis([0, 10, 0, 10])
		
		ax.set_yticklabels([])
		ax.set_xticklabels([])
		ax.xaxis.set_ticks_position('none')
		ax.yaxis.set_ticks_position('none')
		ax.text(5, 5, "Diagnosis for " + e.machine_name, ha = 'center', va = 'center', fontsize = 30)	
		pdf.savefig(fig)
		plt.close("all")
		
		if e.RUN_A_CATEGORIZATION and e.RUN_CATEGORIZATION_ALL_DATA:
			print("-------Categorization of acceleration for all data---------")
			new_data = {}
			load_data(new_data, e.machine_name, e.acc_sensor_list, start = 0, end = inf)
			e.new_data = new_data
			out = e.category_diagnosis("a", details = details)
			categorization_pdf('aa', e, out, start = 0, end = inf, pdf = pdf)
			plt.close("all")
			
		if e.RUN_V_CATEGORIZATION and e.RUN_CATEGORIZATION_ALL_DATA:
			print("-------Categorization of velocity for all data---------")
			new_data = {}
			load_data(new_data, e.machine_name, e.vel_sensor_list, start = 0, end = inf)
			e.new_data = new_data
			out = e.category_diagnosis("v", details = details)
			categorization_pdf('va', e, out, start = 0, end = inf, pdf = pdf)
			plt.close("all")
			
		if e.RUN_A_CATEGORIZATION and e.RUN_CATEGORIZATION_NEW_DATA:
			print("-------Categorization of acceleration for new data---------")
			new_data = {}
			load_data(new_data, e.machine_name, e.acc_sensor_list, start = start, end = end)
			e.new_data = new_data
			out = e.category_diagnosis("a", details = details)
			categorization_pdf('an', e, out, start, end, pdf)
			plt.close("all")
		
		if e.RUN_V_CATEGORIZATION and e.RUN_CATEGORIZATION_NEW_DATA:
			print("-------Categorization of velocity for new data---------")
			new_data = {}
			load_data(new_data, e.machine_name, e.vel_sensor_list, start = start, end = end)
			e.new_data = new_data
			out = e.category_diagnosis("v", details = details)
			categorization_pdf('vn', e, out, start, end, pdf)
			plt.close("all")
		
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
	
	print("Diagnosis exported to " + filename)

def title_page(pdf, display_list):
	fig, ax = plt.subplots(nrows = 1, ncols = 1)
	ax.axis([0, 10, 0, 10])
	
	ax.set_yticklabels([])
	ax.set_xticklabels([])
	ax.xaxis.set_ticks_position('none')
	ax.yaxis.set_ticks_position('none')
	for ind, disp_s in enumerate(display_list):
		if len(display_list) == 1:
			fontsize = 30
		elif ind == 0:
			fontsize = 20
		else:
			fontsize = 10
		ax.text(5, 5-ind, disp_s, ha = 'center', va = 'center', fontsize = fontsize)	
	pdf.savefig(fig)
	plt.close("all")

def no_data_figure(e, type, start, end):
	print('No data')

def categorization_axes(ax1, ax2, e, machine, cur_sensor, out, data, type):
	#fig.patch.set_visible(False)
	disp_machine = ' '.join(machine.split('_')[:])
	disp_sensor	 = ' '.join(cur_sensor.split('_')[:2])
	uk = sum(out)
	ax2.set_title
	if uk == 0:
		ax1.axis('off')
		ax2.axis([0, 10, 0, 10])
		ax2.set_title(disp_sensor, fontsize = 20)
		ax2.text(5, 5, 'No data', va = 'center', ha = 'center', fontsize = 30)
	else:
		if len(data) == 0:
			print("Error")
			return
		ax2.set_title(disp_sensor, fontsize = 20)
		vis.Plot(data = data, kind = 'scatter', s = 1, color = 'blue', ax = ax2, repair = machine, name = f"{type[0]} / {data[0].unit}")
		vis.Plot(data = data, feature = 'rol-mean', color = 'red', ax = ax2, name = disp_sensor)
		ax2.set_xlim([dt.fromtimestamp(data[0].start_timestamp), dt.fromtimestamp(data[-1].start_timestamp)])
		ax1.axis([0, 10, 0, 10])
		
		LIST = e.vel_classification
		if type[0] == 'a':
			LIST = e.acc_classification

		colors = ['green', 'yellow', 'orange', 'red']

		text = r'\noindent '
		for i, C in enumerate(LIST):
			text += f'{C.class_name}: ${out[i]} / {uk} = {int(round(out[i]/uk*100,0))}\%$'
			text += r' \newline '

		ind, category = e.classify(out, type[0])

		ax1.text(5, 5, text, ha = 'center', va = 'center', fontsize = 15)
		ax1.text(5, 1, category.class_name, fontsize=15,  bbox={'facecolor': colors[ind], 'alpha': 0.5, 'pad': 10},
			ha = "center", verticalalignment = "bottom")

		ymin, ymax = ax2.get_ylim()
		offset = 1000

		for i, C in enumerate(LIST):
			lo = C.min_val
			if i == 0:
				lo -= offset
			hi = C.max_val
			lo = max(lo, ymin - offset)
			hi = min(hi, ymax + offset)

			if lo != hi:
				ax2.axhspan(lo, hi, facecolor = colors[i], alpha=0.2)

		plt.xticks(rotation=45)
		ax2.set_ylim(top = ymax, bottom = ymin)
		ax1.axis('off')


def categorization_pdf(type, e, out, start, end, pdf):
	sensor_list = e.vel_sensor_list
	title = r"Velocity sensors"
	if type[0] == 'a':
		sensor_list = e.acc_sensor_list
		title = r"Acceleration sensors"
	if start == 0:
		stamp = "all data"
	else:
		stamp = f"from {filter.to_date(start)} to {filter.to_date(end)}"
	
	title_page(pdf, [r"Categorization of measurements", title, "Time interval: " + stamp])

	for sensor_block in [sensor_list[:3], sensor_list[3:]]:
		plt.close("all")
		fig, axes = plt.subplots(nrows = 2, ncols = 3, figsize = (15, 8))		
		#TODO iz nekog razloga ne radi suptitle, tj tekst se preklapa sa naslovom grafa
		axes[0][1].text(0.5, 1.15, title + " " + stamp, ha="center", va="bottom", transform = axes[0][1].transAxes, fontsize = 20)
		#fig.suptitle("dobar dan", fontsize=14, fontweight='bold')			
		for ind, cur_sensor in enumerate(sensor_block):
			cur_ax1 = axes[ 1 ][ ind ]
			cur_ax2 = axes[ 0 ][ ind ]
			data = []
			filter.filtered_data(data, e.machine_name, cur_sensor, start = start, end = end)
			categorization_axes(cur_ax1, cur_ax2, e, e.machine_name, cur_sensor, out[ cur_sensor ], data, type)	
		plt.tight_layout(w_pad=0.1)
		pdf.savefig(fig)


#estimator has to be loaded
def compatibility_pdfgen(pdf, e, new_data_stamp, referent_data_stamp, use_best_data = False):
	mu, sigma2, new_data_mu, new_data_sigma2, good_cnt_d, outlier_cnt_d = e.compatibility_diagnosis(details = True, use_best_data = use_best_data)
	
	###TITLE PAGE VELOCITY
	
	title_page(pdf, ["Compatibility check for velocity sensors", "New data:" + new_data_stamp,
		"Referent data:" + referent_data_stamp])
		
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
	
	title_page(pdf, ["Compatibility check for acceleration sensors", "New data:" + new_data_stamp,
		"Referent data:" + referent_data_stamp])

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
		percentage = int(round(good_cnt_d[ cur_sensor ] / (good_cnt_d[ cur_sensor ] + outlier_cnt_d[ cur_sensor ]) * 100,0))
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
