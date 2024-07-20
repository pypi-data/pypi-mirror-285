import xarray as xr
import xroms
import numpy as np

def regrid_variable(data_var, ds, xgrid, z_rho_grid, x_rho_grid, y_rho_grid, var_type):
    """
    Regrid data variable in z, x, and y dimensions as necessary.
    
    Parameters:
    data_var (xarray.DataArray): The data variable to transform.
    ds (xarray.Dataset): The dataset containing the data variable.
    xgrid (xgcm.Grid): The xgcm grid object.
    z_rho_grid (xarray.DataArray): Target grid for the z dimension.
    x_rho_grid (xarray.DataArray): Target grid for the x dimension.
    y_rho_grid (xarray.DataArray): Target grid for the y dimension.
    var_type (str): The type of variable ('u', 'v', 'rho', 'w').
    
    Returns:
    xarray.DataArray: The transformed data variable.
    """
    data_z = regrid_z(data_var, ds, xgrid, z_rho_grid, var_type)
    data_xz = regrid_x(data_z, ds, xgrid, x_rho_grid, var_type)
    data_xyz = regrid_y(data_xz, ds, xgrid, y_rho_grid,x_rho_grid, var_type)
    return data_xyz

def regrid_z(data_var, ds, xgrid, z_rho_grid, var_type):
    """
    Regrid data variable in the z dimension.
    
    Parameters:
    data_var (xarray.DataArray): The data variable to transform.
    ds (xarray.Dataset): The dataset containing the data variable.
    xgrid (xgcm.Grid): The xgcm grid object.
    z_rho_grid (xarray.DataArray): Target grid for the z dimension.
    var_type (str): The type of variable ('u', 'v', 'rho', 'w').
    
    Returns:
    xarray.DataArray: The transformed data variable.
    """
    if var_type == 'u':
        return xgrid.transform(data_var, "Z", z_rho_grid, target_data=ds.z_rho_u)
    elif var_type == 'v':
        return xgrid.transform(data_var, "Z", z_rho_grid, target_data=ds.z_rho_v)
    elif var_type == 'rho':
        return xgrid.transform(data_var, "Z", z_rho_grid, target_data=ds.z_rho)
    elif var_type == 'w':
        return xgrid.transform(data_var, "Z", z_rho_grid, target_data=ds.z_w)
    elif var_type == 'dz_w_u':
        return xgrid.transform(data_var, "Z", z_rho_grid, target_data=ds.z_w_u)
    elif var_type == 'dz_w_v':
        return xgrid.transform(data_var, "Z", z_rho_grid, target_data=ds.z_w_v)
    elif var_type == 'dz_psi':
        return xgrid.transform(data_var, "Z", z_rho_grid, target_data=ds.z_rho_psi)
    elif var_type == 'dz_w_psi':
        return xgrid.transform(data_var, "Z", z_rho_grid, target_data=ds.z_w_psi)
    else:
        raise ValueError(f"Unknown variable type '{var_type}'")

def regrid_z_only(data_var, ds, xgrid, z_rho_grid):
    """
    Regrid data variable only in the z dimension.
    
    Parameters:
    data_var (xarray.DataArray): The data variable to transform.
    ds (xarray.Dataset): The dataset containing the data variable.
    xgrid (xgcm.Grid): The xgcm grid object.
    z_rho_grid (xarray.DataArray): Target grid for the z dimension.
    
    Returns:
    xarray.DataArray: The transformed data variable.
    
    """
    # Ensure that the target data has the same dimensions as the data_var
    target_data = ds.z_rho.isel(ocean_time=0, xi_rho=0, eta_rho=0)
    target_data = target_data.broadcast_like(data_var)
    return xgrid.transform(data_var, "Z", z_rho_grid, target_data=target_data)

def regrid_x(data_var, ds, xgrid, x_rho_grid, var_type):
    """
    Regrid data variable in the x dimension.
    
    Parameters:
    data_var (xarray.DataArray): The data variable to transform.
    ds (xarray.Dataset): The dataset containing the data variable.
    xgrid (xgcm.Grid): The xgcm grid object.
    x_rho_grid (xarray.DataArray): Target grid for the x dimension.
    var_type (str): The type of variable ('u', 'v', 'rho', 'w').
    
    Returns:
    xarray.DataArray: The transformed data variable.
    """
    if var_type == 'u' or var_type == 'dz_w_u':
        return xgrid.transform(data_var, "X", x_rho_grid, target_data=ds.x_u)
    elif var_type == 'v' or var_type == 'dz_w_v':
        return xgrid.transform(data_var, "X", x_rho_grid, target_data=ds.x_v)
    elif var_type == 'rho' or var_type == 'w':
        return xgrid.transform(data_var, "X", x_rho_grid, target_data=ds.x_rho)
    elif var_type =='dz_psi' or var_type == 'dz_w_psi':
        return xgrid.transform(data_var, "X", x_rho_grid, target_data=ds.x_psi)
    else:
        raise ValueError(f"Unknown variable type '{var_type}'")

def regrid_y(data_var, ds, xgrid, y_rho_grid,x_rho_grid, var_type):
    """
    Regrid data variable in the y dimension.
    
    Parameters:
    data_var (xarray.DataArray): The data variable to transform.
    ds (xarray.Dataset): The dataset containing the data variable.
    xgrid (xgcm.Grid): The xgcm grid object.
    y_rho_grid (xarray.DataArray): Target grid for the y dimension.
    var_type (str): The type of variable ('u', 'v', 'rho', 'w').
    
    Returns:
    xarray.DataArray: The transformed data variable.
    """
    if var_type == 'u' or var_type =='dz_w_u':
        target_data_y = xgrid.transform(ds.y_u, "X", x_rho_grid, target_data=ds.x_u)
    elif var_type == 'v' or var_type == 'dz_w_v':
        target_data_y = xgrid.transform(ds.y_v, "X", x_rho_grid, target_data=ds.x_v)
    elif var_type == 'rho' or var_type == 'w':
        target_data_y = xgrid.transform(ds.y_rho, "X", x_rho_grid, target_data=ds.x_rho)
    elif var_type =='dz_psi' or var_type == 'dz_w_psi':
        target_data_y = xgrid.transform(ds.y_psi, "X", x_rho_grid, target_data=ds.x_psi)
    else:
        raise ValueError(f"Unknown variable type '{var_type}'")
   
    return xgrid.transform(data_var, "Y", y_rho_grid, target_data=target_data_y)

def regrid_xy(data_var, ds, xgrid, x_rho_grid, y_rho_grid):
    """
    Regrid data variable in the x and y dimensions.
    
    Parameters:
    data_var (xarray.DataArray): The data variable to transform.
    ds (xarray.Dataset): The dataset containing the data variable.
    xgrid (xgcm.Grid): The xgcm grid object.
    x_rho_grid (xarray.DataArray): Target grid for the x dimension.
    y_rho_grid (xarray.DataArray): Target grid for the y dimension.
    
    Returns:
    xarray.DataArray: The transformed data variable.
    """
    data_x = regrid_x(data_var, ds, xgrid, x_rho_grid, 'rho')
    data_xy = regrid_y(data_x, ds, xgrid, y_rho_grid, x_rho_grid,'rho')
    return data_xy