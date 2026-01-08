# %% [markdown]
# # Plotting history files with `hvplot`

# %% [markdown]
# This notebook contains code to plot and view history files interactively with the `hvplot` library, combined with `xarray` data structures.

# %% [markdown]
# ## Imports

# %%
from pathlib import Path

import hvplot
import hvplot.xarray
import numpy as np
import panel as pn
import xarray as xr

# %% [markdown]
# ## Set paths to data files

# %% [markdown]
# Set the root directory for archive files, the subdirectory to the directory containing the history files, and a glob of files you want to include.
# 
# The `archive_root` path will probably depend on the user, so you will most likely need to edit it.

# %%
archive_root: Path = Path('/home/janko/src/repos/norsink/temp_data/betzy/archive')
case_name: str = 'test_NorwayRect_simple_case_CRUJRA2024_2000_alignment'
tape: str = 'h0'
model_name: str = 'clm2'
data_subdir: Path = Path('lnd/hist/')
data_glob: str = f'{case_name}.{model_name}.{tape}.*.nc'

files: list[Path] = sorted((archive_root / case_name / data_subdir).glob(data_glob))

# %%
print(f'Will process {len(files)} files:')
for _f in files:
    print(f'  {_f}')

# %% [markdown]
# ## Open dataset

# %%
ds = xr.open_mfdataset(files, combine='by_coords')

# %%
ds

# %%
# import datetime
# ds['time'] = (
#     'time',
#     [datetime.datetime(1850, _month, 15) for _month in range(1, 6+1)]
# )

# %%
ds['time']

# %%
hvplot.extension('bokeh')
ds['GPP'].hvplot(x='lon', y='lat')

# %%
hvplot.extension('matplotlib')
ds['GPP'].hvplot(x='time', y='lat')

# %%
ds['GPP'].hvplot(x='time', y='lat', xlim=(np.datetime64('2020-01-01'), np.datetime64('2020-09-01')))


# %%
hvplot.extension('bokeh')
# ds['NPP'].sel(lon=12).plot(x='time', y='lat')
ds['NPP'].sel(lon=15).hvplot(x='lat')
