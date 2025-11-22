#!/bin/bash
#SBATCH --account=nn9188k
#SBATCH --job-name=mksurfdata_esmf
#SBATCH --qos=preproc
#SBATCH --partition=preproc
#SBATCH --time=17:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=175G

# This is a batch script to run a set of resolutions for mksurfdata_esmf input namelist

# Run env_mach_specific.sh to control the machine dependent environment including the paths to compilers and libraries external to cime such as netcdf
. /cluster/home/janko/src/CESM_repos/CTSM/tools/mksurfdata_esmf/tool_bld/.env_mach_specific.sh
if [ $? != 0 ]; then echo "Error running env_mach_specific script"; exit -4; fi 
# Edit the mpirun command to use the MPI executable on your system and the arguments it requires 
time srun --kill-on-bad-exit --label  /cluster/home/janko/src/CESM_repos/CTSM/tools/mksurfdata_esmf/tool_bld/mksurfdata < surfdata.namelist 
if [ $? != 0 ]; then echo "Error running for namelist  surfdata.namelist"; exit -4; fi 
echo Successfully ran resolution
