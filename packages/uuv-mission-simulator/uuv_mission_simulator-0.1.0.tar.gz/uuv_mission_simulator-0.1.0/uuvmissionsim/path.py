from uuvmissionsim.utilities import path_utils as utils;
from uuvmissionsim import config as cg;

import math;
import numpy as np;
import xarray as xr;

def get_mission_path(current_point, waypoints, start_time,  instructions, max_depth, min_depth, z_resolution, t_resolution, horizontal_speed, triangle_speed):

    """
    Generates a mission path for a UUV based on given waypoints and instructions.

    This function calculates the mission path for a UUV (Unmanned Underwater Vehicle) 
    based on the provided waypoints, depth constraints, and instructions for different path types.

    Parameters:
    current_point (tuple): The current coordinates of the UUV (x, y, z).
    waypoints (list of tuples): List of waypoints (x, y, z) to navigate through.
    start_time (int): Start time in datetime format.
    instructions (list): List of instructions for path types (0 for yo-yo, 1 for straight).
    max_depth (float): Maximum depth for yo-yo path.
    min_depth (float): Minimum depth for yo-yo path.
    z_resolution (float): Depth resolution for path calculations.
    t_resolution (float): Time resolution for path calculations.
    horizontal_speed (float): Horizontal speed of the UUV.
    triangle_speed (float): Speed for yo-yo maneuvers.

    Returns:
    tuple: A tuple containing the calculated path and formatted time.
    """
    # Initialize lists to store the path coordinates and corresponding time
    path=[]
    time=[]
    distance = 0 
    initial_time = 0 #in seconds 
    
    start_point = waypoints[0]
    
    (xc,yc,zc) = current_point
    (x1,y1,z1) = start_point
    
    # Append the start point to the path and set the initial time
    path.append(start_point)
    time.append(initial_time)
    
    """Firstly we will travel to the first waypoint and start the mission from there. But the data will be collected all the while."""
    current_level = abs(zc) - abs(z1)
    if current_point != waypoints[0]:
        if current_level == 0: #If the UUV is at the same depth as the start point
            p_points, t = utils.interpolate_xyzt_byTimeresolution(current_point, start_point, initial_time, t_resolution, horizontal_speed)
            path.extend(p_points) #The path includes the start point 
            time.extend(t)
        else:  #If the UUV is above or below the start point
            # Pre-calculations for the yo-yo path
            angle_of_attack = math.atan(triangle_speed/horizontal_speed) # Calculate the angle of attack
            b = ((max_depth-min_depth)/math.tan(angle_of_attack))  #Horizontal displacement of half a pulse
            displacement = math.dist(current_point, start_point)
            resultant_speed = triangle_speed/math.sin(angle_of_attack)
            
            path_z, time_z , distance_z= utils.getKnownDepths_path(current_point, start_point, initial_time, z_resolution, resultant_speed)
            distance+=distance_z
            path.extend(path_z)
            time.extend(time_z)
        
    current_time = time[-1] 

    for i in range(len(waypoints)-1):# Iterating through legs (a leg is defined as a path between two consecutive waypoints)
        if instructions[i] == 0: 
            yoyo_path, yoyo_time , yoyo_distance= utils.yo_yo_path(waypoints[i], waypoints[i+1], current_time, min_depth, max_depth, z_resolution, t_resolution, horizontal_speed, triangle_speed)
            path.extend(yoyo_path)
            time.extend(yoyo_time)
            distance+=yoyo_distance
    
        elif instructions[i] == 1 : 
            straight_path, straight_time = utils.interpolate_xyzt_byTimeresolution(waypoints[i], waypoints[i+1], current_time, t_resolution, horizontal_speed)
            straight_distance = math.dist(waypoints[i],waypoints[i+1])
            path.extend(straight_path)
            time.extend(straight_time)
            distance+=straight_distance
            
        current_time = time[-1]
    
    print("Mission Details: ")
    print("distance = ",distance)
    print("total duration (sec) =",time[-1])
    print("mission duration (min) =",time[-1]/60)
    print("mission speed (m/s) =", distance/time[-1])

    # Format the time in datetime64[s] format
    formatted_time = np.array(start_time, dtype='datetime64[s]') + np.array([(np.abs(round(t,1))).astype(int) for t in time], dtype='timedelta64[s]')
    return path,  formatted_time

def get_drifted_path(path, time):

    """
    Calculates the drifted path of a UUV based on ocean current data.

    This function interpolates the velocity data from ROMS model along the given path 
    and calculates the drifted path of the UUV over time.

    Parameters:
    path (list of tuples): List of waypoints (x, y, z) representing the UUV's path.
    time (array-like): Array of time coordinates corresponding to the path points.

    Returns:
    tuple: A tuple containing drifted x, y, z coordinates, time, and headings.
    """

    #Read data (velocity of water in different directions (axis))
    u_data = xr.open_dataset(cg.U_PATH, chunks={'ocean_time': 'auto', 'x_u': 'auto', 'y_u': 'auto', 'z_rho_u': 'auto'})
    v_data = xr.open_dataset(cg.V_PATH, chunks={'ocean_time': 'auto', 'x_v': 'auto', 'y_v': 'auto', 'z_rho_v': 'auto'})
    w_data = xr.open_dataset(cg.W_PATH, chunks={'ocean_time': 'auto', 'x_w': 'auto', 'y_w': 'auto', 'z_rho_w': 'auto'})
    
    # Convert path to a NumPy array
    path = np.array(path) 
    
    # Vectorize the interpolation coordinates
    x = xr.DataArray([p[0] for p in path], dims='point') 
    y = xr.DataArray([p[1] for p in path], dims='point')
    z = xr.DataArray([-p[2] for p in path], dims='point')  # Note the negation for z_rho as depth is recorded from the surface of the ocean
    t = xr.DataArray(time, dims='point')
    
    # Interpolate u, v, w values along the path
    u_values = u_data.u.interp(x_u=x, y_u=y, z_rho_u=z, ocean_time=t).values
    v_values = v_data.v.interp(x_v=x, y_v=y, z_rho_v=z, ocean_time=t).values
    w_values = w_data.w.interp(x_rho=x, y_rho=y, z_w=z, ocean_time=t).values
            
    # Calculate delta_t for each time step
    delta_t = np.diff(time)
    delta_t = np.insert(delta_t, 0, 0)  # Insert 0 at the beginning for initial time step
    delta_t = np.array(delta_t, dtype="int")

    #Calculate drift for each path point
    delta_x = u_values * delta_t
    delta_y = v_values * delta_t
    delta_z = w_values * delta_t

    #Calculate cumulative drift for each path point
    x_drift = np.nancumsum(delta_x)
    y_drift = np.nancumsum(delta_y)
    z_drift = np.nancumsum(delta_z) # Not accumulating drift for z assuming the UUV corrects its depth 

    x_drift += x
    y_drift += y
    z_drift = z
    
    delta_x = np.diff(x_drift)
    delta_y = np.diff(y_drift)
    headings = np.arctan2(delta_y, delta_x)
    headings = np.insert(headings, 0,0) # Insert 0 heading at the start

    return x_drift, y_drift, z_drift, t, headings