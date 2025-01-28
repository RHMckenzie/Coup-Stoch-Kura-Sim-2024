#!/bin/bash
DATE_VAR=`date --rfc-3339="date"`
cd ~/jobresults
qsub -v "FOLDER=${1:?Please use: ./gather_data.sh h5_file}" -N "gather_data_$1" ~/jobs/gather_data.pbs
