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
SCRIPgrid_NorwayRect_0.125x0.125_nomask_cYYMMDD.nc (with YYMMDD replaced by the
current date) in the folder /tools/mkmapgrids/. On betzy, this file was then
moved to /cluster/shared/noresm/inputdata/cicero_mods/share/scripgrids/.
