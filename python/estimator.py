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
	best_mu = {}
	best_sigma2 = {}
	
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
		Classification(class_name = "Good", min_val = 0, max_val = 1000, color = "g", unit = "mg"),
		Classification(class_name = "Satisfactory", min_val = 1000, max_val = 5000, color = "c", unit = "mg"),
		Classification(class_name = "Unsatisfactory", min_val = 5000, max_val = 10000, color = "y", unit = "mg"),
		Classification(class_name = "Unacceptable", min_val = 10000, max_val = inf, color = "r", unit = "mg")		
	]
	
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
	velocity_diagnosis 
		REQUIRES these data loaded in Estimator object:
			machine_name, sensor_list, new_data, vel_classification
		DESCRIPTION:
			Run velocity diagnosis for the machine.
			For each sensor there is some referent vibration interval that the sensor should be in, and some interval that
				it must not exceed	
			For each sensor, all measurements from new_data are classified into vel_classification classes
			if by_sensor == True: Display classification for each sensor separately
			if details == True: Display details
		EXAMPLE of usage:
			Create Estimator object, and load the REQUIRES data.
			velocity_diagnosis()
	'''
	def velocity_diagnosis(self, by_sensor = True, details = True):
		print("Running velocity diagnosis for machine:", self.machine_name)
		###TODO Plot data for each sensor with marked limits of the standard
		cnt_categ = {}
		for cur_sensor in self.vel_sensor_list:
			cnt_categ[ cur_sensor ] = [0] * len(self.vel_classification)
			if len(self.new_data[ cur_sensor ]) == 0 or self.new_data[cur_sensor][ 0 ].unit != "mm/s":
				continue

			for cur_meas in self.new_data[ cur_sensor ]:
				cnt_categ[ cur_sensor ][ self.classify(cur_meas, "v")[ 0 ] ] += 1
		
		if by_sensor:
			for cur_sensor in self.vel_sensor_list:
				class_ind, cur_class = self.classify(cnt_categ[ cur_sensor ], "v")
				
				if class_ind == -1 or len(self.new_data[ cur_sensor ]) == 0 or self.new_data[ cur_sensor ][ 0 ].unit != "mm/s":
					print("..", cur_sensor, ": ", sep = "", end="")
					print("N/A")
					if(details):
						print("....no data or acceleration sensor")
					else:
						print()
				else:
					print("..", cur_sensor, ": ", sep="", end ="")
					print(cur_class.class_name)
					
					if(details):
						for ind, cnt in enumerate(cnt_categ[ cur_sensor ]):
							print("....", self.vel_classification[ ind ].class_name, "/", "all: ", sep = "", end = "")
							print(cnt, "/", len(self.new_data[ cur_sensor ]), " = ", cnt/len(self.new_data[ cur_sensor ]), sep = "")
		
		
		#whole machine classification
		cnt_categ_total = [0] * len(self.vel_classification)
		cnt_categ_total_sum = 0
		for cur_sensor in self.vel_sensor_list:
			for ind,cnt in enumerate(cnt_categ[cur_sensor]):
				cnt_categ_total[ ind ] += cnt
				cnt_categ_total_sum += cnt
		print("Machine", self.machine_name, "is working:", self.classify(cnt_categ_total, "v")[ 1 ].class_name)
		if(details):
			for ind, cnt in enumerate(cnt_categ_total):
				print("..", self.vel_classification[ ind ].class_name, "/", "all: ", sep = "", end = "")
				print(cnt, "/", cnt_categ_total_sum, " = ", cnt/cnt_categ_total_sum, sep = "")
	
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
			new_data, referent_data, machine_name, sensor_list
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
		EXAMPLE of usage:
			
	'''
	def compatibility_diagnosis(self, by_sensor = True, details = True):
		for cur_sensor in self.vel_sensor_list + self.acc_sensor_list:
			if not cur_sensor in self.new_data:
				self.new_data[ cur_sensor ] = []
			if not cur_sensor in self.referent_data:
				self.referent_data[ cur_sensor ] = []
		
		if by_sensor:
			all_good = True
			for cur_sensor in self.vel_sensor_list + self.acc_sensor_list:
				print("Estimating sensor:", cur_sensor)
				m_new_data = len(self.new_data[ cur_sensor ])
				m_referent_data = len(self.referent_data[ cur_sensor ])
				if m_new_data < 10 or m_referent_data < 10:
					if details:
						print("..too low amount of data: new_data(", m_new_data, "), referent_data(", m_referent_data, ")", sep="")
					continue	
				new_data_v = filter.measurements_to_numpy_vector(self.new_data[ cur_sensor ])[:, None] #m*1
				referent_data_v = filter.measurements_to_numpy_vector(self.referent_data[ cur_sensor ])[:, None] #m*1
				
				mu, sigma2 = ad.estimateGaussian(referent_data_v)
				if mu.ndim != 1:
					print("Error dimensions")
				epsilon = ad.multivariateGaussian((mu + 3 * np.sqrt(sigma2))[:, None], mu, sigma2) #3*std.deviation is where 99.7% of data is located
				
				new_data_pred = ad.multivariateGaussian(new_data_v, mu, sigma2)
				good_cnt = sum(new_data_pred >= epsilon)
				outlier_cnt = m_new_data - good_cnt
				
				if outlier_cnt / m_new_data < 0.1: #10% tolerance
					print("..seems to FIT referent data good")
				else:
					print("..NOT FITTING to referent data")
					all_good = False
				if details:
					print("..", good_cnt, "/", m_new_data, "=", good_cnt/m_new_data, " examples from new data FITS to referent data interval", sep = "")
					print("..(This value should be greater than 90%)")
					self.display_data_info(referent_data_v, "referent_data")
					self.display_data_info(new_data_v, "new_data")
					
					
				#TODO Plot distribution for referent_data and new_data on same graph for comparing	
			#endfor
			if all_good:
				print("[GOOD] All sensors for", self.machine_name, "FIT to referent data.")
			else:
				print("[WARNING] Some sensors for", self.machine_name, "DO NOT FIT to referent data.")
				print("Consider consulting vibration analysis expert.")
				#TODO Messages - sto treba raditi ako se povecava / smanjuje mean value, sto treba raditi ako se povecava variance
			
		else:
			print("Multivariate Gaussian not supported")
		
		
		
		
