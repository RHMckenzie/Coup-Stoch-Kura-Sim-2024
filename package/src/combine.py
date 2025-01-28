import h5py
import sys
import os
from tqdm import tqdm
def unify(folder, unified_file, write = True):
    with h5py.File(unified_file, 'w' if write else 'a') as hf_out:
        files = os.listdir(folder)
        files = filter(lambda x: x.endswith('.h5'), files)
        files = tqdm(files)
        for filename in files:
            print("Reading", filename)
            with h5py.File(os.path.join(folder, filename), 'r') as hf_in:
                for k in hf_in.keys():
                    hf_out.copy(hf_in[k], hf_out)

def combine_folders(folder_list, outfile):
    print("combining folders")
    folder_list = folder_list.copy()
    f = folder_list.pop(0)
    print("Unifying", f)
    unify(f, outfile)
    for f in folder_list:
        print("Unifying", f)
        unify(f, outfile, write = False)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 combine.py outfile.h5 folder1 folder2 ...")
        sys.exit(1)
    print("Running for " + str(len(sys.argv) - 2) +" Folders")
    folders = sys.argv[2:]
    file = sys.argv[1]
    combine_folders(folders, file)