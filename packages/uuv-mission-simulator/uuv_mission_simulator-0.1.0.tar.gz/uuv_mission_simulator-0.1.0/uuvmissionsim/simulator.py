import uuvmissionsim.path as path
from uuvmissionsim.sensors import adcp, ctd 

import logging

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')

class SimulatorError(Exception):
    pass

def run(current_point, waypoints, start_time,  instructions, max_depth, min_depth, z_resolution, t_resolution, horizontal_speed, triangle_speed):
    """
    Executes the UUV mission simulation based on the provided parameters.

    This function calculates the original mission path, determines the drifted path based on ocean currents,
    and collects ADCP and CTD data along the drifted path.

    Parameters:
    current_point (tuple): The current coordinates of the UUV (x, y, z).
    waypoints (list of tuples): List of waypoints (x, y, z) to navigate through.
    start_time (int): Start time in timestamp.
    instructions (list): List of instructions for path types (0 for yo-yo, 1 for straight).
    max_depth (float): Maximum depth for yo-yo path.
    min_depth (float): Minimum depth for yo-yo path.
    z_resolution (float): Depth resolution for path calculations.
    t_resolution (float): Time resolution for path calculations.
    horizontal_speed (float): Horizontal speed of the UUV.
    triangle_speed (float): Speed for yo-yo maneuvers.

    Returns:
    tuple: A tuple containing ADCP data, CTD data, original path, drifted path, and original time coordinates.
    """
    try:
        original_path, original_time = path.get_mission_path(current_point, waypoints, start_time,  instructions, max_depth, min_depth, z_resolution, t_resolution, horizontal_speed, triangle_speed)
        x_drift, y_drift, z_drift, drift_time, headings = path.get_drifted_path(original_path, original_time)
        drift_path = (x_drift, y_drift, z_drift)
        adcp_data = adcp.get_adcpData(x_drift, y_drift, z_drift, drift_time, headings)
        ctd_data = ctd.get_ctdData(x_drift, y_drift, z_drift, drift_time)
    except Exception as e:
        logging.error(f"An error occurred during the simulation: {e}")
        raise SimulatorError(f"An error occurred during the simulation: {e}")

    return adcp_data, ctd_data, original_path, drift_path, original_time
