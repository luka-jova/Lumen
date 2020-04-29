import dataset_loader as dl
import measurement as ms
from random import shuffle

MAX_DIFF = 30

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

if __name__ == "__main__":
    dl.split_into_attr_tree("IoT_and_predictive_maintenance-full.csv", "data", ["machine_name", "sensor_type"])
    randomize_blocks('data/FL01/drive_gear_a_max.csv')
    # dodati loadanje i spremanje poretka u file i iz njega (npr randomize provoditi samo na onima

