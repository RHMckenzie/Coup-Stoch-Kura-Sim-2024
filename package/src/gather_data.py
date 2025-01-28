# Short Script that is pointed at a data folder containing numerious runs from subfolders, 
# constructs a csv/pkl of summary data

import numpy as np
import pandas as pd
import os
import tqdm
import sys
import json

def gather_data(folder, breakin = 100, adv_desc = False, desc = True):
    if desc:
        try:
            # initial attempt
            _s = lambda x: x.split('-')[1]
            n  = folder.split("_")
            desc = [_s(n[i]) for i in range(-3, 0)]
        except:
            # not named folder, use settings.json
            print("Non-instanced folder name, falling back")
            try:
                with open(folder + "/settings.json", 'r') as f:
                    js = json.load(f)
                    print(js)
                #Example, extract settings from settings.json
                grp_a = js["graph"]["arguments"]
                grp_s = js["graph"]["settings"]
                desc = []
                desc.append(grp_a["p"])
                desc.append(js["processes"][0]["arguments"]["zeta"])
                desc.append(grp_s["cross_couple_value"])

            except FileNotFoundError as err:
                print(f"Unexpected {err=}, {type(err)=}")
                return None


    try:
        k_f = np.load(folder + "/kuramoto_euler_sigma_squared.npy")
        l_f = np.load(folder + "/ou_euler_sigma_squared.npy")
        k_m = k_f[-breakin:].mean()
        l_m = l_f[-breakin:].mean()
        with open(folder + "/analytical_sigma_cont.dat", "r") as f:
            s_c = float(f.readline())
    except FileNotFoundError as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return None
    out = {
        "kuramoto_sigma_squared": k_m,
        "linear_sigma_squared": l_m,
        "analytical_sigma_continuous": s_c
        }
    if desc and not adv_desc:
        out.update({
            "p": desc[0],
            "zeta" : desc[1],
            "c" : desc[2]})
    elif adv_desc:
        out = {
            "desc": 
                {"p": desc[0],
                "zeta" : desc[1],
                "c" : desc[2]},
            "data": out
        }
    return out
    
def process(folder, breakin = 1000):
    data_array = []
    folders = os.listdir(folder)
    for folder_name in folders:
        f = folder + "/" + folder_name
        print("Reading: " + str(f))
        data = gather_data(f)
        if data is None:
            print("Ommiting " + str(f))
            continue
        data_array.append(data)
    return data_array

def save_data_array(data_array, location):
    df_data = pd.DataFrame(data_array)
    df_data.to_pickle(location + "/gathered_data.pkl")
    df_data.to_csv(location + "/gathered_data.csv")

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("Usage: python3 gather_data.py data_folder")
    folder = sys.argv[1]
    da = process(folder)
    save_data_array(da, folder)
        
        