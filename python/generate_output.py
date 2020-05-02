#generate_output_data prepares the input for Linear regression algorithm
#result of generate_output_data is filled output_data list (provided by reference)
#sen_i is an average value of the vibration
#returns the number of ignored data??
	#sweep line algorithm .... not completed
#output_data is a result list containing lists where output_data[ i ] == [t_start t_end sen_1 sen_2 sen_3 ....]
#t_start is starting time of measurement
#t_end is ending time of measurement
#sen_i is a value of the i-th sensor during the time [t_start, t_end]
def generate_output_data(sensor_data, sensor_list, output_data):
	cnt_ignored = 0
	
	finished = False
	N = len(sensor_list)
	#list of reversed queues
	Q = []
		
	for cur_sensor in sensor_list:
		tmp = []
		for cur_timeblock in sensor_data[ cur_sensor ]:
			tmp.append((start_time(cur_timeblock), end_time(cur_timeblock), effective_value(cur_timeblock)))
		tmp.reverse()
		Q.append(tmp)
	
	while not finished:
		#tmp contains tuples of current time intervals (first from each sensor)
		tmp = []
		for i in range(N):
			tmp.append(Q[ i ][ -1 ])
		
		cur = is_valid(tmp)
		if cur == (-1, -1):
			#pop the minimum timeval
			##print("pop minimum interval")
			##print(tmp)
			mini = tmp[ 0 ][ 0 ]
			ind_mini = 0
			for j in range(N):
				if tmp[ j ][ 0 ] < mini:
					mini = tmp[ j ][ 0 ]
					ind_mini = j
			Q[ ind_mini ].pop()
			cnt_ignored += 1
		else:
			#add this time interval, pop all current intervals
			##print("pop all intervals")
			##print(tmp)
			output_data.append([cur[ 0 ], cur[ 1 ]])
			for j in range(N):
				output_data[ -1 ].append(tmp[ j ][ 2 ])
				Q[ j ].pop()
			
		for i in range(N):
			if len(Q[ i ]) == 0:
				finished = True
	
	for i in Q:
		cnt_ignored += len(i)
	
	return cnt_ignored


#average value in the timeblock
def effective_value(timeblock):
	res = 0
	for cur_measure in timeblock:
		res += cur_measure.realvalue
	res /= len(timeblock)
	return res

def start_time(timeblock):
	return timeblock[ 0 ].start_timestamp
	
def end_time(timeblock):
	return timeblock[ -1 ].end_timestamp

#make starting time for measurements at 0
def normalize_measurements():
	return 1	

#argument is list of tuples (time_start, time_end, eff_val)
#return overlaping time of all tuples, returns (-1, -1) if there is no such time
def is_valid(config):
	l = []
	last = -1
	for i in config:
		l.append((i[ 0 ], 0))
		l.append((i[ 1 ], 1))
	l.sort()
	cnt = 0
	for i in l:
		if i[ 1 ] == 0:
			cnt += 1
			last = i[ 0 ]
		else:
			if cnt == len(config):
				return (last, i[ 0 ])
			else:
				return (-1, -1)
