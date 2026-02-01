"""Code+script to make an evenly spaced rectangular grid mesh and mesh file.

The code in this module can be used to generate an `esmpy.Mesh` object for an
evenly spaced grid that is rectangular in latitude/longitude space, and use it
to write a corresponding ESMF mesh file.

The `Mesh` object and the file will have coordinates in units of degrees, and an
area field with grid cell areas in steradians. It will have a trivial mask field
(all unmasked / 1 for all grid cells).
"""
from collections.abc import Sequence
from pathlib import Path

import esmpy
import netCDF4 as nc4
import numpy as np



type NDArrayFloat1d = np.ndarray[tuple[int], np.dtype[np.float64]]
type NDArrayInt1d = np.ndarray[tuple[int], np.dtype[np.int32]]

def compute_1d_nodes_from_centers(centers: NDArrayFloat1d) -> NDArrayFloat1d:
    """
    Compute 1D node (boundary) coordinates from grid cell center coordinates.

    This function assumes the nodes lie midway between the centers, and 
    extrapolates the boundary nodes based on the width of the edge cells.

    Parameters
    ----------
    centers : numpy.ndarray
        1D array of grid cell center coordinates.

    Returns
    -------
    numpy.ndarray
        1D array of node coordinates with size len(centers) + 1.
    """
    n = len(centers)
    if n < 2:
        raise ValueError("At least 2 grid centers are required to infer node coordinates.")

    nodes = np.zeros(n + 1, dtype=np.float64)

    # Calculate inner nodes as midpoints between centers
    nodes[1:-1] = 0.5 * (centers[:-1] + centers[1:])

    # Extrapolate the first node: centers[0] is average of nodes[0] and nodes[1]
    # centers[0] = (nodes[0] + nodes[1]) / 2  =>  nodes[0] = 2*centers[0] - nodes[1]
    nodes[0] = 2.0 * centers[0] - nodes[1]

    # Extrapolate the last node: centers[-1] is average of nodes[-2] and nodes[-1]
    nodes[-1] = 2.0 * centers[-1] - nodes[-2]

    return nodes


def create_node_coordinates(
    lon_1d: NDArrayFloat1d,
    lat_1d: NDArrayFloat1d
) -> tuple[NDArrayFloat1d, NDArrayFloat1d]:
    """
    Generate 2D meshgrid coordinates for mesh nodes from 1D coordinate arrays.

    Parameters
    ----------
    lon_1d : numpy.ndarray
        1D array of longitude coordinates.
    lat_1d : numpy.ndarray
        1D array of latitude coordinates.

    Returns
    -------
    tuple[numpy.ndarray, numpy.ndarray]
        A tuple containing (lon_2d, lat_2d) flattened to 1D arrays, 
        suitable for ESMF node insertion.
    """
    lon_grid, lat_grid = np.meshgrid(lon_1d, lat_1d, indexing='xy')
    # Flatten to 1D as ESMF expects unstructured lists of nodes
    return lon_grid.flatten().astype(np.float64), lat_grid.flatten().astype(np.float64)


def compute_element_connectivity(
    n_lon_nodes: int,
    n_lat_nodes: int
) -> NDArrayInt1d:
    """
    Compute the connectivity array for a logically rectangular grid of quads.
    
    ESMF expects a 1D array of connectivity indices. For quads, this is
    4 indices per element. The indices must be 1-based.
    
    The node ordering for each quad is Counter-Clockwise (CCW):
    Bottom-Left -> Bottom-Right -> Top-Right -> Top-Left.

    Parameters
    ----------
    n_lon_nodes : int
        Number of nodes along the longitude axis.
    n_lat_nodes : int
        Number of nodes along the latitude axis.

    Returns
    -------
    numpy.ndarray
        1D array of dimensions (num_elements * 4) containing 1-based node indices.
    """
    n_lon_elems = n_lon_nodes - 1
    n_lat_elems = n_lat_nodes - 1
    num_elems = n_lon_elems * n_lat_elems

    # 1-based node indices
    # We create a 2D grid of node indices to easily grab neighbors
    node_indices = np.arange(1, (n_lon_nodes * n_lat_nodes) + 1, dtype=np.int32)
    node_indices = node_indices.reshape((n_lat_nodes, n_lon_nodes))

    # We only iterate up to n-1 to form elements
    # Indices for the "Bottom-Left" corner of every element
    # Slice off the last row and last column
    bl = node_indices[:-1, :-1].flatten()
    
    # Bottom-Right (same row, next column)
    br = node_indices[:-1, 1:].flatten()
    
    # Top-Right (next row, next column)
    tr = node_indices[1:, 1:].flatten()
    
    # Top-Left (next row, same column)
    tl = node_indices[1:, :-1].flatten()

    # Stack them: (Num_Elems, 4)
    # ESMF standard for quads: BL, BR, TR, TL (Counter-Clockwise)
    connectivity = np.column_stack((bl, br, tr, tl))
    
    # Flatten to 1D array
    return connectivity.flatten()


