#!/bin/bash
DATE_VAR=`date --rfc-3339="date"`
PROJ_LOC=/project/TB_NN_INFOTHEORY/rmck6484_thesis

mv ${PROJ_LOC}/data ${PROJ_LOC}/data-${DATE_VAR}
mkdir ${PROJ_LOC}/data

cd ~/jobresults
mkdir ${DATE_VAR}
cd ${DATE_VAR}

qsub ~/jobs/py_auto_array.pbs

