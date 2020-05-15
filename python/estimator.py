from numpy import inf
import numpy as np
from measurement import Measurement

class Velocity_class:
	def __init__(self, class_name = "", min_vel = -inf, max_vel = inf, color = None):
		self.class_name = class_name
		self.min_vel = min_vel
		self.max_vel = max_vel
		self.color = color

class Estimator:
	####Dictionaries where key=sensor_name, val = list of Measurement objects
	known_data = []
	new_data = []
	referent_data = []
	#######
	
	
	machine_name = ""
	sensor_list = []
	
	def __init__(self,  machine_name, sensor_list, known_data = [], new_data = [], referent_data = []):
		self.machine_name = machine_name
		self.sensor_list = sensor_list.copy()
		self.known_data = known_data.copy()
		self.new_data = new_data.copy()
		self.referent_data = referent_data.copy()
	
	###ISO 10816 classification for Class III - Large Rigid Foundations
	#this may me modified - e.x. to Class II
	vel_classification = [
		Velocity_class(class_name = "Good", min_vel = 0, max_vel = 2.8, color = "g"),
		Velocity_class(class_name = "Satisfactory", min_vel = 2.8, max_vel = 7.1, color = "c"),
		Velocity_class(class_name = "Unsatisfactory", min_vel = 7.1, max_vel = 18.0, color = "y"),
		Velocity_class(class_name = "Unacceptable", min_vel = 18.0, max_vel = inf, color = "r")		
	]
	
	'''
	returns (index, Velocity_class)
	input can be:
		a) Measurement 
			-> in this case it classifies a single Measurement in vel_classification categories
		b) list which count of how many measures there are for each category in vel_classification 
			-> in this case it classifies the whole set of measurements
	'''
	def classify(self, data):
		if isinstance(data, Measurement):
			cur_meas = data
			for i, cur_clas in enumerate(self.vel_classification):
				if cur_meas.realvalue >= cur_clas.min_vel and cur_meas.realvalue < cur_clas.max_vel:
					return (i, cur_clas)
		else:
			cnt_categ = data
			class_ind = -1
			for ind, cnt in enumerate(cnt_categ):
				if cnt > 0:
					class_ind = ind
			return (class_ind, self.vel_classification[ class_ind ])
		
	
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
	def velocity_diagnosis(self, by_sensor = False, details = False):
		print("Running velocity diagnosis for machine:", self.machine_name)
		###TODO Plot data for each sensor with marked limits of the standard
		cnt_categ = {}
		for cur_sensor in self.sensor_list:
			cnt_categ[ cur_sensor ] = [0] * len(self.vel_classification)
			if len(self.new_data[ cur_sensor ]) == 0 or self.new_data[cur_sensor][ 0 ].unit != "mm/s":
				continue

			for cur_meas in self.new_data[ cur_sensor ]:
				cnt_categ[ cur_sensor ][ self.classify(cur_meas)[ 0 ] ] += 1
		
		if by_sensor:
			for cur_sensor in self.sensor_list:
				class_ind, cur_class = self.classify(cnt_categ[ cur_sensor ])
				
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
		for cur_sensor in self.sensor_list:
			for ind,cnt in enumerate(cnt_categ[cur_sensor]):
				cnt_categ_total[ ind ] += cnt
				cnt_categ_total_sum += cnt
		print("Machine", self.machine_name, "is working:", self.classify(cnt_categ_total)[ 1 ].class_name)
		if(details):
			for ind, cnt in enumerate(cnt_categ_total):
				print("..", self.vel_classification[ ind ].class_name, "/", "all: ", sep = "", end = "")
				print(cnt, "/", cnt_categ_total_sum, " = ", cnt/cnt_categ_total_sum, sep = "")
	
