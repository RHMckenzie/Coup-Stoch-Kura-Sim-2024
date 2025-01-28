#Each file contains 9 iterations

#each file now takes 1 hour (incl. overhead)!

# 1 file per hour
# 12 files per 12 hour period
# 24 files per day period

# 960 total files



#dataset costs 40 jobs per day,
#max queue is 200, (for 5 jobs running the same data)
#can run 5 * 9 iterations/day
# will likely take 3 days

#0.2MB per iteration.

# 960 * 10 iterations. 2GB total data for a n=10 dataset, 20 gb for n=100


import os
import functools
import sys
import parser
import json
import pandas as pd
import numpy as np
import traceback
import re
import h5py
from collections.abc import Generator
reduce, partial = functools.reduce, functools.partial





# This entire autorun setup is quite weird, I don't think it's necessary to utilise (and parser.py should be invoked instead), but may come in handy if you're planning on running batch tests.
# what I suggest you do if you're using this of your own accord is to just do "autorun.py 0-39 1" with the tests in the tests folder.

# distribution of jobs, presuming you're running 40 jobs.
job_dist = 40
# job cycling, so that jobs are not saved to the same timeslot accidentally, this variable is safe to ignore. 
cycle_var = 4

proj_loc = "/project/RDS-FEI-TB_NN_INFOTHEORY-RW/rmck6484_thesis/"

parser_script \
        = proj_loc + "src/parser.py"
parser_list = ["python3", parser_script]

folder = "tests/"

#files = os.listdir( folder)

#Rightwards partial function for overloading and chaining function arguments.
#very similar to "partial" from functools
def rpartial(func, *args, **keywords):
    def newfunc(*fargs, **fkeywords):
        newkeywords = {**fkeywords, **keywords}
        return func(*fargs, *args, **newkeywords)
    newfunc.func = func
    newfunc.args = args
    newfunc.keywords = keywords
    return newfunc

# a "for while" generator, yields x and increments while count is true.
# Equivalent to "range(max_count)[x::split_count]" or "range(x, max_count, split_count)"
def split(x: int, split_count: int, max_count: int) -> Generator[int]:
    while x < max_count:
        yield x
        x += split_count

# creates and seperates max_count objects into split_count different groups, evenly distributes and staggers, used for mapping.
def split_all(split_count: int, max_count: int) -> list[list[int]]:
    out = map(rpartial(split, split_count, max_count), range(0, split_count))
    out = map(list, out)
    return list(out)

# A helper function that gathers info about the parameters used for a specific run
def gather_info(folder):
    try:
        with open(os.path.join(folder, "settings.json"), "r") as f:
            d = json.load(f)
        out = {
            "n": d["graph"]["arguments"]["n"],
            "k": d["graph"]["arguments"]["k"],
            "p": d["graph"]["arguments"]["p"],
            "c": d["graph"]["settings"]["cross_couple_value"],
            "zeta": d["processes"][0]["arguments"]["zeta"]
        }
        return out
    except Exception as e:
        print(f"Error gathering info from {folder}: {e}")
        return None

# replaces suffix of file
def replace_suffix(filename, new_suffix):
    base = os.path.splitext(filename)[0]
    return f"{base}.{new_suffix.lstrip('.')}"  # Ensure no leading dot

# adds the run from folder into the hd5 at destination using the info dictionary.
def create_hd5_group(folder, destination, info_dict, append=True):
    if folder in info_dict:
        info = info_dict[folder]
    else:
        info = gather_info(folder)
        info_dict[folder] = info

    try:
        keyset = set(info.keys()) - set(("data",))
        data_name = str(os.path.basename(folder))
        #print(data)
        # Save to HDF5
        with h5py.File(destination, 'a' if append else 'w') as hf:
            group = hf.create_group(data_name)
            for k in keyset:
                group.attrs[k] = info[k]
        return True
    except Exception as e:
        print(f"Error processing {folder}: {e}")
        print(traceback.format_exc())
        return False


