# Short Script that is pointed at a h5 package file, 
# constructs a csv/pkl of summary data


import numpy as np
import pandas as pd
import os
from tqdm import tqdm
import sys
import h5py


# files that were specifically valid for the task at hand, may be expanded if necessary
allowed = [
    "analytical_sigma_cont.dat",
    "ou_euler_sigma_squared.npy",
    "kuramoto_euler_sigma_squared.npy"
]


def process(file, breakin = 1000, limit = (None, 2000, 1100, 1010)):
    with h5py.File(file, 'r') as hf:
        data_array = []
        key_iter = tqdm(hf.keys())
        for k in key_iter:
            obj = hf[k]
            out_buffer = {}
            for attr in obj.attrs:
                out_buffer[attr] = obj.attrs[attr]
            for file in obj.keys():
                if file not in allowed:
                    continue
                file_path = os.path.splitext(file)[0]
                if file.endswith(".npy"):
                    for l in limit:
                        if l == None:
                            limit_name = "all"
                        else:
                            limit_name = str(l - breakin)
                        data_name = (file_path + '_' + limit_name)
                        out_buffer[data_name] = np.mean(obj[file][breakin:l])
                else:
                    out_buffer[file_path] = obj[file][()]
            data_array.append(out_buffer)
    return data_array
                


def save_data_array(data_array, location):
    df_data = pd.DataFrame(data_array)
    df_data.to_pickle(location + "/gathered_data.pkl")
    df_data.to_csv(location + "/gathered_data.csv")

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: python3 gather_data.py data_file.h5")
    file = sys.argv[1]
    da = process(file)
    save_data_array(da, os.path.dirname(file))
        
        