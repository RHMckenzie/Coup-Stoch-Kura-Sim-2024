#!/bin/bash
DATE_VAR=`date --rfc-3339="date"`
cd ~/jobresults
if [ $# -lt 2 ]; then
	echo "a list of Files is required"
	exit 1
fi
echo ${1:?}
FOLD=${@:2}
echo $FOLD
qsub -v "FILE=${1:?},FOLDERS=$FOLD" -N "Data_aggregation_for_$1" ~/jobs/combine_data.pbs
