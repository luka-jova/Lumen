import visual_test as vis
import data_filter as filter
import anomaly_detector as ad
import numpy as np
from numpy import inf

CUR_MACHINE = "FL01"
CUR_SENSOR = "drive_gear_V_eff"

list_sensors = filter.list_sensors
list_machines = filter.list_machines

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


def estimate(start_train = 0, duration_train = None, end_train = inf, start_outlier = 0, duration_outlier = None, end_outlier = inf):
	global CUR_MACHINE, CUR_SENSOR, mu, Sigma2, epsilon, F1, estimated
	print("Estimating for:\n..Machine:", CUR_MACHINE, "\n..Sensor:", CUR_SENSOR)
	if CUR_MACHINE == "":
		print("Please select machine")
		return
	train_list = []
	outlier_list = []
	filter.filtered_data(train_list, CUR_MACHINE, CUR_SENSOR, start_train, duration_train, end_train)
	filter.filtered_data(outlier_list, CUR_MACHINE, CUR_SENSOR, start_outlier, duration_outlier, end_outlier)
	
	train_v = filter.measurements_to_numpy_vector(train_list)[:, None] #Making it transposed
	M_total = train_v.shape[ 0 ]
	M_train = int(M_total * 0.7)
	M_cvs_good = M_total - M_train
	M_cvs_outlier = len(outlier_list)
	
	perm = np.random.permutation(M_total)
	cvs_good_v = train_v[ perm[0:M_cvs_good] ]
	train_v = train_v[ perm[M_cvs_good:M_total] ]
	cvs_outlier_v = filter.measurements_to_numpy_vector(outlier_list)[:, None] #Making it transposed
	
	print("M_train", M_train, train_v.shape[ 0 ])	
	print("M_cvs_good", M_cvs_good, cvs_good_v.shape[ 0 ])
	print("M_cvs_outlier", M_cvs_outlier, cvs_outlier_v.shape[ 0 ])
	
	print("Plotting histogram of Train data, should resemble Gaussian")
	vis.Plot(train_v[:, 0], kind = 'density')
	
	mu, Sigma2 = ad.estimateMultivariateGaussian(train_v)
	estimated = True
	print("Estimation finished.", "Mu found:", mu, "Sigma2 found:", Sigma2, sep = "\n")
	
	y_cvs_all = np.hstack((np.zeros(M_cvs_good, dtype=bool), np.ones(M_cvs_outlier, dtype=bool)))
	p_cvs_all = ad.multivariateGaussian(np.vstack((cvs_good_v, cvs_outlier_v)), mu, Sigma2)
	
	print("Selecting epsilon...")
	epsilon, F1 = ad.selectThreshold(y_cvs_all, p_cvs_all)
	print("Best epsilon:", epsilon, "\nGives F1:", F1)
	
	#circle all found outliers
	cvs_outlier_cnt = sum(p_cvs_all[M_cvs_good:] < epsilon) #found outliers out of all outliers
	cvs_good_cnt = sum(p_cvs_all[0:M_cvs_good] >= epsilon) #found good measures out of all good measures
	print("Out of all outliers, we predicted ", cvs_outlier_cnt, "/", M_cvs_outlier, " to be outlier", sep="")
	print("Out of all good measurements, we predicted ", cvs_good_cnt, "/", M_cvs_good, " to be good", sep = "")	
	
