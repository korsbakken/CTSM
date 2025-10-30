# Steps to produce high-resolution grid and input data for NorSink

The following are notes and instructions for how to produce a high-resolution
(0.125x0.125 degrees) grid for Norway and surrounding regions for use in
NorSink, and input data for CLM/CTSM and accompanying models used in the
project.

## Definition of the grid

The grid is defined to be a 0.125x0.125 degree grid that is quadratic in
latitude/longitude space and includes all of the Norwegian mainland and adjacent
islands, as well as the course of any rivers that can transport
carbon-containing material from Norwegian territory until they drain into the
ocean.

Towards the west, north and east, this is achieved by setting longitude/latitude
limits that enclose Norway itself, since Norway has no land borders to the west
or north, and no rivers that flow out from Norway (all of which flow into
Sweden) extend further east than to the bay of Bothnia, which is entirely
contained within any rectangular region that includes all of Norway. To the
south, the grid must be extended to where the southernmost course of the Göta
Älv drains into Kattegat at Gothenburg, since some rivers in eastern Norway
flow into Sweden and eventually empty into lake Vänern, which in turn is drained
by the Göta Älv. No rivers that carry water originating from Norway extend any
further south than that.

The grid is set to be the smallest grid that fulfills the criteria above, *and*
that starts and ends on multiples of 0.125 degrees in both latitude and
longitude.

These definitions produce the following limits for the grid:
* **West**: 4.375 E (constrained by Steinsøyna in the Utvær archipelago, in Solund,
  Vestland, which extends a few meters west of 4.5 E)
* **East**: 31.25 E (constrained by the easternmost point of Hornøya in Vardø,
  Finnmark, at about 31.17 E)
* **South**: 57.5 N (constrained by the mouth of the Göta Älv at Gothenburg,
  Sweden. The mouth of the river itself is at around 57.68 N, but we extend this
  a little further to allow for possible transport of sediment further south in
  the archipelago outside of Gothenburg).
* **North**: 71.25 N (constrained by the northernmost point of the minor island
  Avløysa at Kinnarodden on Magerøya, Finnmark, at around 71.13 N).

These limits are taken to be constraints on the *centers* of the grid cells.
I.e., the grid cells at the edges have center latitudes and/or longitudes equal
to those listed above, while the grid corners on the edges have latitudes and/or
longitudes 0.0625 degrees beyond those values.


## Steps before creating the surface data set

**NB!** The sections of the CTSM User Guide that deal with creating new grid
resolutions and input data sets, and various README files in the CTSM tools
directories, are not up to date at the time of writing. Many mention
requirements to create mapping files and domain files, which do not appear to be
required anymore with CTSM 5.3 [*This still needs to be confirmed by completing
the workflow without those files*]. Several outdated scripts such ad
mknoocnmap.pl and mkmapdata.sh.

The current workflow appears to be:

1. Generate a SCRIP grid file for the new resolution.
2. Enter the new resolution and SCRIP grid file into XML config files. May
   require also creating a mesh file with
   `/tools/site_and_regional/mesh_maker`, and possibly adding a land mask
   and land fractions. Or the mesh file can be passed directly to `mksurfdat_esmf`
   below without adding the resolution to the config files.
3. Run scripts to prepare for running `mksurfdata_esmf` (in
   `/tools/mksurfdata_esmf`):
     a. `gen_mksurfdata_build`, to compile the mksurfdata executable.
     b. `gen_mksurfdata_namelist`, to create namelist for mksurfdata\_esmf
     c. `gen_mksurfdata_jobscript_multi` or `gen_mksurfdata_jobscript_single`,
        to create job script to run mksurfdata\_esmf.
4. Run mksurfdata using the job scripts. Download missing input data as needed.
5. Move the generated data files to appropriate input data folders, and add them
   to the XML databases.
6. [Add summary of how to add the atmospheric forcing, and any custom bullets on
   the river transport model].

### 1. Create the SCRIP grid file

This step requires installing and activating the Python environment specified in
`pixi.toml` and `pixi.lock` with the following commands:

1. `pixi install`
2. `pixi shell`

Creating the SCRIP grid file only requires the `ncl` package in the Python
environment and its dependencies. But if you also want to use the packages in
the dev environment, then replace the last command with `pixi shell -e dev`.

Then go to the directory `/tools/mkmapgrids/` and call the following command:

`PRINT=TRUE PTNAME="NorwayRect_0.125x0.125" W_LON=4.3125 E_LON=31.3125 S_LAT=57.4375 N_LAT=71.3125 NX=216 NY=111 ncl ./mkscripgrid.ncl`

See `/tools/mkmapgrids/README` for an explanation of the environment variables
that are set prior the `ncl` command.

These commands will produce an output file named
`SCRIPgrid_NorwayRect_0.125x0.125_nomask_cYYMMDD.nc` (with YYMMDD replaced by
the current date) in the folder /tools/mkmapgrids/.

**NB!** The commands above produce a SCRIP file without a land mask (or, more
precisely, a land mask that is 1 for every grid cell) and no land fraction data.
At the time of writing this (2025-10-27) it is not yet clear whether we need to
add a land mask and/or land fraction, or whether this can be taken from the raw
data files when generating the surface data set.

### 2. Add new resolution and grid to config files

On betzy, the SCRIP file produced in the previous step was moved from
`${CTSMROOT}/tools/mkmapgrids/` to
`/cluster/shared/noresm/inputdata/cicero_mods/share/scripgrids/`.

The new resolution was then added to XML configuration/database files in the
following way:

#### Add resolution name to CTSM namelist definition file

In `/bld/namelist_files/namelist_definition_ctsm.xml`, the new resolution name
must be added to the entry `res`. Find the the XML `<entry>` tag that has the
attribute `id="res"`, and add the new resolution name to the comma-separated
list (without any added spaces) in the `valid_values=` attribute.

On Betzy, the name `NorwayRect_0.125x0.125` was added. This will be used in the
remainder of this guide.

