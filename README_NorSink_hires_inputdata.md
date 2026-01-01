# Steps to produce high-resolution grid and input data for NorSink

The following are notes and instructions for how to produce a high-resolution
(0.125x0.125 degrees) grid for Norway and surrounding regions for use in
NorSink, and input data for CLM/CTSM and accompanying models used in the
project.

## Contents
- [Definition of the grid](#definition-of-the-grid)
- [Create grid files and input data for CTSM](#create-grid-files-and-input-data-for-ctsm)
  - [1. Create the SCRIP grid file](#1-create-the-scrip-grid-file)
  - [2. Create a (preliminary) mesh file with triival mask](#2-create-a-preliminary-mesh-file-with-triival-mask)
  - [3. Add new resolution and grid to config files](#3-add-new-resolution-and-grid-to-config-files)
    - [Add resolution name to CTSM namelist definition file](#add-resolution-name-to-ctsm-namelist-definition-file)
    - [Add mesh file path to the nuopc component/model grid definition files](#add-mesh-file-path-to-the-nuopc-componentmodel-grid-definition-files)
  - [4. Run scripts to prepare for running `mksurfdata_esmf`](#4-run-scripts-to-prepare-for-running-mksurfdata_esmf)
    - [a. Compile the `mksurfdata` executable](#a-compile-the-mksurfdata-executable)
    - [b. Create the namelist for `mksurfdata`](#b-create-the-namelist-for-mksurfdata)
    - [c. Create job script for `mksurfdata`](#c-create-job-script-for-mksurfdata)
  - [5. Download missing raw input data](#5-download-missing-raw-input-data)
    - [a. Use (and optionally create) a dummy case directory](#a-use-and-optionally-create-a-dummy-case-directory)
    - [b. Modify download and input file paths to get around missing write permissions](#b-modify-download-and-input-file-paths-to-get-around-missing-write-permissions)
  - [6. Run `mksurfdata` to generate surface data and land use files](#6-run-mksurfdata-to-generate-surface-data-and-land-use-files)
  - [7. Move the generated files to inputdata folders and add to XML databases](#7-move-the-generated-files-to-inputdata-folders-and-add-to-xml-databases)
    - [1. Move the fles to an appropriate input data folder](#1-move-the-fles-to-an-appropriate-input-data-folder)
    - [2. Add the paths to the generated files to the XML databases](#2-add-the-paths-to-the-generated-files-to-the-xml-databases)
- [Run a test case with the new CTSM input data (only)](#run-a-test-case-with-the-new-ctsm-input-data-only)
  - [1. Create the test case](#1-create-the-test-case)


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


## Create grid files and input data for CTSM

**NB!** The sections of the CTSM User Guide that deal with creating new grid
resolutions and input data sets, and various README files in the CTSM tools
directories, are not up to date at the time of writing. Many mention
requirements to create mapping files and domain files, which do not appear to be
required anymore with CTSM 5.3 [*This still needs to be confirmed by completing
the workflow without those files*]. Several outdated scripts such ad
mknoocnmap.pl and mkmapdata.sh.

The current workflow appears to be:

1. Generate a SCRIP grid file for the new resolution.
2. Create a mesh file for the resolution.
3. Enter the new resolution and SCRIP grid file into XML config files. May
   require also creating a mesh file with
   `/tools/site_and_regional/mesh_maker`, and possibly adding a land mask
   and land fractions. Or the mesh file can be passed directly to `mksurfdat_esmf`
   below without adding the resolution to the config files.
4. Run scripts to prepare for running `mksurfdata_esmf` (in
   `/tools/mksurfdata_esmf`):
     a. `gen_mksurfdata_build`, to compile the mksurfdata executable.
     b. `gen_mksurfdata_namelist`, to create namelist for mksurfdata\_esmf
     c. `gen_mksurfdata_jobscript_multi` or `gen_mksurfdata_jobscript_single`,
        to create job script to run mksurfdata\_esmf.
5. Download missing raw input data, using the generated scripts and namelists.
6. Run mksurfdata using the job scripts. Download missing input data as needed.
7. Add land mask and grid cell areas to the mesh file.
8. Move the generated data files to appropriate input data folders, and add them
   to the XML databases.
9. [Add summary of how to add the atmospheric forcing, and any custom bullets on
   the river transport model].

### 1. Create the SCRIP grid file

This step requires installing and activating the Python environment specified in
`pixi.toml` and `pixi.lock` with the following commands:

1. `pixi install`
2. `pixi shell`

`pixi.toml` contains both the dependencies of the main CTSM Python environment
as specified in [/python/conda_env_ctsm_py.yml](./python/conda_env_ctsm_py.yml)
and some additional dependencies that are required for other steps in this
guide (notably using
[/tools/surfdat_landfrac_to_mesh_mask.py](./tools/surfdat_landfrac_to_mesh_mask/surfdat_landfrac_to_mesh_mask.py)
to add a land mask and cell areas to the mesh file).

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

On betzy, the SCRIP file was moved from `${CTSMROOT}/tools/mkmapgrids/` to
`/cluster/shared/noresm/inputdata/cicero_mods/share/scripgrids/`.

### 2. Create a (preliminary) mesh file with triival mask

The SCRIP grid file from the previous file is used to produce a mesh file with a
trivial mask (1 everywhere), and without a field for the grid cell areas (since
the SCRIP file from the previous step does not contain one). We need a mesh file
to create the surface data set, but the surface data contains its own land
fraction data and does not need a mask. We will then later use the surface data
set to add a land mask to the mesh file, and at the same time compute and add
grid cell areas.

The preliminary mesh file is produced with the following commands, where
`[ESMF_module]` is replaced with a suitable module that enables the
`ESMF_Scrip2Unstruct` command, `[scrip_file]` is replaced by the full path to
the SCRIP file from the previous section, and `[output_esmf_file]` is replaced
with the desired path and name of the output ESMF mesh file):

```
module load [ESMF_module]
ESMF_Scrip2Unstruct [scrip_file] [output_esmf_file] 0
```

The `0` at the end of the `ESMF_Scrip2Unstruct` command tells the converter that
we want a straight grid conversion where grid cell center coordinates remain
element centers, and grid cell corners are mapped to corners/nodes. The opposite
would be `1` for a dual grid, where the corners are used as element centers and
the grid cell centers of the SCRIP grid as nodes.

On betzy, the following commands were used after changing to the directory
`/cluster/shared/noresm/inputdata/cicero_mods/share/scripgrids/`

```
module load ESMF/8.8.0-iomkl-2022a-ParallelIO-2.6.5
ESMF_Scrip2Unstruct ./SCRIPgrid_NorwayRect_0.125x0.125_nomask_c251026.nc ../meshes/ESMFmesh_NorwayRect_0.125x0.125_nomask_c251031.nc 0
```

### 3. Add new resolution and grid to config files

The new resolution was then added to XML configuration/database files in the
following way:

#### Add resolution name to CTSM namelist definition file

In `/bld/namelist_files/namelist_definition_ctsm.xml`, the new resolution name
must be added to the entry `res`. Find the the XML `<entry>` tag that has the
attribute `id="res"`, and add the new resolution name to the comma-separated
list (without any added spaces) in the `valid_values=` attribute.

On Betzy, the name `NorwayRect_0.125x0.125` was added. This will be used in the
remainder of this guide.

#### Add mesh file path to the nuopc component/model grid definition files

In `/ccs_config/component_grids_nuopc.xml` add a `<domain>` with the mesh file
from point 2 in the `<domains>` section. The following tag was added on betzy
(after `<domains>` and before `</domains>`):

```
  <domain name="NorwayRect_0.125x0.125">
    <nx>217</nx>  <ny>112</ny>
    <mesh>$DIN_LOC_ROOT/cicero_mods/share/meshes/ESMFmesh_NorwayRect_0.125x0.125_nomask_c251031.nc</mesh>
    <desc>0.125x0.125 degree rectangular grid containing Norway and all rivers that drain from Norway -- only valid for DATM/CLM compset</desc>
  </domain>
```

Then add aliases for the grid name in `/ccs_config/modelgrid_aliases_nuopc.xml`.
The following was added on betzy:

```
  <model_grid alias="NorwayRect_0.125x0.125">
    <grid name="atm">NorwayRect_0.125x0.125</grid>
    <grid name="lnd">NorwayRect_0.125x0.125</grid>
    <grid name="ocnice">NorwayRect_0.125x0.125</grid>
    <mask>null</mask>
  </model_grid>
```

### 4. Run scripts to prepare for running `mksurfdata_esmf`

The following steps need to be taken to build and configure mksurfdata\_esmf
before running it to produce the input surface data:

#### a. Compile the `mksurfdata` executable

This works more or less out of the box as described in
`/tools/mksurfdata_esmf/README.md` provided the machine you are running on is
configured correctly in `/ccs_config/machines`. Just cd to
`/tools/mksurfdata_esmf` and run `./gen_mksurfdata_build`, but note below for
betzy.

**NB!** On betzy, there is some issue with the files included in the PIO module.
The build process that is run by `gen_mksurfdata_build` expects to find dymamic
library files `libpioc.so` and `libpiof.so`. These don't appear to exist in the
configured modules for betzy, and not in any other available modules either.
Instead, only the files `libpioc.a` and `libpiof.a`, which presumably are the
corresponding statically linked libraries. This issue appears to be resolvable
by simply changing `libpioc.so` to `libpioc.a` and `libpiof.so` to `libpiof.a`
on lines 53 and 54 of `/tools/mksurfdata_esmf/src/CMakeLists.txt`. The
executable compiles successfully after doing so (already done in the commit
where this text was composed).

#### b. Create the namelist for `mksurfdata`

Assuming the new grid resolution and mesh file have been added to the XML files
as described previously, the namelist used by `mksurfdata` can be generated with
the following command (while in the directory `/tools/mksurfdata_esmf/`):

```
./gen_mksurfdata_namelist -v --start-year 1850 --end-year 2023 --res NorwayRect_0.125x0.125 --rawdata-dir /cluster/shared/noresm/inputdata --inlandwet
```

Replace `NorwayRect_0.125x0.125` with the desired resolution name if using a
different resolution or name, and the path after `--rawdata-dir` with the path
to the root of the input data directory (`$DIN_LOC_ROOT`) if running on a
different machine than betzy with a different input data path.

The command will output a file called `surfdata.namelist` in current directory.

In the output `surfdata.namelist`, check the name after `hostname` and correct
it if necessary. On betzy, this is originally set to the name of the login
node, but should be replaced by `'betzy'`.

Note that the xml file used to set the paths of the raw nput data,
`/tools/mksurfdata_esmf/gen_mksurfdata_namelist.xml`, contained some hardcoded
absolute paths to `/glade/campaign` (a data area at NCAR, presumably). This was
corrected to relative paths that should give the correct paths in
`surfdata.namelist` after running `gen_mksurfdata_namelist`, but check whether
any absolute paths from NCAR's machines persist if you get error messages.

#### c. Create job script for `mksurfdata`

A job script is required to run `mksurfdata` on a compute node. A starting
point can be generated with the script `gen_mksurfdata_jobscript_single` (in
the `/tools/mksurfdata_esmf` folder), but this generates a job script for
NCAR machines and the scheduling system that the use, not for betzy and not for
SLURM.

A job script adapted for betzy and SLURM can be found at
`/tools/mksurfdata_esmf/mksurfdata_jobscript_single_betzy_janko.sh`. You may
need to adjust the time allocation depending on what you want to generate
(or if the time expires before the job finishes, or next time if you finish
with a lot of time left over). This in particular depends on whether you
generate input files for transient land use, or just the surface data input
file, since the land use files require separate files for each model year
and can take a long time to generate.

The time is adjusted by changing the line that starts with `#SBATCH --time=`,
and setting the requested wall time in format `h:mm:ss`.

In the run made by `korsbakken` on betzy, the surface data file itself was
generated after less than 20 minutes, while processing data for the land use
file took more than 4 minutes per year, and a total of 12.6 hours for the period
1850--2023.

The job script included in the commit at the time of writing has the time
allocation set to 1&nbsp;hour. If you only want to generate a surface data file
and no land use files, 30&nbsp;minutes (`0:30:00`) will probably be more than
enough.


### 5. Download missing raw input data

The previous steps generates a file called `.input_data_list` in
`/tools/mksurfdata_esmf` with a list of required input data files. Check that
there are no error messages or anything funny-looking in this file.

Assuming `.input_data_list` looks reasonable, you would normally check for the
required input files and download missing ones by running the script
`download_input_data` in `/tools/mksurfdata_esmf`. **However**, the Python code
called by this script contains what looks like some temporary hacks that require
yo to have a dummy case directory that the script can plug into to use the same
download code that is used when submitting cases to be run. **Furthermore**, the
module `mksurfdata_download_input_data.py` (in `/python/ctsm/`) hardcodes the
path to this dummy directory to be a subdirectory of the home directory of
Samuel Levis (`slevis`) at UCAR. Which presumably works on NCAR machines, but
obviously not on betzy or any sigma2 machine. This hack was still present in the
master branch of CTSM in November 2025, and had been there for at least three
years at that point.

We have not yet patched the code to remove the need for a dummy case directory,
but `mksurfdata_download_input_data.py` in the current branch (where this README
is found) has been modified to allow using a different dummy case directory,
which must be created in advance and passed to `download_input_data` through a
new and required `--dummycasedir` argument.

On betzy, there may also be issues with write permissions on individual
subdirectories of the shared NorESM inputdata directory
(`/cluster/shared/noresm/inputdata`) that will block `download_input_data` from
writing downloaded data to the required locations. Basically, some
subdirectories end up belonging to the personal file group of the user who first
created them and/or having write permissions only for that user. This will
prevent you from downloading new input data files if the generated input data
list requires them to be written into the affected subdirectories.

Until these problems are fixed, the following two sets of extra steps are
therefore necessary for `download_input_data` to succeed, and for `mksurfdata`
to be able to use the downloaded data:

#### a. Use (and optionally create) a dummy case directory

If you already have run a case with CTSM 5.3 on betzy and have a case directory
that is compatible with that CTSM version, you can use this to run
`download_input_data` as follows (while in `/tools/mksurfdata_esmf`):

```
./download_input_data --dummycasedir CASEDIR
```
where you replace `CASEDIR` with the absolute path to your case directory.
Probably, any case directory that is compatible with CTSM 5.3 should work, but
if you run in to problems, try creating a new case directory from scratch to see
if that helps. It does not matter what compset or resolution you use, the
directory just has to be any valid case directory.

If you haven't created a case for CTSM 5.3 before, you need to do so.
Preferrably using `create_newcase` from this repository to ensure that the
versions used are consistent.

#### b. Modify download and input file paths to get around missing write permissions

If the log or error messages says that some files could not be downloaded or
could not be written when running `download_input_data`, check whether you have
write permissions to the directory that is being downloaded to. If not, the most
sustainable option is to get in touch with the user or users who own each
affected directory, and ask them to

1. Change the group of the directory and everything in it to `noresm` if it does
   not already belong to it:
   ```
   chgrp -R noresm dirname
   ```
   where `dirname` is the name of the outermost directory that does not have the
   right group or permissions.

2. Give write permissions to the group to everything, and `s` and `x` permission
   for all directories:
   ```
   chmod -R g+w dirname
   find dirname -type d -exec chmod g+sx {} \;
   ```
   where again `dirname` is replaced with the path of the outermost directory
   that does not have the right permissions.

If this is not feasible in a reasonable amount of time (which it may not be,
since there may be many different users involved), you can create an alternate
directory with the right group and permissions (if it does not already exist,
see below), and then manually change the affected paths in the following files:
* `.input_data_list`
* `surfdata.namelist`
* The list of land use files (`landuse_timeseries_hist_*.txt`, where the `*`
  depends on the years and number of pfts).

This problem did arise in the run on betzy in November 2025. This was "solved"
by creating a separate directory called `rawdata_norsink_tmp` under
`/cluster/shared/noresm/inputdata/`, parallel to the main rawdata folder
`/cluster/shared/noresm/inputdata/rawdata/`. If this folder is still there, it
should have the correct group and permissions set, and persumably have a lot of
the files that are needed already. It can be reused to avoid redownloading and
duplicating files unnecessarily.


### 6. Run `mksurfdata` to generate surface data and land use files

If all downloads completed successfully, everything should be ready to run
`mksurfdata` and generate the surface data and land use input files.

Before running, check that the settings in the job script file (e.g., modelled
after `mksurfdata_jobscript_single_betzy_janko.sh`) are appropriate. In
particular, check the following:

1. **That the paths to `.env_mach_specific.sh` and the `mksurfdata` executable are set correctly.**
   There is one line that sources the script `.env_mach_specific.sh` to set the
   correct environment, and one that runs `mksurfdata` itself (starting with
   `time srun ...` and containing a path to `mksurfdata`). In the example job
   script used by `janko` in this branch, there are absolute paths to the
   location of the repo in the home folder of the user `janko` on these lines,
   and they must be chaned to the absolute paths of `.env_mach_specific.sh`` and
   `mksurfdata` under the `mksurfdata_esmf` folder where you have your clone of
   the repo.
2. **That the `SBATCH` parameters at the top of the job script are appropriate.**

   The following parameters were used for the run on betzy in November 2025, for
   generating both a surface data and land use file:
   ```
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
   ```
   The actual run took 12.6 hours of wall time in total. The surface data file
   was generated after about 15 minutes of runtime, the remaining time was spent
   generating the land use file.

Then submit the job with the command `sbatch ./jobscriptname.sh` (replace
`./jobscriptname.sh` with the actual path to your jobscript file) and wait for
the job to start and finish. Once it starts, the job will create a log file in
your current directory with the form `surfdata_*cYYMMDD.log` which will be added
to as the job runs. You can tail this file to monitor the progress.

***
**NB! Missing year numbers in land use file**

The land use file (`landuse.timeseries_*.nc`) generated by `mksurfdat` contains
a `time` dimension with one point per year, as well as a 1-d variable named `YEAR` that
presumably should contain year numbers. The dimension contains the expected
number of points (one per year), but the values of both `YEAR` and the `time`
coordinate variable itself are for some reason all 0. This can presumably be
rectified by manually changing the `YEAR` and/or `time` variable to have the
correct values.
***

If the `mksurfdata` job finishes successfully, it will put a surface data file
and a land use in the `/tools/mksurfdata_esmf` folder, with names of the form
`surfdata_*_cYYMMDD.nc` and `landuse.timeseries_*_cYYMMDD.nc`, respectively. For
the grid used in the November 2025 run, these should be roughly 800 MB and 7.3
GB, respectively.

### 7. Move the generated files to inputdata folders and add to XML databases

Do the two following steps to use the generated input files (the last one is
required only for later convenience):

#### 1. Move the fles to an appropriate input data folder

Move these two files (and optionally also the log file) to the inputdata folder
where you want to use them. There is no absolute requirement for where to place
them, butthe data generated in November 2025 in NorSink on betzy were moved to
`/cluster/shared/noresm/inputdata/cicero_mods/surfdata_esmf/ctsm5.3.0/`.

In general on betzy, we use folders under `/cluster/shared/noresm/inputdata/`
for input files that all noresm users on betzy should have access to, and
specifically the subfolder `cicero_mods` for files that have been modified or
created by CICERO for special purposes.

#### 2. Add the paths to the generated files to the XML databases

In order to use the new grid and the new input data files in scripts such as
`create_newcase`, they need to be added to
`/bld/namelist_files/namelist_defaults_ctsm.xml` (if not, you will need to
specify them manually when creating a case):

1. Add the path to the surface data file in an `<fsurdat>` field, with appropriate options for `sim_year` and `use_crop`.
   For the `NorwayRect_0.125x0.125` grid and files created in November 2025 on betzy, the following lines were added:
   ```
   <fsurdat hgrid="NorwayRect_0.125x0.125" sim_year="1850" use_crop=".true." >
   cicero_mods/surfdata_esmf/ctsm5.3.0/surfdata_NorwayRect_0.125x0.125_hist_1850_78pfts_c251102.nc</fsurdat>
   ```

2. Add the path to the land use file in an `<flanduse>` field. For the
   `NorwayRect_0.125x0.125` grid and files created in November 2025 on betzy,
   the following lines were added:
   ```
   <flanduse_timeseries hgrid="NorwayRect_0.125x0.125" sim_year_range="1850-2023">
   cicero_mods/surfdata_esmf/ctsm5.3.0/landuse.timeseries_NorwayRect_0.125x0.125_hist_1850-2023_78pfts_c251102.nc</flanduse_timeseries>
   ```


## Run a test case with the new CTSM input data (only)

This section describes how to set up and run a case to test the new input data
for CTSM but with a standard meteorological forcing dataset for DATM (the
atmosphere data model), before creating a new high-resolution forcing data set.
In the test case, CTSM will run on the new high-resolution grid, while DATM runs
on a standard lower-resolution grid, relying on dynamic regridding during the
run to map the atmosphere forcing data onto the land grid.

### 1. Create the test case

Before continuing, ensure that you have `/cime/scripts/` under the CTSM repo
folder added to your `PATH` environment variable, and ensure that it is earlier
in PATH than any directories that might contain different versions of the CIME
scripts.

Also ensure that you have a shell where you have activated the pixi
Python environment (e.g., test by typing `type python` and check that the Python
binary path it returns is in your pixi environment folder, or check whether your
command line prompt starts with `(ctsm_pylib)` or `(ctsm_pylib:dev)`). Activate
it if not (`pixi shell -e dev` while in the root folder of the CTSM repo).

We create a test case with using a customized compset that uses CLM5, MOSART
(river model), DATM for forcing, and stub components for everything else, with
1850 surface data but no initial conditions file (we will be spinning up the
model later). We use `BGC-CROP` settings for CLM, and the historical data set
used for spinup with DATM (`CPLHIST`). The land and atmosphere model are run on
the new grid, the river model on the `r05` grid, and other model on a `null`
grid (being stubs). The overall mask is set to that of the new grid.

To to the directory where you want to create the new case directory as a
subdirectory and give the following command (replace `NorwayRect_0.125x0.125`
with the name of your new grid if you chose a different name, and
`test_NorwayRect_simple_case` with a different case name if desired):

```
create_newcase \
  --case test_NorwayRect_simple_case_nullmask \
  --compset '1850_DATM%CPLHIST_CLM50%BGC_SICE_SOCN_MOSART_CISM2%NOEVOLVE_SWAV' \
  --res 'a%NorwayRect_0.125x0.125_l%NorwayRect0.125x0.125_r%r05_g%gland4_oi%null_w%null_z%null_m%null' \
  --machine betzy \
  --project nn9188k \
  --run-unsupported \
  --walltime '0:30:00'
```

