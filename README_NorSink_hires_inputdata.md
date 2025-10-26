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