# save simulation data to hd5 file
def populate_hd5_group(folder, destination, filename, info_dict, append=True):
    if folder in info_dict:
        info = info_dict[folder]
    else:
        info = gather_info(folder)
        info_dict[folder] = info
    try:
        # Load the data from the .npy file
        if os.path.splitext(filename)[1] == ".dat":
            with open(os.path.join(folder, filename), "r") as f:
                data = np.float32(f.read())
        else:
            data = np.load(os.path.join(folder, filename), allow_pickle = True)
        keyset = set(info.keys()) - set(("data",))
        data_name = str(os.path.join(os.path.basename(folder), filename))
        # Save to HDF5
        with h5py.File(destination, 'a' if append else 'w') as hf:
            dataset = hf.create_dataset(data_name, data = data, compression="lzf" if type(data) is not np.float32 else None)
            for k in keyset:
                dataset.attrs[k] = info[k]
        return True
    except Exception as e:
        print(f"Error processing {folder} {filename} to store in {destination}: {e}")
        print(traceback.format_exc())
        return False

# check if a folder exists
def ensure_folder_exists(folder_path):
    """Check if a folder exists, and create it if it doesn't."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

# select all files that end with .npy or .dat (usually important data files)
def gather_files(folder):
    file_list = []
    for filename in os.listdir(folder):
        if filename.endswith('.npy') or filename.endswith('.dat'):
            file_list.append(filename)
    return file_list

# collects all the data from all runs and stores them in the HD5 files
def collect_data(folders, destination_folder, destination_name):
    ensure_folder_exists(destination_folder)
    dest = os.path.join(destination_folder, destination_name)
    if os.path.isfile(dest):
        os.remove(dest)
    print("Collecting data in",dest)
    info = {}
    for f in folders:
        create_hd5_group(f, dest, info, append=True)
        files = gather_files(f)
        for filename in files:
            populate_hd5_group(f, dest, filename, info, append=True)

#Weird main setup, this file was designed explicilty to record all the given data into a hd5 file (not necessarily what parser.py does)
#for the case, you need to 

if __name__ == "__main__":
    proj_loc = "/project/RDS-FEI-TB_NN_INFOTHEORY-RW/rmck6484_thesis/"
    files = os.listdir(proj_loc + folder)    
    li = split_all(job_dist, len(files))
    li_files = map(partial(map, lambda x: folder + files[x]), li)
    li_files = list(map(list, li_files))


    if len(sys.argv) <= 1:
        print("You should read the comments before running this program")
        print("Usage: python autorun.py [0-39]")
        print("Or:")
        print("python autorun.py help")
        sys.exit(1)
    #testing routine, don't actually ever pass in "test" as the first argument.
    if sys.argv[1] == "help":
        print("""Script that is the individual instancer for bulk run tests
        run by python autorun.py [0-39], where the first argument represents the individual instance id
        this id (and thus the split allocation of work can be modified in the job_dist variable
        Will generally evenly allocate the work, will need to be run on each job under a different ID.
        Look at py_auto_array.pbs for further understanding
        Requires there to be test.json files under \$\{proj_loc\}/tests/""")
        sys.exit(0)
    if sys.argv[1] == "test":
        test_vars = [proj_loc + "sim.json"]
        parser_list = parser_list + test_vars
        i = "simulated"
        cycle = "run"
    else:
        if len(sys.argv) <= 2:
            #print("Please pass in two numerical arguments")
            na = 1
        try:
            _ = int(sys.argv[1])
            if len(sys.argv) <= 2:
                _ = int(sys.argv[2])
        except:
            print("Incorrect arguments passed:", sys.argv[1], sys.argv[2])
            sys.exit(1)
        i = int(sys.argv[1])
        if i >= len(li):
            print("Too large i passed:", sys.argv[1])
            sys.exit(1)
        cycle = 1
        if len(sys.argv) > 2:
            cycle = int(sys.argv[2])
        to_use = li_files[i]
        for l in range(cycle * cycle_var):
            to_use.append(to_use.pop(0))
        parser_list = parser_list + to_use
    #does functional programming magic to combine the lists
    print("python3 " + reduce(lambda x,y: x + ' ' + y, parser_list))
    
    #runs the simulations
    files = parser.main_loop(parser_list[1:], return_value=True)
    
    #combines the files here:
    output = "_" + str(i) + "_" + str(cycle)
    output_loc = os.path.join(proj_loc, "data")
    name = "run" + output + ".h5"
    collect_data(files, output_loc, name)
        
        
