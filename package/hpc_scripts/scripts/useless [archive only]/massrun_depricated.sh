#!/bin/bash
DATE_VAR=`date --rfc-3339="date"`
cd ~/jobresults
for j in {0..4}
do
	for i in {0..39}
	do
		echo "For Batch $j, Dispatching job $i"
		qsub -v "BATCH_NUM=${i},CYCLE=${j}" -N "${DATE_VAR}_run_${j}_batch_${i}" ~/jobs/py_auto.pbs	
	done
	sleep 2
done