def build_esmf_mesh(
    lon_nodes: NDArrayFloat1d,
    lat_nodes: NDArrayFloat1d,
    connectivity: NDArrayInt1d,
    n_elems: int
) -> esmpy.Mesh:
    """
    Instantiate and populate an esmpy.Mesh object.

    Parameters
    ----------
    lon_nodes : NDArrayFloat
        Flattened array of node longitude coordinates.
    lat_nodes : NDArrayFloat
        Flattened array of node latitude coordinates.
    connectivity : NDArrayInt
        Flattened connectivity array (1-based indices).
    n_elems : int
        Total number of elements in the mesh.

    Returns
    -------
    esmpy.Mesh
        The constructed ESMF Mesh object.
    """
    # Create the Mesh object in 2D space
    mesh = esmpy.Mesh(parametric_dim=2, spatial_dim=2, coord_sys=esmpy.CoordSys.SPH_DEG)

    # 1. Add Nodes
    # n_nodes is derived from the coordinate arrays
    num_nodes = len(lon_nodes)
    mesh.add_nodes(num_nodes, node_ids=np.arange(1, num_nodes + 1, dtype=np.int32))

    # Set coordinates (0=lon, 1=lat for SPH_DEG)
    # esmpy requires specific buffer pointers or standard numpy arrays
    mesh.get_coords(0)[:] = lon_nodes
    mesh.get_coords(1)[:] = lat_nodes

    # 2. Add Elements
    # element_types needs to be an array of ESMF.MeshElemType.QUAD
    # Since all are quads, we create a constant array
    elem_types = np.full(n_elems, esmpy.MeshElemType.QUAD, dtype=np.int32)
    
    mesh.add_elements(
        element_count=n_elems,
        element_ids=np.arange(1, n_elems + 1, dtype=np.int32),
        element_types=elem_types,
        element_conn=connectivity
    )

    return mesh


def calculate_mesh_areas(mesh: esmpy.Mesh) -> NDArrayFloat1d:
    """
    Calculate the area of every element in the mesh using ESMF's internal engine.

    This creates a temporary Field on the Mesh to perform the calculation.

    Parameters
    ----------
    mesh : esmpy.Mesh
        The ESMF Mesh object.

    Returns
    -------
    NDArrayFloat
        Array of area values for each element.
    """
    # We must create a Field to hold the calculation
    # MeshLoc.ELEMENT ensures we get one value per cell
    area_field = esmpy.Field(mesh, name='area_calc', meshloc=esmpy.MeshLoc.ELEMENT)
    
    # ESMF provides a direct method to compute area into a field
    area_field.get_area()
    
    # Return a copy of the underlying numpy buffer
    return area_field.data.copy()


