from uuvmissionsim.utilities import regrid_roms_utils as utils

import xarray as xr
import xroms
import numpy as np

def regridData(data, variables_to_keep, x_rho_grid, y_rho_grid, z_rho_grid):
    """
    Regrid the provided ROMS data according to the specified target grids for x, y, and z dimensions. S-coordinate system is converted to Z-coordinate system.
    
    Parameters:
    data (xarray.Dataset): The input dataset in s-coordinate system to be regridded.
    variables_to_keep (list): List of variables to be regridded.
    x_rho_grid (xarray.DataArray): Target grid for the x dimension.
    y_rho_grid (xarray.DataArray): Target grid for the y dimension.
    z_rho_grid (xarray.DataArray): Target grid for the z dimension.
    
    Returns:
    xarray.Dataset: The regridded dataset.
    """
    
    # Ensure data is in s-coordinate system
    if "s_rho" not in data.dims and "s_w" not in data.dims:
        raise ValueError("Dataset is not in s-coordinate! Please provide a dataset in s-coordinate system.")
    
    # Set up the ROMS dataset and grid
    ds, xgrid = xroms.roms_dataset(data, include_cell_volume=True, include_Z0=True)
    ds.xroms.set_grid(xgrid)
    
    # Initialize an empty dataset for the regridded data
    regridded_dataset = xr.Dataset()
    
    for var in variables_to_keep:
        
        # Skip the stretching functions Cs_r and Cs_w
        if var in ['Cs_r', 'Cs_w']:
            print(f"Skipping variable '{var}' because it is a stretching function.")
            continue
            
        data_var = ds[var]
        
        # Skip variables that do not have a depth dimension
        if 's_rho' not in data_var.dims and 's_w' not in data_var.dims:
            print(f"Skipping variable '{var}' because it does not have a depth dimension.")
            continue
        
        # Skip variables that have no dimensions or no relevant coordinates
        if not data_var.dims or not any(dim in data_var.dims for dim in ['s_rho', 's_w', 'xi_u', 'eta_v', 'eta_rho', 'xi_rho']):
            print(f"Skipping variable '{var}' because it has no relevant dimensions.")
            continue

        if 's_rho' in data_var.dims:
            if "xi_u" in data_var.dims and "eta_v" in data_var.dims:
                data_xyz = utils.regrid_variable(data_var, ds, xgrid, z_rho_grid, x_rho_grid, y_rho_grid, 'dz_psi')
            elif "xi_u" in data_var.dims:
                data_xyz = utils.regrid_variable(data_var, ds, xgrid, z_rho_grid, x_rho_grid, y_rho_grid, 'u')
            elif "eta_v" in data_var.dims:
                data_xyz = utils.regrid_variable(data_var, ds, xgrid, z_rho_grid, x_rho_grid, y_rho_grid, 'v')
            elif "eta_rho" in data_var.dims and "xi_rho" in data_var.dims:
                data_xyz = utils.regrid_variable(data_var, ds, xgrid, z_rho_grid, x_rho_grid, y_rho_grid, 'rho')
            else:
                # Handle variables with only s_rho dimension
                data_xyz = utils.regrid_z_only(data_var, ds, xgrid, z_rho_grid)
            
        elif 's_w' in data_var.dims:
            if "xi_u" in data_var.dims and "eta_v" in data_var.dims:
                data_xyz = utils.regrid_variable(data_var, ds, xgrid, z_rho_grid, x_rho_grid, y_rho_grid, 'dz_w_psi')
            elif "xi_u" in data_var.dims:
                data_xyz = utils.regrid_variable(data_var, ds, xgrid, z_rho_grid, x_rho_grid, y_rho_grid, 'dz_w_u')
            elif "eta_v" in data_var.dims:
                data_xyz = utils.regrid_variable(data_var, ds, xgrid, z_rho_grid, x_rho_grid, y_rho_grid, 'dz_w_v')
            elif "eta_rho" in data_var.dims and "xi_rho" in data_var.dims:
                data_xyz = utils.regrid_variable(data_var, ds, xgrid, z_rho_grid, x_rho_grid, y_rho_grid, 'w')
            else:
                # Handle variables with only s_w dimension
                data_xyz = utils.regrid_z_only(data_var, ds, xgrid, z_rho_grid)
        else:
            # If no vertical coordinate ('s_rho' or 's_w'), regrid only in x and y
            data_xyz = utils.regrid_xy(data_var, ds, xgrid, x_rho_grid, y_rho_grid)
        
        var_dataset = xr.Dataset({var: data_xyz})
        regridded_dataset = regridded_dataset.merge(var_dataset)
    
    return regridded_dataset