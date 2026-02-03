# Steps to produce high-resolution grid and input data for NorSink

The following are notes and instructions for how to produce a high-resolution
(0.1x0.1 degrees) grid for Norway and surrounding regions for use in NorSink,
and input data for CLM/CTSM and accompanying models used in the project.

## Contents
- [Definition of the grid](#definition-of-the-grid)
- [Create the Python enironment](#create-the-python-enironment)
- [Create grid files and input data for CTSM](#create-grid-files-and-input-data-for-ctsm)
  - [1. Create the SCRIP grid file](#1-create-the-scrip-grid-file)
    - [1.a Legacy method using `/tools/mkmapgrids/mkscripgrid.ncl`](#1a-legacy-method-using-toolsmkmapgridsmkscripgridncl)
  - [2. Create a (preliminary) mesh file with triival mask](#2-create-a-preliminary-mesh-file-with-triival-mask)
  - [3. Add new resolution and grid to config files](#3-add-new-resolution-and-grid-to-config-files)
    - [Add resolution name to CTSM namelist definition file](#add-resolution-name-to-ctsm-namelist-definition-file)
    - [Add the prelminiary, nomask mesh file path to the nuopc component/model grid definition files](#add-the-prelminiary-nomask-mesh-file-path-to-the-nuopc-componentmodel-grid-definition-files)
  - [4. Run scripts to prepare for running `mksurfdata_esmf`](#4-run-scripts-to-prepare-for-running-mksurfdata_esmf)
    - [a. Compile the `mksurfdata` executable](#a-compile-the-mksurfdata-executable)
    - [b. Create the namelist for `mksurfdata`](#b-create-the-namelist-for-mksurfdata)
    - [c. Create job script for `mksurfdata`](#c-create-job-script-for-mksurfdata)
  - [5. Download missing raw input data](#5-download-missing-raw-input-data)
    - [a. Use (and optionally create) a dummy case directory](#a-use-and-optionally-create-a-dummy-case-directory)
    - [b. Modify download and input file paths to get around missing write permissions](#b-modify-download-and-input-file-paths-to-get-around-missing-write-permissions)
  - [6. Run `mksurfdata` to generate surface data and land use files](#6-run-mksurfdata-to-generate-surface-data-and-land-use-files)
  - [7. Add land mask and grid cell areas to the mesh file](#7-add-land-mask-and-grid-cell-areas-to-the-mesh-file)
  - [8. Move the generated files to inputdata folders and add to / adjust XML databases](#8-move-the-generated-files-to-inputdata-folders-and-add-to--adjust-xml-databases)
    - [1. Move the surface data files to an appropriate input data folder](#1-move-the-surface-data-files-to-an-appropriate-input-data-folder)
    - [2. Adjust the mask and mesh file config in the XML databases](#2-adjust-the-mask-and-mesh-file-config-in-the-xml-databases)
    - [3. Add the paths to the generated surfacedata and land use files to the XML databases](#3-add-the-paths-to-the-generated-surfacedata-and-land-use-files-to-the-xml-databases)
- [Run a test case with the new CTSM input data (only)](#run-a-test-case-with-the-new-ctsm-input-data-only)
  - [1. Create the test case](#1-create-the-test-case)
  - [2. Check and adjust config parameters](#2-check-and-adjust-config-parameters)
    - [a. Force a cold start](#a-force-a-cold-start)
    - [b. Adjust the length of the run](#b-adjust-the-length-of-the-run)
    - [c. Set output interval for history files](#c-set-output-interval-for-history-files)
    - [d. Adjust start year and alignment year with forcing data](#d-adjust-start-year-and-alignment-year-with-forcing-data)
  - [3. Initialize the case with `case.setup`](#3-initialize-the-case-with-casesetup)
  - [4. Build the case for run](#4-build-the-case-for-run)
  - [5. Submit](#5-submit)
- [Add and run with high-resolution ERA5 Land meteorological forcing data](#add-and-run-with-high-resolution-era5-land-meteorological-forcing-data)
  - [1. Download the required ERA5 Land variables for the required region](#1-download-the-required-era5-land-variables-for-the-required-region)
  - [2. Convert ERA5 Land grib files to DATM7 3-stream netCDF files](#2-convert-era5-land-grib-files-to-datm7-3-stream-netcdf-files)
  - [3. Enter the new forcing data files in XML database files as new DATM streams](#3-enter-the-new-forcing-data-files-in-xml-database-files-as-new-datm-streams)
    - [a. Add the mode and default settings for it in XML settings](#a-add-the-mode-and-default-settings-for-it-in-xml-settings)
    - [b. Add streams for the mode in the namelist definition XML file](#b-add-streams-for-the-mode-in-the-namelist-definition-xml-file)
    - [c. Define the streams and file locations / path patterns in the streams definition XML file](#c-define-the-streams-and-file-locations--path-patterns-in-the-streams-definition-xml-file)
  - [4. Create and run a test case with the new forcing data](#4-create-and-run-a-test-case-with-the-new-forcing-data)
    - [a. Create the case](#a-create-the-case)
    - [b. Set XML options](#b-set-xml-options)
    - [c. Build and submit](#c-build-and-submit)


## Definition of the grid

The grid is defined to be a 0.1x0.1 degree grid that is quadratic in
latitude/longitude space and includes all of the Norwegian mainland and adjacent
islands, as well as the course of any rivers that can transport
carbon-containing material from Norwegian territory until they drain into the
ocean. The resolution is chosen to match that of the raw data from the ERA5 Land
metorological dataset, which will be used for atmospheric forcing.

For convenience, we choose the borders so that the corner grid cells are
centered on integer degrees (the actual edges will then be 0.05 degrees outside
of that). This is is not a firm requirement that is imposed by the definition,
but made for convenience. The ERA5 Land dataset has grid cell points at integer
multiples of 0.1 degrees, so any corners with coordinates that are integer
multiples of 0.1 degrees and otherwise fulfill the definition would also work.

Towards the west, north and east, the requirements are fulfilled by setting
longitude/latitude limits that enclose Norway itself. Norway has no land borders
to the west or north, and no rivers that flow out from Norway (all of which flow
into Sweden) extend further east than to the bay of Bothnia, which is entirely
contained within any rectangular region that includes all of Norway. To the
south, the grid must be extended to where the southernmost course of the Göta
Älv drains into Kattegat at Gothenburg, since some rivers in eastern Norway flow
into Sweden and eventually empty into lake Vänern, which in turn is drained by
the Göta Älv. No rivers that carry water originating from Norway extend any
further south than that.

The grid is set to be the smallest grid that fulfills the criteria above, *and*
where the grid cell centers start and end on integer degrees in both latitude
and longitude.

These definitions produce the following limits for the grid:
* **West**: 4.0 E (constrained by Steinsøyna in the Utvær archipelago, in Solund,
  Vestland, which extends a few meters west of 4.5 E)
* **East**: 32.0 E (constrained by the easternmost point of Hornøya in Vardø,
  Finnmark, at about 31.17 E)
* **South**: 57.0 N (constrained by the mouth of the Göta Älv at Gothenburg,
  Sweden. The mouth of the river itself is at around 57.68 N, and possibly a
  little further south to allow for transport of sediment in the archipelago
  outside of Gothenburg).
* **North**: 72.0 N (constrained by the northernmost point of the minor island
  Avløysa at Kinnarodden on Magerøya, Finnmark, at around 71.13 N).

These limits are taken to be constraints on the *centers* of the grid cells.
I.e., the grid cells at the edges have center latitudes and/or longitudes equal
to those listed above, while the grid corners on the edges have latitudes and/or
longitudes 0.05 degrees beyond those values.


## Create the Python enironment

Some of the steps (including most steps that use CIME scripts and other Python
code in the CTSM repo itself) require installing a custom Python environment.
This can be done in several ways, but this repo utilizes the package manager
[`pixi`](https://pixi.prefix.dev/latest/installation/), and specifies all
dependencies in the file `pixi.toml` and exact installed environment in
`pixi.lock` in the repo root.

You can install the pixi environment specified in `pixi.toml` and `pixi.lock`
and activate it with the following commands:
```
pixi install

pixi -e dev shell
```

`pixi.toml` contains both the dependencies of the main CTSM Python environment
as specified in [/python/conda_env_ctsm_py.yml](./python/conda_env_ctsm_py.yml)
and some additional dependencies that are required for other steps in this
guide (notably using
[/tools/surfdat_landfrac_to_mesh_mask.py](./tools/surfdat_landfrac_to_mesh_mask/surfdat_landfrac_to_mesh_mask.py)
to add a land mask and cell areas to the mesh file).

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

There are many ways to create a SCRIP file for a rectangular grid. The simplest
approach, which also adds grid cell areas to the SCRIP file (not done in many
other methods), is to use the `ncks --rgr` command in
[NCO](https://nco.sourceforge.net). You need at least version 4.5.2. A legacy
method using `/tools/mkmapgrids/mkscripgrid.ncl` in the CTSM repo is outlined
below, but it does not give you grid cell areas, and we recommend using `ncks`
instead.

We follow the approach documented in the section "[Grid
Generation](https://nco.sourceforge.net/nco.html#Grid-Generation)" of the [NCO User Guide](https://nco.sourceforge.net/nco.html)

On betzy, you can use NCO by loading the NCO module:
```
module load NCO/5.1.9-foss-2023b-ESMF-8.8.0
```
(other versions of the same module may also work, as long as it's higher than
4.5.2)

The command below outputs a file named
`SCRIPgrid_NorwayRect_0.1x0.1_nomask_c260108.nc` for the rectangular grid
covering Norway listed above. Adjust the name given in the `scrip=` option in
the command below if desired. If you change the coordinates, the coordinates in
the options `lat_sth` and `lon_wst` should be half a grid cell width west/south
of the grid cell centers at the western/southern edge, and the coordinates in
`lat_nrt` and `lat_est` correspondingly half a grid cell width north/east of the
northern/western edges (i.e., they are grid cell edge coordinates, not the
coordinates of the centers). `lat_nbr` and `lon_nbr` must be set to the number
of grid cells (the number of centers) in the latitude and longitude direction
(which determines the resolution). This will be given by
$$$
lat_nbr = \frac{lat_nrt - lat_sth}{resolution}
$$$
and similarly for `lon_nbr`, `lon_wst` and `lon_est`.

The second-to-last command line argument is a dummy input netCDF file. It can be
any netCDF file, the content will be ignored, but it is required for the `ncks`
function to run. The final argument is similarly a dummy output file that will
be created (and should not already exist), but will not have any meaningful
content.
```
ncks \
    --rgr grd_ttl="Rectangular 0.1x0.1 degree grid that covers Norway and outflowing rivers" \
    --rgr scrip=SCRIPgrid_NorwayRect_0.1x0.1_nomask_c260203.nc \
    --rgr lat_typ=uni \
    --rgr lon_typ=grn_ctr \
    --rgr lat_nbr=151 \
    --rgr lon_nbr=281 \
    --rgr lat_drc=s2n \
    --rgr lat_sth=56.95 \
    --rgr lat_nrt=72.05 \
    --rgr lon_wst=3.95 \
    --rgr lon_est=32.05 \
    dummy_in.nc dummy_out.nc
```

On betzy for NorSink, the SCRIP file was moved to the folder
`/cluster/shared/noresm/inputdata/cicero_mods/share/scripgrids/` after having
been created.

#### 1.a Legacy method using `/tools/mkmapgrids/mkscripgrid.ncl`

Creating the SCRIP grid file only requires the `ncl` package in the Python
environment and its dependencies. But if you also want to use the packages in
the dev environment, then replace the last command with `pixi shell -e dev`.

Then go to the directory `/tools/mkmapgrids/` and call the following command:

`PRINT=TRUE PTNAME="NorwayRect_0.1x0.1" W_LON=3.95 E_LON=32.05 S_LAT=56.95 N_LAT=72.05 NX=281 NY=151 ncl ./mkscripgrid.ncl`

See `/tools/mkmapgrids/README` for an explanation of the environment variables
that are set prior the `ncl` command.

These commands will produce an output file named
`SCRIPgrid_NorwayRect_0.1x0.1_nomask_cYYMMDD.nc` (with YYMMDD replaced by
the current date) in the folder /tools/mkmapgrids/.

**NB!** The commands above produce a SCRIP file without a land mask (or, more
precisely, a land mask that is 1 for every grid cell) and no land fraction data.
See comments about this in the next section.

On betzy, the SCRIP file was moved from `${CTSMROOT}/tools/mkmapgrids/` to
`/cluster/shared/noresm/inputdata/cicero_mods/share/scripgrids/`.

### 2. Create a (preliminary) mesh file with triival mask

The SCRIP grid file from the previous file is used to produce a mesh file with a
trivial mask (1 everywhere). We need a mesh file to create the surface data set,
but the surface data contains its own land fraction data and does not need a
mask. We will then later use the surface data set to add a land mask to the mesh
file.

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

ESMF_Scrip2Unstruct ./SCRIPgrid_NorwayRect_0.1x0.1_nomask_c260203.nc ../meshes/ESMFmesh_NorwayRect_0.1x0.1_nomask_c260203.nc 0
```

Note that if you get an error message about the ESMF module (or at least the
specified version of it) being found on betzy, you may need to tell the module
system to look for modules in the custom module library for noresm and then try
again. On betzy, this was done with the following command:

```
module use /cluster/shared/noresm/eb_noresm3/modules/all/
```

### 3. Add new resolution and grid to config files

The new resolution was then added to XML configuration/database files in the
following way:

#### Add resolution name to CTSM namelist definition file

In `/bld/namelist_files/namelist_definition_ctsm.xml`, the new resolution name
must be added to the entry `res`. Find the the XML `<entry>` tag that has the
attribute `id="res"`, and add the new resolution name to the comma-separated
list (without any added spaces) in the `valid_values=` attribute.

On Betzy, the name `NorwayRect_0.1x0.1` was added. This will be used in the
remainder of this guide.

#### Add the prelminiary, nomask mesh file path to the nuopc component/model grid definition files

In `/ccs_config/component_grids_nuopc.xml` add a `<domain>` with the mesh file
from point 2 in the `<domains>` section. The following tag was added on betzy
(after `<domains>` and before `</domains>`):

```
  <domain name="NorwayRect_0.1x0.1">
    <nx>281</nx>  <ny>151</ny>
    <mesh>$DIN_LOC_ROOT/cicero_mods/share/meshes/ESMFmesh_NorwayRect_0.1x0.1_nomask_c260108.nc</mesh>
    <desc>0.1x0.1 degree rectangular grid containing Norway and all rivers that drain from Norway -- only valid for DATM/CLM compset</desc>
  </domain>
```

(Note that this is not really the file we will use, it is only used for
generating the surface data files below. The mesh file we will use for creating
and running cases will be a derived mesh file created later, where we use the
land fractions from the surface data file to add a land mask.)

Then add aliases for the grid name in `/ccs_config/modelgrid_aliases_nuopc.xml`.
The following was added on betzy:

```
  <model_grid alias="NorwayRect0.1">
    <grid name="atm">NorwayRect_0.1x0.1</grid>
    <grid name="lnd">NorwayRect_0.1x0.1</grid>
    <grid name="ocnice">NorwayRect_0.1x0.1</grid>
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

**NB!! The text here refers to the original version of
`/tools/mksurfdata_esmf/gen_mksurfdata_namelist.xml` that was used in generating
the surface dataset in late 2025. A new version was merged in on 2026-01-29,
which contains changes that were merged into the noresm branch from the upstream
ESCOMP/CTSM repo in NorESMHub/CTSM PR 178 (update to CTSM 5.4). The new version
fixes the hardcoded paths to glade mentioned below, but also updates the files
to new versions for CTSM 5.4. The surface data files have not yet been
regenerated using the new raw data files as of 2026-01-28.**

Assuming the new grid resolution and mesh file have been added to the XML files
as described previously, the namelist used by `mksurfdata` can be generated with
the following command (while in the directory `/tools/mksurfdata_esmf/`):

```
./gen_mksurfdata_namelist -v --start-year 1850 --end-year 2023 --res NorwayRect_0.1x0.1 --rawdata-dir /cluster/shared/noresm/inputdata --inlandwet
```

Replace `NorwayRect_0.1x0.1` with the desired resolution name if using a
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

**Update:** This error may have been fixed in a later update in the main branch
(but not yet merged into the norsink inputdata branch at the time of writing).

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
file took more than 4 minutes per year, and a total of 12.7 hours for the period
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

This problem did arise in the run on betzy in January 2026. This was "solved"
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
   and they must be changed to the absolute paths of `.env_mach_specific.sh`` and
   `mksurfdata` under the `mksurfdata_esmf` folder where you have your clone of
   the repo.
2. **That the `SBATCH` parameters at the top of the job script are appropriate.**


   The following parameters were used for the run on betzy in January 2006, for
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
   The actual run took 12.7 hours of wall time in total. The surface data file
   was generated after just over 15 minutes of runtime, the remaining time was
   spent generating the land use file.

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
the 0.1x0.1 degree grid used in the January 2026 run, these should be roughly
1.4 GB and 13 GB, respectively.

### 7. Add land mask and grid cell areas to the mesh file

The SCRIP grid file and the ESMF mesh file that were created in the first steps
contain only a trivial mask (1 everywhere, not just in grid cells that contain
land) and no field for grid cell areas. In this step we use the land fraction
data in the generated surface data file to derive a land mask, compute the grid
cell areas, and add both to the mesh file. This is done using a tool that has
been added in the `/tools` directory of the CTSM repo from the same branch were
this README was added, under
[/tools/surfdat_landfrac_to_mesh_mask/](./tools/surfdat_landfrac_to_mesh_mask/).

Before proceeding, ensure that you are in a shell where the Python environment
has been activated, by running `pixi shell` in the CTSM repo folder as advised
in step 1 above.

To avoid having to type a potentially very long command in the next step, set an
environment variable with the path to the surfdat_landfrac_to_mesh_mask tool as
follows:
```
masktooldir="$(pwd)/tools/surfdat_landfrac_to_mesh_mask"
```
This assumes that you are in the root folder of the CTSM repo. If not, replace
`$(pwd)` with the path to the CTSM repo root.

Then set an environment variable with the path to the generated surface data
file:
```
surfdatafilepath="$(pwd)/tools/mksurfdata_esmf/surfdatafilename.nc"
```
Replace `surfdatafilename.nc` with the actual file name of the surface data file
that was generated in the previous step. The value above assumes that you are in
the root folder of the CTSM repo, and that the surface data file is still in the
`/tools/mksurfdata_esmf` folder under that root folder. Adjust the path if this
is not the case.

Then go to the folder that the mesh file was moved to (which
was `/cluster/shared/noresm/inputdata/cicero_mods/share/meshes/` on betzy, when
following the steps above).

In the folder of the mesh file, give the following command to generate a land
mask and grid cell areas and output a new mesh file with both added to the
original:
```
"${masktooldir}/surfdat_landfrac_to_mesh_mask.sh" \
    --mesh-file ./ESMFmesh_NorwayRect_0.1x0.1_nomask_c260108.nc  \
    --surfdata-file "${surfdatafilepath}" \
    --output-mesh-file ./ESMFmesh_NorwayRect_0.1x0.1_lndmask_c260108.nc
```
Adjust the file name after `--mesh-file ./` to match the actual name of the
preliminary mesh file you generated. If desired, also modify the file name after
`--output-mesh-file` to match the file name that you want for the output mesh
file with added land mask and grid cell areas.

### 8. Move the generated files to inputdata folders and add to / adjust XML databases

Do the two following steps to use the generated input files (the last one is
required only for later convenience):

#### 1. Move the surface data files to an appropriate input data folder

Move the surface data and land use files generated above (and optionally also
the log file) to the inputdata folder where you want to use them. There is no
absolute requirement for where to place them, but the data generated in January
2026 in NorSink on betzy were moved to
`/cluster/shared/noresm/inputdata/cicero_mods/surfdata_esmf/ctsm5.3.0/`.

In general on betzy, we use folders under `/cluster/shared/noresm/inputdata/`
for input files that all noresm users on betzy should have access to, and
specifically the subfolder `cicero_mods` for files that have been modified or
created by CICERO for special purposes.

#### 2. Adjust the mask and mesh file config in the XML databases

Now that we have generated a complete mesh file with land mask and grid cell
areas, we need to adjust the preliminary grid and mesh file configurations we
added to the XML databases in the previous steps.

1. Change the mask in the grid alias definition: In
   [`modelgrid_aliases_nuopc.xml`](./ccs_config/modelgrid_aliases_nuopc.xml),
   change `null` in `<mask>null</mask>` in the block you added previously to the
   name of the grid. For the grid that was described for betzy above, the
   `<model_grid>` block above then becomes:
   ```
   <model_grid alias="NorwayRect0.1">
     <grid name="atm">NorwayRect_0.1x0.1</grid>
     <grid name="lnd">NorwayRect_0.1x0.1</grid>
     <grid name="ocnice">NorwayRect_0.1x0.1</grid>
     <mask>NorwayRect_0.1x0.1</mask>
   </model_grid>
   ```
   where the `<mask>` tag on the penultimate line has been changed.

2. Change the mesh file name in the domain definition: In
   [`component_grids_nuopc.xml`](./ccs_config/component_grids_nuopc.xml), change
   the path of the mesh file (in the `<mesh>` tag) to the modified mesh file
   that you generated with `surfdat_landfrac_to_mesh_mask.sh` above. With the
   settings above, the domain block for the grid then becomes:
   ```
   <domain name="NorwayRect_0.1x0.1">
     <nx>281</nx>  <ny>151</ny>
     <mesh>$DIN_LOC_ROOT/cicero_mods/share/meshes/ESMFmesh_NorwayRect_0.1x0.1_lndmask_c260108.nc</mesh>
     <desc>0.1x0.1 degree rectangular grid containing Norway and all rivers that drain from Norway -- only valid for DATM/CLM compset</desc>
   </domain>
   ```
   where the `<mesh>` tag in the third line was changed.

#### 3. Add the paths to the generated surfacedata and land use files to the XML databases

In order to use the new grid and the new input data files in scripts such as
`create_newcase`, they need to be added to
`/bld/namelist_files/namelist_defaults_ctsm.xml` (if not, you will need to
specify them manually when creating a case):

1. Add the path to the surface data file in an `<fsurdat>` field, with appropriate options for `sim_year` and `use_crop`.
   For the `NorwayRect_0.1x0.1` grid and files created in January 2026 on betzy, the following lines were added:
   ```
   <fsurdat hgrid="NorwayRect_0.1x0.1" sim_year="1850" use_crop=".true." >
   cicero_mods/surfdata_esmf/ctsm5.3.0/surfdata_NorwayRect_0.1x0.1_hist_1850_78pfts_c260108.nc</fsurdat>
   ```

2. Add the path to the land use file in an `<flanduse>` field. For the
   `NorwayRect_0.1x0.1` grid and files created in January 2026 on betzy, the
   following lines were added:
   ```
   <flanduse_timeseries hgrid="NorwayRect_0.1x0.1" sim_year_range="1850-2023">
   cicero_mods/surfdata_esmf/ctsm5.3.0/landuse.timeseries_NorwayRect_0.1x0.1_hist_1850-2023_78pfts_c260108.nc</flanduse_timeseries>
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

Go to the directory where you want to create the new case directory as a
subdirectory and give the following command (replace `NorwayRect_0.1x0.1`
with the name of your new grid if you chose a different name, and
`test_NorwayRect_simple_case` with a different case name if desired):

```
create_newcase \
  --case test_NorwayRect_simple_case \
  --compset '1850_DATM%CRUJRA2024_CLM50%BGC_SICE_SOCN_MOSART_SGLC_SWAV' \
  --res 'a%NorwayRect_0.1x0.1_l%NorwayRect_0.1x0.1_r%r05_g%null_oi%null_w%null_z%null_m%NorwayRect_0.1x0.1' \
  --machine betzy \
  --project nn9188k \
  --run-unsupported \
  --walltime '0:30:00'
```

Note that depending on your settings, the case directory may not have been
created under your current working directory (where you issued the
`create_newcase`) command, but rather under the directory specified by the
`<CIME_OUTPUT_ROOT>` tag in your `config_machines.xml` file. On betzy, the
default config file under
[`/ccs_config/machines/betzy/config_machines.xml`](./ccs_config/machines/betzy/config_machines.xml)
sets `<CIME_OUTPUT_ROOT>` to `/cluster/work/users/$USER/noresm` (where the path
here is absolute, not relative to the CTSM repo root, and `$USER` is replaced by
your username when running).

After create\_newcase has completed, cd into the new case directory to complete
the remaining steps.

### 2. Check and adjust config parameters

Parameters can be changed at ths stage with `./xmlchange` and inspected with
`./xmlquery`, when located in the case directory.

#### a. Force a cold start

We need to change parameters to force CTSM to make a cold start rather than try
to start from initial conditions, since we presumably don't have an initial
conditions or restart file at the right resolution at this point. In principle,
it seems that CESM should interpolate a provided initial conditions file
automatically, but this produces an error at runtime if we go with the defaults
(maybe issues related to using a stub ice sheet model, or some other issue with
the non-CTSM parts of the model?).

Also, we presumably want to do a spinup and not start from initial conditions
(?).

Change the relevant option with the following:
```
./xmlchange CLM_FORCE_COLDSTART=on
```

To do a proper spinup, we might also want to set `CLM_ACCELERATED_SPINUP` to
`on` to do an initial accelerated spinup. Unfortunately doing so produces an
error when running `./case.build`. If we want to do accelerated spinup and the
error persists in production cases, the cause of that error will need to be
investigated further (wasn't investigated further for this test case).

#### b. Adjust the length of the run

Set the length of the run (in model time) by setting `STOP_N` to the nunmber of
model days to run before stopping, and/or optionally change `STOP_OPTION` to a
different unit (e.g., `nmonths`). The default is 5 days (`STOP_OPTION=ndays` and
`STOP_N=5`).

To test output of monthly history files, we set the run time to 3 months. On
betzy, anything up to around 6-9 months should fit within the 30-minute wall
time that gets allocated with the default settings (in the "devel" queue for
short development runs).

```
./xmlchange STOP_OPTION=nmonths
./xmlchange STOP_N=3
```

Note that these options can be changed at any time before running
`./case.submit`.

#### c. Set output interval for history files

The default settings do not output any history files. For this test run, we set
monthly outputs, which gives us three history files with the 3-month run length
above (but you can choose any interval that is shorter than the total run
length).

```
./xmlchange HIST_OPTION=nmonths
./xmlchange HIST_N=1
```

#### d. Adjust start year and alignment year with forcing data

By default, the model starts with year 1 (date `0001-01-01`), which can create
some issues for plotting with the `cftime` library (and be confusing in
general). In this run, we start at 2000 and also set the forcing data to start
in the same year, so we can do the run in a time period where we have multiple
forcing data sets available. Note that the surface data is still generated for
1850, so results may not be expected to match those of a regular 2000 compset.

```
./xmlchange RUN_STARTDATE=2000-01-01
./xmlchange DATM_YR_START=2000
./xmlchange DATM_YR_ALIGN=2000
./xmlchange DATM_YR_END=2023
```

### 3. Initialize the case with `case.setup`

Give the following command to set up the case and prepare for build:
```
./case.setup --verbose --debug
```

The `--verbose` and `--debug` options are optional. The latter will write very
detailed information to `case.setup.log`.

### 4. Build the case for run

Give the following command to start the build (can take a long time):
```
./case.build --verbose --debug
```

If you have run a build previously, you may need to clean it up by first running
`./case.build --clean-all` and then `./case.setup` again, before issuing the
`./case.build` above.

After having done this, you can inspect the various namelists and input file
specifications that have been generated in the `Buildconf` directory under the
case directory.

### 5. Submit 

Submit the case as follows (with `--verbose` and especially `--debug` being
optional):
```
./case.submit --verbose --debug
```

Once the job starts, it should run for the number of days specified by the
`STOP_N` parameter (can be inspected with `./xmlquery STOP_N` and changed with
`./xmlchange STOP_N=n` prior to running `case.build`), or a corresponding number
of months or other time unit if you changed `STOP_OPTION`.


## Add and run with high-resolution ERA5 Land meteorological forcing data

The setup so far can be run as-is with existing metorological forcing data. But
to match the higher resolution of the new grid, you will need higher-resolution
metorological data streams than what is provided out of the box with the main
CESM input data.

In NorSink, we used data from the ERA5 Land data. This was processed into the
same variables and three-stream data file setup that is used by the standard
CRUNCEP and CRUJRA data modes in the DATM data-model, at native 0.1-degree and
1-hour resolution (i.e., we rely on standard CESM routines to downscale the data
to the model time step resolution). The processed data were entered into the
CIME XML databases so that they can be used to set up cases automatically with
`create_newcase`, with DATM mode `ERA5LANDNorwayRect` (the `NorwayRect`
identifier is used to make it clear that the data only covers the region used in
NorSink).

### 1. Download the required ERA5 Land variables for the required region

### 2. Convert ERA5 Land grib files to DATM7 3-stream netCDF files

*The procedure for downloading and converting the ERA5 Land files will be
described here later. Both are done using custom-made Python code, in the
package [`era5land_to_datm`](https://github.com/ciceroOslo/era5land_to_datm).*

*On Betzy, the converted data for the 0.1-degree grid covering Norway for
NorSink is stored in
`/cluster/shared/noresm/inputdata/cicero_mods/atm/datm7/atm_forcing.datm7.ERA5LAND_NORWAYRECT.0.1d.c20260120`
(each stream in a separate subfolder, `Precip1Hrly`, `Solar1Hrly`, and
`TPQWL1Hrly`)*

### 3. Enter the new forcing data files in XML database files as new DATM streams

To use the new files as a DATM mode in compset names when using
`create_newcase`, they must be defined as a new mode, with three new data
streams, and the files and various attributes for each of those streams. Do this
by adding to each XML file as specified below (*only pointers to locations are
given for now, will be amended, in the meantime use `git diff` to see what
changed*):

*NB! The tuning mode (XML config option `LND_TUNING_MODE`) should be set
according to the meteorological forcing used. There are modes for CRUJRA, but
it's currently unclear what we should for the ERA5 Land data. There are also
modes with `era5` in the name, but it's unclear whether this is adapted for the
ERA5 Land data that we have downloaded (and appropriate for the regional grid),
or whether it's used for the pre-existing ERA5 DATM mode that might be based on
other data.*

#### a. Add the mode and default settings for it in XML settings

In `/components/cdeps/datm/cime_config/config_component.xml`, add a mode
with compset identifier `ERA5LAND-NORWAYRECT` and mode name
`ERA5LAND_NORWAYRECT` and suitable description and settings for it under:
* `<description modifier_mode="1">` (the compset identifier)
* `<entry id="DATM_MODE">` (both as a valid value and in list of `<value>`
  fields, mapping compset identifier to mode name)
* `<entry id="DATM_YR_ALIGN">` (optional, but will probably need to be set
  manually with `xmlchange` if not set. Requires specifying a compset pattern
  match, which will include the compset identifier)
* `<entry id="DATM_YR_START">`
* `<entry id="DATM_YR_END">`

In `/cime_config/config_component.xml` (the CTSM component config file), add
tuning modes for the forcing data under `<entry id="LND_TUNING_MODE">`. We don't
have separate tuning for the ERA5 Land data, but assume we can use the tuning
for ERA5 data in general, i.e., set the tuning mode as `clmN_N_ERA5`, replacing
`N_N` with the relevant CLM versions (4.5, 5.0, 6.0).

#### b. Add streams for the mode in the namelist definition XML file

In `/components/cdeps/datm/cime_config/namelist_definition.xml`:
* add the mode as a value field `<value datm_mode="ERA5LAND_NORWAYRECT">` with
streams `ERA5LAND_NORWAYRECT.Solar`, `ERA5LAND_NORWAYRECT.Precip`, and
`ERA5LAND_NORWAYRECT.TPQW`.
* add the mode as a valid mode in `valid_values` under `<entry id="datamode">`.

#### c. Define the streams and file locations / path patterns in the streams definition XML file

In `/components/cdeps/datm/cime_config/stream_definition.xml`, add a stream
definition block (`<stream_entry name="...">`) for each of the three streams
`ERA5LAND_NORWAYRECT.Solar`, `ERA5LAND_NORWAYRECT.Precip`, and
`ERA5LAND_NORWAYRECT.TPQW`, with the correct path for each and file name
patterns as follows:
* `ERA5LAND_NORWAYRECT.Solar`: `clmforc.ERA5Land_NorwayRect0.1x0.1.Prec.%ym.nc`
* `ERA5LAND_NORWAYRECT.Precip`: `clmforc.ERA5Land_NorwayRect0.1x0.1.Solr.%ym.nc`
* `ERA5LAND_NORWAYRECT.TPQW`: `clmforc.ERA5Land_NorwayRect0.1x0.1.TPQWL.%ym.nc`


### 4. Create and run a test case with the new forcing data

Repeat the [previous steps for creating and running a test
case](#run-a-test-case-with-the-new-ctsm-input-data-only) but with options
adjusted for using the new high-resolution metorological forcing. Below we
mostly just list the commands and options to use, see each subsection of ["Run a
test case with the new CTSM input data
(only)"](#run-a-test-case-with-the-new-ctsm-input-data-only) above for
more detailed descriptions. If you change any names or options used at any step,
make sure to check whether later steps also need to be modified.

#### a. Create the case

In the parent directory where you want your case directory:
```
create_newcase \
  --case test_NorwayRect_with_era5land_forcing \
  --compset '1850_DATM%ERA5LAND-NORWAYRECT_CLM50%BGC_SICE_SOCN_MOSART_SGLC_SWAV' \
  --res 'a%NorwayRect_0.1x0.1_l%NorwayRect_0.1x0.1_r%r05_g%null_oi%null_w%null_z%null_m%NorwayRect_0.1x0.1' \
  --machine betzy \
  --project nn9188k \
  --run-unsupported \
  --walltime '0:45:00'
```

#### b. Set XML options

In the case directory created in the previous step:
```
./xmlchange CLM_FORCE_COLDSTART=on

./xmlchange STOP_OPTION=nmonths
./xmlchange STOP_N=3

./xmlchange HIST_OPTION=nmonths
./xmlchange HIST_N=1

./xmlchange RUN_STARTDATE=2019-01-01
./xmlchange DATM_YR_START=2019
./xmlchange DATM_YR_ALIGN=2019
./xmlchange DATM_YR_END=2019
```

#### c. Build and submit

In the case directory, after inspecting files and checking that things look
right:
```
./case.setup --verbose
./case.build --verbose --debug
./case.submit --verbose --debug
```
