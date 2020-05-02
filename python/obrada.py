import dataset_loader as dl
import measurement as ms
from random import shuffle
import numpy as np
import os, os.path
from scipy import stats

MAX_DIFF = 30
DATA_TREE_PATH = "data"

# max_diff is maximum distance between starting time of
# two measurements that can be in the same batch (in seconds)
def separate_by_time(measurements_list, max_diff = MAX_DIFF):
    batches = []
    previous_timestamp = -max_diff - 1
    for measurement in measurements_list:
        if measurement.start_timestamp - previous_timestamp > max_diff:
            batches.append([])
        previous_timestamp = measurement.start_timestamp
        batches[-1].append(measurement)
    return batches

def load_shared_data():
    with open('prog_data.txt', 'r') as pd:
        path, ordering = pd.readline().strip().split(':')
        ordering = [int(i) for i in ordering.split(',')]
        shared_data[path] = ordering
def save_shared_data():
    with open('prog_data.txt', 'w') as pd:
        for key in shared_data:
            pd.write(':'.join([key, ','.join([str(i) for i in shared_data[key]])]))

def randomize_blocks(path):
    ms = []
    dl.load_measurements(path, ms)
    temp = separate_by_time(ms)
    shared_data[path] = list(range(len(temp)))
    shuffle(shared_data[path])

shared_data = {}
path_measurements_map = {}

def get_measurements(path, keep_loaded):
    if path in path_measurements_map:
        if keep_loaded:
            return path_measurements_map[path]
        else:
            return path_measurements_map.pop(path)
    else:
        if keep_loaded:
            path_measurements_map[path] = []
            dl.load_measurements(path, path_measurements_map[path])
            return path_measurements_map[path]
        else:
            temp = []
            dl.load_measurements(path, temp)
            return temp

def get_sensor_csv(dir_path, acc, filename_contains = ""):
    if not dir_path.endswith('/'): dir_path += '/'
    files = os.listdir(dir_path)
    for p in files:
        if os.path.isfile(dir_path + p):
            if p.endswith('.csv') and filename_contains in p:
                acc.append(dir_path + p)
        else:
            acc.append([])
            get_sensor_csv(dir_path + p, acc[-1], filename_contains)

def find_correlations(paths, desired_corr_list, max_corr_time_dist, min_corr_coeff, keep_loaded):
    measurements_j = get_measurements(paths[0], keep_loaded)
    for i in range(len(paths) - 1):
        measurements_i = measurements_j
        for j in range(len(paths) - 1, i, -1):
            measurements_j = get_measurements(paths[j], keep_loaded)
            print("Correlating", paths[i], "and", paths[j])
            datasets = [[], []]
            k, l = 0, 0
            while k < len(measurements_i) and l < len(measurements_j):
                dist = measurements_i[k].end_timestamp - measurements_j[l].end_timestamp
                if abs(dist) < max_corr_time_dist:
                    datasets[0].append(measurements_i[k].realvalue)
                    datasets[1].append(measurements_j[l].realvalue)
                    k += 1
                    l += 1
                elif dist < 0:
                    k += 1
                else:
                    l += 1
            if len(datasets[0]) < 3:
                print("Not enough data to correlate")
                continue

            corr_coeff, pvalue = stats.pearsonr(*datasets)
            if min_corr_coeff < abs(corr_coeff):
                print("############## IMPORTANT ###############")
                desired_corr_list.append((corr_coeff, paths[i], paths[j]))
            print("Correlation based on", len(datasets[0]), "corr_coeff =: ", corr_coeff)

if __name__ == "__main__":
    dl.split_into_attr_tree("IoT_and_predictive_maintenance-full.csv", DATA_TREE_PATH, ["machine_name", "sensor_type"])
    apaths, vpaths = [], []
    get_sensor_csv(DATA_TREE_PATH, apaths, "a_max")
    interesting_correlations = []
    for machine_paths in apaths:
        find_correlations(machine_paths, interesting_correlations, 3, 0.7, True)
    with open("corr.csv", 'w') as corr_file:
        corr_file.write('"corr_coeff";"path1";"path2"\n')
        for corr_coeff, path1, path2 in sorted(interesting_correlations):
            print(corr_coeff, path1, path2)
            corr_file.write(str(corr_coeff) + ';' + '"' + path1 + '"' + ';' + '"' + path2 + '"\n')
    # randomize_blocks('data/FL01/drive_gear_a_max.csv')
    # dodati loadanje i spremanje poretka u file i iz njega (npr randomize provoditi samo na onima

