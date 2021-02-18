mksurfdata_map was built using the following commands:

module purge; module load netCDF-Fortran/4.4.4-intel-2018a-HDF5-1.8.19  
# (actually this may have been netCDF/4.4.1.1-intel-2018a-HDF5-1.8.19)
export INC_NETCDF=/cluster/software/netCDF-Fortran/4.4.4-intel-2018a-HDF5-1.8.19/include/
export LIB_NETCDF=/cluster/software/netCDF-Fortran/4.4.4-intel-2018a-HDF5-1.8.19/lib/
gmake

