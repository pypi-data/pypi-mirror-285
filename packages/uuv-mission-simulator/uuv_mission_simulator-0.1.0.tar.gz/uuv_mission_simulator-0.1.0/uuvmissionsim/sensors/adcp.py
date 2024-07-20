
import uuvmissionsim.config as cg
from uuvmissionsim.utilities import sensor_utils as utils

import xarray as xr
import numpy as np
import multiprocessing
from joblib import Parallel, delayed

def get_adcpData(x_drift, y_drift, z_drift, time_coords, headings):
    """
    Collects ADCP (Acoustic Doppler Current Profiler) data along a given path.

    This function interpolates ADCP data along the provided path coordinates and 
    resamples the data to match the desired frequency.

    Parameters:
    x_drift (array-like): Array of x coordinates of the path.
    y_drift (array-like): Array of y coordinates of the path.
    z_drift (array-like): Array of z coordinates (depth) of the path.
    time_coords (array-like): Array of time coordinates corresponding to the path.
    headings (array-like): Array of heading angles along the path.

    Returns:
    dict: A dictionary containing the collected and processed ADCP data for each variable.
    """

    # Initialize a dictionary to store the collected data
    collected_data = {}
    
    # Extend data collection space above and below path for ADCP
    spacing_vertical = cg.VERTICAL_SPACING
    z_above_path = cg.Z_ABOVE_PATH
    z_below_path = cg.Z_BELOW_PATH
    blanking_distance = cg.BLANKING_DISTANCE
    
    #Read data (velocity of water in different directions (axis))
    u_data = xr.open_dataset(cg.U_PATH, chunks={'ocean_time': 'auto', 'x_u': 'auto', 'y_u': 'auto', 'z_rho_u': 'auto'})
    v_data = xr.open_dataset(cg.V_PATH, chunks={'ocean_time': 'auto', 'x_v': 'auto', 'y_v': 'auto', 'z_rho_v': 'auto'})
    w_data = xr.open_dataset(cg.W_PATH, chunks={'ocean_time': 'auto', 'x_w': 'auto', 'y_w': 'auto', 'z_rho_w': 'auto'})

    # Calculate z points above and below the original path for each point
    z_above = np.arange(blanking_distance, z_above_path + spacing_vertical, spacing_vertical)
    z_below = np.arange(-blanking_distance, z_below_path - spacing_vertical, -spacing_vertical)

    # Create extended paths
    extended_paths_above = []
    extended_paths_below = []

    extended_times_below = []
    extended_times_above = []
    
   # Parallelize the loop
    num_cores = multiprocessing.cpu_count()
    result = Parallel(n_jobs=num_cores)(
        delayed(utils.process_point)(i, x_drift, y_drift, z_drift, time_coords, headings, z_above, z_below) for i in range(len(time_coords))
    )
    
    # Extract extended paths and times from the result
    extended_paths_above = np.concatenate([res[0] for res in result])
    extended_paths_below = np.concatenate([res[1] for res in result])
    extended_times_above = np.concatenate([res[2] for res in result])
    extended_times_below = np.concatenate([res[3] for res in result])
    
    # Extract bin numbers 
    bin_numbers_above = np.concatenate([res[4] for res in result])
    bin_numbers_below = np.concatenate([res[5] for res in result])
    
    extended_heading_above = np.concatenate([res[6] for res in result])
    extended_heading_below = np.concatenate([res[7] for res in result])

    extended_path = np.concatenate([extended_paths_above, extended_paths_below])
    extended_time = np.concatenate([extended_times_above, extended_times_below])
    extended_heading = np.concatenate([extended_heading_above, extended_heading_below])

    # Concatenated bin numbers
    bin_numbers = np.concatenate([bin_numbers_above, bin_numbers_below])

    # Create coordinate DataArrays
    x_with_drift = xr.DataArray(extended_path[:, 0], dims='point')
    y_with_drift = xr.DataArray(extended_path[:, 1], dims='point')
    z_with_drift = xr.DataArray(extended_path[:, 2], dims='point')
    time_extended_coords = xr.DataArray(extended_time, dims='point',attrs={'axis': 'T', 'standard_name': 'time'})
    bin_numbers = xr.DataArray(bin_numbers, dims='point')
    
    # Interpolate u values
    u_values = u_data.interp(x_u=x_with_drift, y_u= y_with_drift, z_rho_u=z_with_drift, ocean_time=time_extended_coords)
    v_values = v_data.interp(x_v=x_with_drift, y_v= y_with_drift, z_rho_v=z_with_drift, ocean_time=time_extended_coords)
    w_values = w_data.interp(x_rho=x_with_drift, y_rho= y_with_drift, z_w=z_with_drift, ocean_time=time_extended_coords)

    collected_data['u'] = u_values
    collected_data['v'] = v_values
    collected_data['w'] = w_values
    
    #creating a dataset for each variable and setting time as dimension 
    for key in collected_data.keys():
        collected_data[key] = utils.createADCPDataset(key,collected_data[key],bin_numbers, extended_heading)
    
    # Rotate the direction of the currents to match the vehicle heading 
    u_transformed, v_transformed  = utils.rotate_uv(collected_data['u'].u, collected_data['v'].v, collected_data['u'].u.heading)
    
    collected_data['transformed_u'] = u_transformed.to_dataset(name='transformed_u')
    collected_data['transformed_v'] = v_transformed.to_dataset(name='transformed_v')

    # Resample the data to match the ADCP sensor frequency
    for key in collected_data.keys():
         collected_data[key] = utils.updateFrequency(collected_data[key], cg.ADCP_FREQUENCY)

    return collected_data