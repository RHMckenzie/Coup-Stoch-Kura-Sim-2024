## Important information about JSON templates



## Individual Runs

The simulator can be invoked using `python parser.py task1.json [task2.json ...]`, where `task1.json` is a task specified from a json file (such as the one in the json templates), usually a good idea to modify the save_folder location of such things so the final data is autosaved correctly.

the resultant contents should be in the data folder

## Batch Processing

Execution should follow the flow of generator.ipynb -> autorun.py -> combine.py -> gather_data_h5.py.

That is, you first generate the task .json specifications (ideally from a pre-existing template with permutations of parameters), then you run those via the autorun.py script (after modifying the variables within the script), then combine.py should be run to combine the different h5 result files, finally gather_data_h5.py produces the summary statistics from the concatenated output of combine.py

### generator.ipynb

You can utilise the generator.ipynb notebook under the jupyter notebooks

### autorun.py
Change `job_dist` variable to the number of subjobs you plan on running, set `proj_loc` to be your project location, `folder` is the subfolder under the project location that should store your .json files, my example folder structure `/project/RDS-FEI-TB_NN_INFOTHEORY-RW/rmck6484_thesis/tests` would contain ~200 different test .jsons, equally distributed into `job_dist = 40` different instances, each instance would thus run 5 different .jsons.

###