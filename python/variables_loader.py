from ast import literal_eval
from estimator import Estimator, Classification
from numpy import array

CONFIG_FILE_PATH = "config/.config"

def keep_primitives(from_dict, which=None, keep_types=(str, int, float, dict, set, list, tuple, bool)):
	"""Helper function for filtering variables to load or store
	
	Filters out those variables whose type isn't in keep_types or name is like __*__.
	Optionally, the names of variables to keep may be passed in which iterable.
	
	Parameters
	----------
	from_dict : dict with str keys
		Dictionary to filter
	which : iterable
		If not None, the function will only keep the keys that are in this iterable
	keep_types : iterable
		Types of values to keep
		
	Returns
	-------
	A new dictionary of items from from_dict that satisfy the filter
	"""
	return {it:from_dict[it] for it in from_dict 
		if (which is None or it in which) and type(from_dict[it]) in keep_types and not(it.startswith("__") and it.endswith("__"))
	}

def load_variables(which=None, to_dict=globals(), from_file_path=CONFIG_FILE_PATH):
	"""Loads variables whose name is in which from_file_path to_dict
	
	Dict may be locals() or globals() dictionary of a module / scope whose global
	or local variables need to be loaded from from_file_path.
	
	Parameters
	----------
	which : iterable
		If not None, the function will only keep the variables whose names are in this iterable
	to_dict : dict with str keys
		Dictionary that needs to be populated with variable_name : variable_value items
	from_file_path : str
		Path to file containing str representation of dictionary with variable_name : variable_value items
		
	Returns
	-------
	None
	"""
	with open(from_file_path, 'r', encoding="utf-8") as config_file:
		to_dict.update(keep_primitives(literal_eval(config_file.read()), which))

def store_variables(which=None, from_dict=globals(), to_file_path=CONFIG_FILE_PATH):
	with open(to_file_path, 'w', encoding="utf-8") as config_file:
		config_file.write(str(keep_primitives(from_dict, which)))

def store_estimator(to_file_path, src_est):
	variables_to_store = {
		"best_mu" : { key : list(value) for key, value in src_est.best_mu },
		"best_sigma2" : { key : list(value) for key, value in src_est.best_sigma2 },
		"vel_classification" : [vars(it) for it in src_est.vel_classification],
		"acc_classification" : [vars(it) for it in src_est.acc_classification],
		"RUN_V_CATEGORIZATION" : src_est.RUN_V_CATEGORIZATION,
		"RUN_A_CATEGORIZATION" : src_est.RUN_A_CATEGORIZATION,
		"RUN_CATEGORIZATION_NEW_DATA" : src_est.RUN_CATEGORIZATION_NEW_DATA,
		"RUN_CATEGORIZATION_ALL_DATA" : src_est.RUN_CATEGORIZATION_ALL_DATA,
		"RUN_COMPATIBILITY_LAST_WEEK" : src_est.RUN_COMPATIBILITY_LAST_WEEK,
		"RUN_COMPATIBILITY_LAST_N_DAYS" : src_est.RUN_COMPATIBILITY_LAST_N_DAYS,
		"RUN_COMPATIBILITY_BEST_FIT" : src_est.RUN_COMPATIBILITY_BEST_FIT,
		"REFERENT_LAST_N_DAYS" : src_est.REFERENT_LAST_N_DAYS
	}
	store_variables(None, variables_to_store, to_file_path)

def load_estimator(from_file_path, dest_est):
	variables_to_load = {}
	load_variables(None, variables_to_load, from_file_path)
	for key, value in variables_to_load.items():
		if key in ("best_mu", "best_sigma2"):
			for sensor in value:
				value[sensor] = array(value[sensor])
		elif "classification" in key:
			value = [Classification(**it) for it in value]
		setattr(dest_est, key, value)
	
	


