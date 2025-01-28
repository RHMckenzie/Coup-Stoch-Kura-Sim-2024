The entire simulator package for the thesis, including:

### src
The main meat and bones of the python process for the package, if you plan on running this simulator you will want to read the README.md contained within.

### HPC scripts
Bash Scripts and OpenPBS Jobs ran by the high-performance compute cloud "Artemis" designed to execute python files in parallel

### JSON templates
For writing your own simulations/running test examples

### Jupyter Notebooks
For analysing data and mass modifying JSON templates

### Additional Demonstrations
`testrun.sh` contained in this will run two consecutive simulations from `json_templates/test.json` and save the data to folders within this directory.