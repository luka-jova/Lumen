# import pandas as pd
import multiprocessing as mp
import os.path
import os
from shutil import rmtree
from measurement import Measurement
# pd.read_csv("IoT_and_predictive_maintenance-full.csv", sep = ';')


'''
    Splits textual file in number_of_batches files with roughly equal number of lines (+-1)
'''
def split_by_line_number(src_path, dest_path, number_of_batches, copy_first_line = True):
    with open(src_path) as dat:
        for i, ln in enumerate(dat):
            if (i == 0):
                attr_ln = ln
        dat.seek(0)
        ln_cnt = i + 1
        print("Number of lines:", ln_cnt)
        qs = [mp.Queue() for i in range(number_of_batches)]
        processes = [mp.Process(
                        args=(embed_in_path(dest_path, str(i)), qs[i]),
                        target = q_to_file
                        ) for i in range(number_of_batches)]
        for process in processes: process.start()
        j = 1
        for i, ln in enumerate(dat):
            if (i >= ln_cnt * j // number_of_batches):
                print("Line", i, "- sending terminal character to process", j - 1)
                qs[j - 1].put('\n')
                if copy_first_line: qs[j].put(attr_ln)
                j += 1
            qs[j - 1].put(ln)
        print("Reading completed. Sending terminal character to the last process.")
        qs[-1].put('\n')
        print("Writing still in progress, please don't terminate the program.")
        for process in processes: process.join()
        print("Writing complete.")

'''
    Splits a csv file in separate csv files for each different value in selected column
'''
def split_by_attr(src_path, dest_path, attr_name, copy_first_line = True):
    with open(src_path, encoding="utf-8") as dat:
        attrs_map = {}
        for i, ln in enumerate(dat):
            if (i == 0):
                attr_ln = ln
                attrs = attr_ln[1:-1].replace('"', '').split(';')
                if attr_name not in attrs:
                    print("Attribute not found")
                    return
                else:
                    print("Reading file, please wait.")
                    attr_index = attrs.index(attr_name)
            else:
                attr_key = ln.split(';')[attr_index]
                if attr_key not in attrs_map:
                    q = mp.Queue()
                    p = mp.Process(
                        target = q_to_file,
                        args = (embed_in_path(dest_path, attr_key), q)
                    )
                    p.start()
                    if copy_first_line: q.put(attr_ln)
                    attrs_map[attr_key] = (q, p)
                attrs_map[attr_key][0].put(ln)

        print("Reading completed. Sending terminal character to the processes.")
        for q, p in attrs_map.values():
            q.put('\n')
        print("Writing still in progress. Please don't terminate the program.")
        for q, p in attrs_map.values():
            p.join()

        print("Writing complete.")

'''
    Copies from queue q to the file with path dest_path until q gets '\n'
'''
def q_to_file(dest_path, q):
    with open(dest_path, 'w') as outFile:
        ln = q.get()
        while (ln != '\n'):
            outFile.write(ln)
            ln = q.get()

'''
    Adds string s to the end of file path, before extension
'''
def embed_in_path(path, s):
    extension_index = path.rfind('.')
    if extension_index == -1: return path + s

    return path[:extension_index] + s + path[extension_index:]

def split_into_attr_tree(src_path, dest_dir_path, attributes, force_rewrite = False, del_src = False):
    if not os.path.isfile(src_path): return
    if not attributes or os.path.isdir(dest_dir_path) and not force_rewrite:
        return
    elif os.path.isdir(dest_dir_path):
        rmtree(dest_dir_path)
    else:
        os.mkdir(dest_dir_path)
    curr_attr = attributes[0]
    if not dest_dir_path.endswith('/'):
        dest_dir_path += '/'
    split_by_attr(src_path, dest_dir_path + '.csv', curr_attr)
    if del_src: os.remove(src_path)
    child_files = os.listdir(dest_dir_path)
    for f in child_files:
        split_into_attr_tree(dest_dir_path + f, dest_dir_path + f[:f.rfind('.csv')], attributes[1:], force_rewrite, True)

def load_measurements(src_path, dest_list, predicate = lambda m: True):
    with open(src_path) as dat:
        for ln in dat:
            if Measurement.CSV_HEADER in ln: continue
            try:
                m = Measurement(ln[:-1])
                if predicate and predicate(m):
                    dest_list.append(m)
            except Exception as e:
                print(e)

def store_measurements(src_list, dest_path, add_header = True):
    with open(dest_path, 'w') as dest_file:
        if add_header:
            dest_file.write(Measurement.CSV_HEADER)
        for measurement in src_list:
            dest_file.write(measurement.to_csv() + '\n')

if __name__ == "__main__":
    # usage examples:
    # split_by_attr("IoT_and_predictive_maintenance-full.csv", "machine.csv", "machine_name")
    # split_by_line_number("machineFL02.csv", "machine2_batch.csv", 10)

    split_into_attr_tree("IoT_and_predictive_maintenance-full.csv", "data", ["machine_name", "sensor_type"])

