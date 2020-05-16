from ast import literal_eval

CONFIG_FILE_PATH = ".config"

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

