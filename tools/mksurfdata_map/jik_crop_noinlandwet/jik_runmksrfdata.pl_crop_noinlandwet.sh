# Command used to build the surface data set with crop, without inland wetlands
./mksurfdata.pl -hirespft -years 2005 -dinlc /cluster/projects/nn9188k/cesm2.0/inputdata -res usrspec -usr_gname Fennoscandia0.05x0.1 -usr_gdate 201123 -usr_mapdir /cluster/projects/nn9188k/cesm2.0/inputdata/cicero_mods/lnd/clm2/mappingdata/maps/Fennoscandia0.05x0.1 2>&1 | tee jikrun_mksurfdata.pl_$(jiktimestr).log
