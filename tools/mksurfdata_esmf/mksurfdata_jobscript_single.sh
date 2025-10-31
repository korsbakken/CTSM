#!/bin/bash
#SBATCH --job-name=mksurfdata_esmf
#SBATCH --acount=nn9188k
#SBATCH --qos=preproc
#SBATCH --time=0:30:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=218G

# This is a batch script to run a set of resolutions for mksurfdata_esmf input namelist
# NOTE: THIS SCRIPT IS AUTOMATICALLY GENERATED SO IN GENERAL YOU SHOULD NOT EDIT it!!

# Run env_mach_specific.sh to control the machine dependent environment including the paths to compilers and libraries external to cime such as netcdf
. /cluster/projects/nn9188k/janko/src/clones/CTSM/tools/mksurfdata_esmf/tool_bld/.env_mach_specific.sh
if [ $? != 0 ]; then echo "Error running env_mach_specific script"; exit -4; fi 
# Edit the mpirun command to use the MPI executable on your system and the arguments it requires 
time srun --kill-on-bad-exit --label  /cluster/projects/nn9188k/janko/src/clones/CTSM/tools/mksurfdata_esmf/tool_bld/mksurfdata < surfdata.namelist 
if [ $? != 0 ]; then echo "Error running for namelist  surfdata.namelist"; exit -4; fi 
echo Successfully ran resolution
