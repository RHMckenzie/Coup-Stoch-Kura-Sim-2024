A set of misc. scripts designed to assist me in running parallel instances of the simulations on the USYD HPC Cluster, scripts are divided into the following:

## Scripts
The scripts that launch the instances on openPBS.
* combine_data.sh: launches the aggregates data in all the given folders into the file (file is first argument, folders are second argument onwards)
* gather_data.sh: turns the given h5 file into a data summary in a csv and pkl file.
* jobcheck.sh: misc. script to check status of jobs on openPBS.
* masskill.sh: misc. script that kills all jobs on openPBS 
* massrun.sh: script that runs all my simulations via py_auto_array.

## Jobs
The instances ran by the scripts on openPBS
* combine_data.pbs: a script that runs combine.py, designed to combine .h5 files in existing folders into a single .h5 file (for data aggregation)
* gather_data.pbs: a script that runs gather_data_h5.py, turning a h5 file into it's summaries (which can be analysed easier)
* interactive.pbs: job to launch interactive session for openPBS, useless otherwise.
* py_auto_array.pbs: job that launches an "array job" or 200 batch jobs of autorun.py, runs the simulator for runs.
* py_setup.pbs: job for setting up the environment.
* remove_data.pbs: job for deleteing the data folder

