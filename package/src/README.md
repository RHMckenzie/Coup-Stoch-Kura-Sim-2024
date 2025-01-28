## Important information about JSON templates



## Individual Runs

The simulator can be invoked using `python parser.py task1.json [task2.json ...]`, where `task1.json` is a task specified from a json file (such as the one in the json templates), usually a good idea to modify the save_folder location of such things so the final data is autosaved correctly.

the resultant contents should be in the data folder and should be in `.npy` files, these are loadable from `numpy.load()`, otherwise `gather_data.py` can (in cases where the settings.json is preserved) gather the data manually, see also `individual_testrun.sh` in the parent folder.



## Batch Processing

Execution should follow the flow of generator.ipynb -> autorun.py -> combine.py -> gather_data_h5.py.

That is, you first generate the task .json specifications (ideally from a pre-existing template with permutations of parameters), then you run those via the autorun.py script (after modifying the variables within the script), then combine.py should be run to combine the different h5 result files, finally gather_data_h5.py produces the summary statistics from the concatenated output of combine.py

### generator.ipynb

You can utilise the generator.ipynb notebook under the jupyter notebooks, it will try to use final_template to generate a new set of json tests, these are used in the next step.

### autorun.py
Change `job_dist` variable to the number of subjobs you plan on running, set `proj_loc` to be your project location, `folder` is the subfolder under the project location that should store your .json files, my example folder structure `/project/RDS-FEI-TB_NN_INFOTHEORY-RW/rmck6484_thesis/tests` would contain ~200 different test .jsons, equally distributed into `job_dist = 40` different instances, each instance would thus run 5 different .jsons. The result of running these in parallel should be 40 different .h5 files in `/project/RDS-FEI-TB_NN_INFOTHEORY-RW/rmck6484_thesis/data` or `proj_loc/data`.

This is executed via `python3 autorun.py [0-job_dist]` where job_dist is the integer specified in the script, ensure you modify the variables within the script before running or else it won't work.

### combine.py
This is a fairly straight forward script that should combine those 40 .h5 files into a single concatenated .h5 file, fairly straight forward `python3 combine.py outfile.h5 [proj_loc/data]`, the output is a single .h5 file.

### gather_data_h5.py
This script should produce summary statistics from the single .h5 file `outfile.h5` from the previous step and create gathered_data.pkl/gathered_data.csv, Usage: `python3 gather_data.py outfile.h5`.

## TODO: 
* produce example for batch processing 
* modularise autorun variables to be invoked outside