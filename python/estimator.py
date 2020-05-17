from numpy import inf
import numpy as np
from measurement import Measurement
import anomaly_detector as ad
import data_filter as filter

class Classification:
	def __init__(self, class_name = "", min_val = -inf, max_val = inf, color = None, unit = ""):
		self.class_name = class_name
		self.min_val = min_val
		self.max_val = max_val
		self.color = color
		self.unit = unit

class Estimator:
	####Dictionaries where key=sensor_name, val = list of Measurement objects
	new_data = {}
	referent_data = {}
	#######
	
	'''
	The next data should be loaded from .config file and not changed after the creation of estimator object
	
	Complex structures:
		best_mu -> dictionary where key=sensor_name, val = numpy row vector with one element
		best_sigma2 -> dictionary where key=sensor_name, val = numpy row vector with one element
		
		vel_classification
		acc_classification
		
	Booleans:
		RUN_V_CATEGORIZATION = True
		RUN_A_CATEGORIZATION = True
		RUN_CATEGORIZATION_NEW_DATA = True
		RUN_CATEGORIZATION_ALL_DATA = True	
		RUN_COMPATIBILITY_LAST_DAY = True 
		RUN_COMPATIBILITY_LAST_WEEK = True
		RUN_COMPATIBILITY_LAST_N_DAYS = True
		RUN_COMPATIBILITY_BEST_FIT = True
	
	Integers:
		REFERENT_LAST_N_DAYS = 30
	'''
	
	best_mu = {
		"lifting_motor_a_max": np.array([100.4])
	}
	best_sigma2 = {
		"lifting_motor_a_max": np.array([1298708.6737446])	
	}
	
	machine_name = ""
	acc_sensor_list = []
	vel_sensor_list = []
	
	
	###ISO 10816 classification for Class III - Large Rigid Foundations
	#this may me modified - e.x. to Class II
	vel_classification = [
		Classification(class_name = "Good", min_val = 0, max_val = 2.8, color = "g", unit = "mm/s"),
		Classification(class_name = "Satisfactory", min_val = 2.8, max_val = 7.1, color = "c", unit = "mm/s"),
		Classification(class_name = "Unsatisfactory", min_val = 7.1, max_val = 18.0, color = "y", unit = "mm/s"),
		Classification(class_name = "Unacceptable", min_val = 18.0, max_val = inf, color = "r", unit = "mm/s")		
	]
	
	##Choose range...
	acc_classification = [
		#Classification(class_name = "Good", min_val = 0, max_val = 1000, color = "g", unit = "mg"),
		#Classification(class_name = "Satisfactory", min_val = 1000, max_val = 5000, color = "c", unit = "mg"),
		#Classification(class_name = "Unsatisfactory", min_val = 5000, max_val = 10000, color = "y", unit = "mg"),
		#Classification(class_name = "Unacceptable", min_val = 10000, max_val = inf, color = "r", unit = "mg")		
	
		Classification(class_name = "Brado", min_val = 0, max_val = 500, color = "g", unit = "mg"),
		Classification(class_name = "Oke", min_val = 500, max_val = 1000, color = "c", unit = "mg"),
		Classification(class_name = "A_ono", min_val = 1000, max_val = 10000, color = "y", unit = "mg"),
		Classification(class_name = "Lose", min_val = 10000, max_val = inf, color = "r", unit = "mg")		
	]
	
	'''
	###################
	#DIAGNOSIS DETAILS#
	###################
	'''
	RUN_V_CATEGORIZATION = False
	RUN_A_CATEGORIZATION = False
	RUN_CATEGORIZATION_NEW_DATA = False
	RUN_CATEGORIZATION_ALL_DATA = False
	
	RUN_COMPATIBILITY_LAST_DAY = False 
	#if new_data is in intervl [start, end], then referent_data will become [start - 24:00:00, end - 24:00:00]
	RUN_COMPATIBILITY_LAST_WEEK = False
	#if new_data is in intervl [start, end], then referent_data will become [start - 24:00:00 * 7, end - 24:00:00 * 7]
	RUN_COMPATIBILITY_LAST_N_DAYS = False
	REFERENT_LAST_N_DAYS = 100
	#if new_data is in intervl [start, end], then referent_data will become [start - 24:00:00 * REFERENT_LAST_N_DAYS, end - 24:00:00 * REFERENT_LAST_N_DAYS]
	
	RUN_COMPATIBILITY_BEST_FIT = True
	#Try fitting new_data to Gaussian distribution provided with (best_mu, best_sigma2)
	
	FIND_MIN_MEAN = True
	MIN_MEAN_WINDOW = 14 
	#Find minimum rolling mean value. Rolling mean has MIN_MEAN_WINDOW DAYS of window
	
	#
		
	'''
	##########################
	#END of DIAGNOSIS DETAILS#
	##########################
	'''
	
	def __init__(self,  machine_name, acc_sensor_list = filter.list_a_sensors, vel_sensor_list = filter.list_V_sensors, new_data = {}, referent_data = {}):
		self.machine_name = machine_name
		self.acc_sensor_list = acc_sensor_list.copy()
		self.vel_sensor_list = vel_sensor_list.copy()
		self.new_data = new_data.copy()
		self.referent_data = referent_data.copy()
	
	'''
	returns (index, Classification)
	input can be:
		a) Measurement 
			-> in this case it classifies a single Measurement in vel_classification categories
		b) list which count of how many measures there are for each category in vel_classification 
			-> in this case it classifies the whole set of measurements
	'''
	def classify(self, data, meas_type):
		if meas_type not in ["a", "v"]:
				print("measurement type is not compatibile")
				return(0, None)
			
		if isinstance(data, Measurement):
			cur_meas = data
			if meas_type == "v":
				for i, cur_clas in enumerate(self.vel_classification):
					if cur_meas.realvalue >= cur_clas.min_val and cur_meas.realvalue < cur_clas.max_val:
						return (i, cur_clas)
			elif meas_type == "a":
				for i, cur_clas in enumerate(self.acc_classification):
					if cur_meas.realvalue >= cur_clas.min_val and cur_meas.realvalue < cur_clas.max_val:
						return (i, cur_clas)	
		else:
			cnt_categ = data
			class_ind = -1
			for ind, cnt in enumerate(cnt_categ):
				if cnt > 0:
					class_ind = ind
			if meas_type == "v":
				return (class_ind, self.vel_classification[ class_ind ])
			elif meas_type == "a":
				return (class_ind, self.acc_classification[ class_ind ])
		
	
	'''
	category_diagnosis 
		REQUIRES these data loaded in Estimator object:
			machine_name, (acc_sensor_list or vel_sensor_list), new_data, (acc_classification or vel_classification)
		DESCRIPTION:
			Run velocity diagnosis for the machine.
			For each sensor there is some referent vibration interval that the sensor should be in, and some interval that
				it must not exceed	
			For each sensor, all measurements from new_data are classified into meas_classification classes
			if by_sensor == True: Display classification for each sensor separately
			if details == True: Display details
			
			if meas_type == "a": run category_diagnosis for all available acceleration sensors using acc_classification classifier
			if meas_type == "v": run category_diagnosis for all available velocity sensors using vel_classification classifier
		EXAMPLE of usage:
			Create Estimator object, and load the REQUIRES data.
			category_diagnosis(meas_type = "a") or category_diagnosis(meas_type = "v")
	'''
	def category_diagnosis(self, meas_type, by_sensor = True, details = True):
		if meas_type not in ["a", "v"]:
			print("Wrong measure type")
			return None
		if(meas_type == "a"):
			print("Running acceleration diagnosis for machine:", self.machine_name)			
			sensor_list = self.acc_sensor_list
			meas_classification = self.acc_classification
		else:
			print("Running velocity diagnosis for machine:", self.machine_name)
			sensor_list = self.vel_sensor_list
			meas_classification = self.vel_classification
			
		###TODO Plot data for each sensor with marked limits of the standard
		cnt_categ = {}
		
		for cur_sensor in sensor_list:
			cnt_categ[ cur_sensor ] = [0] * len(meas_classification)
			if len(self.new_data[ cur_sensor ]) == 0:
				continue

			for cur_meas in self.new_data[ cur_sensor ]:
				cnt_categ[ cur_sensor ][ self.classify(cur_meas, meas_type)[ 0 ] ] += 1
		
		for cur_sensor in sensor_list:
			class_ind, cur_class = self.classify(cnt_categ[ cur_sensor ], meas_type)
			'''
			<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<remove this
			if class_ind == -1 or len(self.new_data[ cur_sensor ]) == 0:
				print("..", cur_sensor, ": ", sep = "", end="")
				print("N/A")
				if(details):
					print("....no data")
				else:
					print()
			else:
				print("..", cur_sensor, ": ", sep="", end ="")
				print(cur_class.class_name)
				
				if(details):
					for ind, cnt in enumerate(cnt_categ[ cur_sensor ]):
						print("....", meas_classification[ ind ].class_name, "/", "all: ", sep = "", end = "")
						print(cnt, "/", len(self.new_data[ cur_sensor ]), " = ", cnt/len(self.new_data[ cur_sensor ]), sep = "")
				>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
				'''
		'''
		#whole machine classification
		cnt_categ_total = [0] * len(meas_classification)
		cnt_categ_total_sum = 0
		for cur_sensor in sensor_list:
			for ind,cnt in enumerate(cnt_categ[cur_sensor]):
				cnt_categ_total[ ind ] += cnt
				cnt_categ_total_sum += cnt
		print("Machine", self.machine_name, "is working:", self.classify(cnt_categ_total, meas_type)[ 1 ].class_name)
		if(details):
			for ind, cnt in enumerate(cnt_categ_total):
				print("..", meas_classification[ ind ].class_name, "/", "all: ", sep = "", end = "")
				print(cnt, "/", cnt_categ_total_sum, " = ", cnt/cnt_categ_total_sum, sep = "")
		'''
		return cnt_categ
	
	
	
	'''
	display_data_info
		REQUIRES
		DESCRIPTION
			If data is a numpy vector, displays it's mean, standard deviation and variance
		EXAMPLE of usage:
			
	'''
	def display_data_info(self, data, data_name, pref = "..."):
		print(pref, "Info for ", data_name, sep = "")
		mu, sigma2 = ad.estimateGaussian(data)
		print(pref, ".mean: ", mu, sep = "")
		print(pref, ".std d: ", np.sqrt(sigma2), sep = "")
		print(pref, ".variance: ", sigma2, sep = "")
	
	
	'''
	compatibility_diagnosis
		REQUIRES these data loaded in Estimator object:
			new_data, machine_name, sensor_list
			referent_data or (best_mu and best_sigma2)
			
		DESCRIPTION
			Finds the estimation of measurements from referent_data 
				and predict that measurement from new_data is "good" if it belongs to 3*std.dev. interval from its mean, which means
				it belongs to 99.7% of referent_data, and predict that it is "outlier" otherwise. 
				If there are more than 10% of outliers in new_data, the function will display that it is not compatibile with referent_data
				which is considered that something has changed over time, and further analysis should be taken by expert in vibration analysis
				or maintaince event should be performed.   
			if by_sensor == True: Make 1d Gaussian estimation from referent_data
				-> i.e. for each sensor make Gaussian estimation and try to fit each sensor from new_data into it
			if by_sensor == False: Make multivariateGaussian estimation from referent_data
				-> i.e. create new features where each example is rolling mean for some time interval, each feature corresponding to one sensor
			if use_best_data == False: Make estimation from referent_data
			if use_best_data == True: Use best_mu and best_sigma2 as estimations
		EXAMPLE of usage:
	'''
	def compatibility_diagnosis(self, details = True, use_best_data = False):
		mu = {}
		sigma2 = {}
		for cur_sensor in self.vel_sensor_list + self.acc_sensor_list:
			if not cur_sensor in self.new_data:
				self.new_data[ cur_sensor ] = []
			if not cur_sensor in self.referent_data:
				self.referent_data[ cur_sensor ] = []
		
		if use_best_data:
			mu = self.best_mu.copy()
			sigma2 = self.best_sigma2.copy()
		else:
			#need to estimate data from referent_data			
			for cur_sensor in self.vel_sensor_list + self.acc_sensor_list:
				print("Estimating sensor:", cur_sensor)
				m_referent_data = len(self.referent_data[ cur_sensor ])
				if m_referent_data < 10:
					print("..too low amount of data: referent_data(", m_referent_data, ")", sep="")
					continue
				referent_data_v = filter.measurements_to_numpy_vector(self.referent_data[ cur_sensor ])[:, None] #m*1
				ref_mu, ref_sigma2 = ad.estimateGaussian(referent_data_v)
				if ref_mu.size != 1 or ref_sigma2.size != 1:
					print("Error dimensions")
				mu[ cur_sensor ] = ref_mu
				sigma2[ cur_sensor ] = ref_sigma2
		##estimation done
		
		good_cnt_d = {}
		outlier_cnt_d = {}
		new_data_mu = {}
		new_data_sigma2 = {}
		
		all_good = True
		for cur_sensor in self.vel_sensor_list + self.acc_sensor_list:
			if cur_sensor not in mu or cur_sensor not in sigma2:
				print("Skipping", cur_sensor)
				continue
			print("Diagnosing sensor", cur_sensor)
			m_new_data = len(self.new_data[ cur_sensor ])
			if m_new_data < 10:
				if details:
					print("..too low amount of data: new_data(", m_new_data, ")", sep="")
				continue	
			new_data_v = filter.measurements_to_numpy_vector(self.new_data[ cur_sensor ])[:, None] #m*1
			
			cur_mu = mu[ cur_sensor ]
			cur_sigma2 = sigma2[ cur_sensor ]
			
			epsilon = ad.multivariateGaussian((cur_mu + 3 * np.sqrt(cur_sigma2))[:, None], np.array([cur_mu]), np.array([cur_sigma2])) 
			#3*std.deviation is where 99.7% of data is located
			
			new_data_pred = ad.multivariateGaussian(new_data_v, cur_mu, cur_sigma2)
			good_cnt = sum(new_data_pred >= epsilon)
			outlier_cnt = m_new_data - good_cnt
			good_cnt_d[ cur_sensor ] = good_cnt
			outlier_cnt_d[ cur_sensor ] = outlier_cnt
			new_data_mu[ cur_sensor ], new_data_sigma2[ cur_sensor ] = ad.estimateGaussian(new_data_v)
			'''
			if outlier_cnt / m_new_data < 0.1: #10% tolerance
				print("..FITTING to referent data good")
			else:
				print("..NOT FITTING to referent data")
				all_good = False
			if details:
				print("..", good_cnt, "/", m_new_data, "=", good_cnt/m_new_data, " examples from new data FITS to referent data interval", sep = "")
				print("..(This value should be greater than 90%)")
				print(cur_sensor, "\n.referent data\n", "..mu: ", cur_mu, "\n..std.dev.: ", np.sqrt(cur_sigma2), "\n..variance: ", cur_sigma2, sep="")
				self.display_data_info(new_data_v, "new_data")
			'''	
				
			#TODO Plot distribution for referent_data and new_data on same graph for comparing	
		#endfor
		'''
		if all_good:
			print("[GOOD] All sensors for", self.machine_name, "FIT to referent data.")
		else:
			print("[WARNING] Some sensors for", self.machine_name, "DO NOT FIT to referent data.")
			print("Consider consulting vibration analysis expert.")
			#TODO Messages - sto treba raditi ako se povecava / smanjuje mean value, sto treba raditi ako se povecava variance
		'''
		return (mu, sigma2, new_data_mu, new_data_sigma2, good_cnt_d, outlier_cnt_d)
		