def write_mesh_to_netcdf(
    mesh: esmpy.Mesh,
    filename: str,
    area_data: NDArrayFloat1d,
    mask_data: NDArrayInt1d
) -> None:
    """
    Write the Mesh geometry to a NetCDF file and append Area and Mask variables.

    esmpy.Mesh.write() handles the complex geometry/topology writing.
    We then open the file with netCDF4 to add the data fields, as the basic
    write command only dumps the grid structure.

    Parameters
    ----------
    mesh : esmpy.Mesh
        The ESMF Mesh object.
    filename : str
        Output filename (e.g., 'mesh.nc').
    area_data : NDArrayFloat
        Array of element areas.
    mask_data : NDArrayInt
        Array of element mask values.
    """
    # 1. Write the standard ESMF Mesh geometry (Coords + Connectivity)
    mesh.write(filename)

    # 2. Open the file to append the extra variables
    # ESMF usually names the element dimension 'elementCount' or 'element_count'
    # We inspect the file to be safe, but typically we can append based on dimension size.
    with nc4.Dataset(filename, 'r+') as nc:
        # Identify the element dimension name
        # It is usually 'elementCount' in files generated by ESMF
        elem_dim_name = 'elementCount'
        if elem_dim_name not in nc.dimensions:
            # Fallback search for dimension with matching size
            for dim_name, dim in nc.dimensions.items():
                if dim.size == len(area_data):
                    elem_dim_name = dim_name
                    break
        
        # Create Area Variable
        if 'area' not in nc.variables:
            area_var = nc.createVariable('area', np.float64, (elem_dim_name,))
            area_var.units = 'square radians' # ESMF default for Sphere
            area_var.long_name = 'Grid Cell Area'
            area_var[:] = area_data

        # Create Mask Variable
        if 'mask' not in nc.variables:
            mask_var = nc.createVariable('mask', np.int32, (elem_dim_name,))
            mask_var.long_name = 'Grid Cell Mask'
            mask_var[:] = mask_data
            
    print(f"Successfully generated ESMF Mesh file: {filename}")


def generate_esmf_rect_mesh(
    lon_centers: NDArrayFloat1d,
    lat_centers: NDArrayFloat1d,
) -> esmpy.Mesh:
    """
    Orchestration function to generate a regular rectangular ESMF Mesh object.
    
    This function accepts grid cell CENTERS, computes the corresponding
    NODES (corners), and generates the mesh object.

    Parameters
    ----------
    lon_centers : numpy.ndarray
        1D array of longitude coordinates (cell centers).
    lat_centers : numpy.ndarray
        1D array of latitude coordinates (cell centers).

    Returns
    -------
    esmpy.Mesh
        The constructed ESMF Mesh object, with area field and trivial mask.
    """
    # 1. Prepare Coordinates
    print('Calculating node coordinates from centers...')
    lon_nodes = compute_1d_nodes_from_centers(lon_centers)
    lat_nodes = compute_1d_nodes_from_centers(lat_centers)

    print(f'  Longitude nodes: {len(lon_nodes)} (from {len(lon_centers)} centers)')
    print(f'  Latitude nodes:  {len(lat_nodes)} (from {len(lat_centers)} centers)')

    print('Generating mesh coordinates...')
    flat_lons, flat_lats = create_node_coordinates(lon_nodes, lat_nodes)

    # 2. Build Connectivity
    print('Building element connectivity...')
    n_lon_nodes = len(lon_nodes)
    n_lat_nodes = len(lat_nodes)
    connectivity = compute_element_connectivity(n_lon_nodes, n_lat_nodes)
    
    # Calculate total elements based on centers provided
    n_elems = len(lon_centers) * len(lat_centers)

    # 3. Create ESMF Mesh
    print('Creating ESMF Mesh object...')
    mesh = build_esmf_mesh(flat_lons, flat_lats, connectivity, n_elems)

    # 4. Calculate Area
    print('Calculating cell areas...')
    area_values = calculate_mesh_areas(mesh)

    # 5. Create Trivial Mask (All 1s)
    mask_values = np.ones(n_elems, dtype=np.int32)


# Example Usage Block
if __name__ == '__main__':
    # Define a simple grid based on centers
    # Example: 10 degree spacing centered at -175, -165... to ...175
    # This will result in nodes at -180, -170... 180
    lons_c = np.arange(-175, 176, 10.0, dtype=np.float64)
    lats_c = np.arange(-85, 86, 10.0, dtype=np.float64)

    generate_esmf_rect_mesh_file(lons_c, lats_c, 'global_rect_mesh.nc')
