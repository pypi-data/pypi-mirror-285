import xarray as xr
import numpy as np

from uuvmissionsim import config as cg
from uuvmissionsim.utilities import sensor_utils as utils

def get_ctdData(x_drift, y_drift, z_drift, drift_time): #16Hz
    """
    Collects CTD (Conductivity, Temperature, Depth) data along a given drift path.

    This function interpolates CTD data along the provided path coordinates and 
    resamples the data to match the desired frequency.

    Parameters:
    x_drift (array-like): Array of x coordinates of the path.
    y_drift (array-like): Array of y coordinates of the path.
    z_drift (array-like): Array of z coordinates (depth) of the path.
    drift_time (array-like): Array of time coordinates corresponding to the path.

    Returns:
    dict: A dictionary containing the collected and processed CTD data for each variable.
    """
    # Initialize a dictionary to store the collected data
    collected_data={}
    data_paths = cg.CTD_DATA_PATHS # Initialize a dictionary to store the collected data
   
    # Convert drift path coordinates to xarray DataArrays with the dimension 'point'
    x_with_drift = xr.DataArray(x_drift, dims='point')
    y_with_drift = xr.DataArray(y_drift, dims='point')
    z_with_drift = xr.DataArray(z_drift, dims='point')   

    # Loop through each CTD data path to interpolate and collect data along the path
    for d_path in data_paths:
        var_data = xr.open_dataset(d_path, chunks={'ocean_time': 'auto', 'x_rho': 'auto', 'y_rho': 'auto', 'z_rho': 'auto'})
        var_data = var_data.interp(x_rho=x_with_drift, y_rho=y_with_drift, z_rho=z_with_drift,ocean_time=drift_time)
        collected_data[np.array(var_data.variables)[0]] = var_data

    # Convert the collected data into a structured CTD dataset and update the frequency
    for key in collected_data.keys():
        collected_data[key] = utils.createCTDDataset(key,collected_data[key])

    # Resample the data to match the CTD sensor frequency
    for key in collected_data.keys():
        collected_data[key] = utils.updateFrequency(collected_data[key], cg.CTD_FREQUENCY)

    return collected_data