import numpy as np
import pandas as pd
import xarray as xr

def process_point(i, x_drift, y_drift, z_drift, time, headings, z_above, z_below):
    x, y, z , t= np.array(x_drift), np.array(y_drift), np.array(z_drift), np.array(time)
    x_p, y_p, z_p = x[i], y[i], z[i]
    extended_paths_above = np.column_stack([np.repeat(x_p, len(z_above)), np.repeat(y_p, len(z_above)), z_p + z_above])
    extended_paths_below = np.column_stack([np.repeat(x_p, len(z_below)), np.repeat(y_p, len(z_below)), z_p + z_below])
    extended_path_length = len(extended_paths_above)
    extended_times_above = np.repeat(t[i], extended_path_length)
    extended_times_below = np.repeat(t[i], extended_path_length)
    extended_heading_above = np.repeat(headings[i], extended_path_length)
    extended_heading_below = np.repeat(headings[i], extended_path_length)
    
    # Track bin number for each point
    bin_numbers_above = np.arange(len(z_above)) + 1  # Start from 1
    bin_numbers_below = -np.arange(len(z_below)) + 1  # Start from 1
    
    return extended_paths_above, extended_paths_below, extended_times_above, extended_times_below, bin_numbers_above, bin_numbers_below, extended_heading_above, extended_heading_below

def createADCPDataset(var_name, var_dataArray, bin_numbers, headings):
    
    t = var_dataArray[var_name].ocean_time.data
    var_values = var_dataArray[var_name].data
    
    for coord in var_dataArray.coords:
        #co-ordinates
        if 'x' in coord:
            x = var_dataArray[var_name][coord].data
        elif 'y' in coord:
            y = var_dataArray[var_name][coord].data
        elif 'z' in coord:
            z = var_dataArray[var_name][coord].data
   
    data = {
        'x': x,
        'y': y,
        'z': z,
        't': t,
        'var_data': var_values,
        'bins': bin_numbers, #new,
        'heading': headings
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Group by unique combinations of t and z, then calculate mean
    result = df.groupby(['t', 'z']).mean().reset_index()

    # Pivot the table
    pivot_table = result.pivot(index='z', columns='t', values=['x', 'y', 'var_data', 'bins', 'heading'])

    # Define grid for t and z
    unique_t = sorted(set(df['t']))
    unique_z = sorted(set(df['z']))

    # Convert pivot_table to xarray Dataset
    dataArray = xr.DataArray(
            data= pivot_table['var_data'].values.T,
            dims=['t', 'z'],
            coords=dict(
            x=(["t", "z"], pivot_table['x'].values.T),
            y=(["t", "z"], pivot_table['y'].values.T),
            bins =(["t", "z"], pivot_table['bins'].values.T),
            heading =(["t", "z"], pivot_table['heading'].values.T),
            z= unique_z,
            t= unique_t))
    dataset = xr.Dataset({var_name: dataArray})
    return dataset

def updateFrequency(data, new_frequency):
    """
    Resamples the time array to match the new frequency with nanosecond precision.

    Parameters:
    time_array (np.ndarray): The original time array in seconds as datetime64[ns].
    new_frequency (float): The new frequency in Hz (e.g., 1200e3 for 1200 kHz).

    Returns:
    np.ndarray: The resampled time array with nanosecond precision.
    """
    time_array = data.t
    # Ensure the time array is in datetime64[ns] format
    time_array = np.array(time_array, dtype='datetime64[ns]')
    
    # Calculate the new sampling interval in nanoseconds
    new_sampling_interval_ns = int(1e9 / new_frequency)  #Convert Hz to nanoseconds interval
    
    # Create the new time array based on the new sampling interval
    start_time = time_array[0]
    end_time = time_array[-1]
    new_time_array = np.arange(start_time, end_time, np.timedelta64(new_sampling_interval_ns, 'ns'))
    data = data.interp(t=new_time_array)
    return data

def createCTDDataset(var_name, var_dataArray):
    
    t = var_dataArray['ocean_time'].data
    var_values = var_dataArray[var_name].data
    
    for coord in var_dataArray.coords:
        if 'x' in coord:
            x = var_dataArray[coord].data
        elif 'y' in coord:
            y = var_dataArray[coord].data
        elif 'z' in coord:
            z = var_dataArray[coord].data

    data = {
        'x': x,
        'y': y,
        'z': z,
        't': t,
        'var_data': var_values
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Group by unique combinations of t and z, then calculate mean
    result = df.groupby('t').mean().reset_index()

    # Define unique time array
    unique_t = sorted(set(df['t']))

    # Convert result to xarray Dataset
    dataArray = xr.DataArray(
        data=result['var_data'].values,
        dims=['t'],
        coords=dict(
            x=(["t"], result['x'].values),
            y=(["t"], result['y'].values),
            z=(["t"], result['z'].values),
            t=unique_t
        )
    )
    dataset = xr.Dataset({var_name: dataArray})
    
    return dataset

def rotate_uv(u, v, heading_angle):
    U = u + (v * 1j)
    # Rotate the vector using the heading angle directly
    transformed_V = np.exp(1j * heading_angle) * U
    transformed_u = transformed_V.real
    transformed_v = transformed_V.imag
    return transformed_u, transformed_v