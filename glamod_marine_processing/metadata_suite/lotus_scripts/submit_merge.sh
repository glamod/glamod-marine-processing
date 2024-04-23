#!/bin/bash
#BSUB -J merge_[1-64]
#BSUB -q short-serial
#BSUB -o ./merge_logs/%J_%I.out
#BSUB -e ./merge_logs/%J_%I.err
#BSUB -W 24:00
#BSUB -R "rusage[mem=64000]"
#BSUB -M 64000

source ./setenv0.sh
if [ -f merge_${LSB_JOBINDEX}.success ]
then
    echo ""
    echo "Job previously successful, job not rerun. Remove file 'merge_${LSB_JOBINDEX}.success' to force rerun."
    echo ""
else
    python3 ${scripts_directory}/merge_countries.py -config ${code_directory}/config/config_lotus.json \
        -jobs ${code_directory}/config/jobs.json -countries ${code_directory}/config/countries.json -index ${LSB_JOBINDEX} 
    if [ $? -eq 0 ] 
    then
	    touch merge_${LSB_JOBINDEX}.success
        bsub -w "done(${LSB_JOBID})" mv ./merge_logs/${LSB_JOBID}_${LSB_JOBINDEX}.* ./merge_logs/successful/
        if [ -f  merge_${LSB_JOBINDEX}.failed ]
        then
            rm merge_${LSB_JOBINDEX}.failed
        fi
    else
	    touch merge_${LSB_JOBINDEX}.failed
        bsub -w "done(${LSB_JOBID})" mv ./merge_logs/${LSB_JOBID}_${LSB_JOBINDEX}.* ./merge_logs/failed/
	fi
fi

if [ ${LSB_JOBINDEX} == 1 ]
then
bsub -w "done(${LSB_JOBID})" python3 ${scripts_directory}/combine_master_files.py -config ${code_directory}/config/config_lotus.json \
    -countries ${code_directory}/config/countries.json
fi
