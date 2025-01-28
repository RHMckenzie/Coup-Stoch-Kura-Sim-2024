#!/bin/bash
DATE_VAR=`date --rfc-3339="date"`
cd ~/jobresults
qsub -v "LIMIT=$2,DATA_LOC=$1" -N "Data_aggregation_for_$2_$1" ~/jobs/gather_data_adv.pbs
