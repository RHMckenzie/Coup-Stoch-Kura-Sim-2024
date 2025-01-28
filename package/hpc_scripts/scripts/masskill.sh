USER=rmck6484
for i in `qstat -au ${USER} | cut - -d '.' -f 1 | tail -n +6`
do 
	echo $i
	qdel $i
done
