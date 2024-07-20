import math;
import numpy as np;
import xarray as xr;

def interpolate_xyt_byDepth(point1, point2, t1, t2, known_z):  
    x1, y1, z1 = point1
    x2, y2, z2 = point2
  
    if z2 < z1:
        return interpolate_xyt_byDepth(point2, point1, t2, t1, known_z)

    x = np.interp(known_z, (z1, z2), (x1, x2))
    y = np.interp(known_z, (z1, z2), (y1, y2))
    t = np.interp(known_z, (z1, z2), (t1, t2))
    
    return x, y, t

"""The below function return a straight path between given two waypoints, for a configured time resolution."""
def interpolate_xyzt_byTimeresolution(point1, point2, start_time, time_resolution, speed):#straight path
    path = []
    time = []
    #When traversing with constant depth, resolution priority is given to time resolution of the model.
    x1, y1, z1 = point1
    x2, y2, z2 = point2
    t1 = start_time
    t2 = t1+ math.dist(point1,point2)/speed
    if z2 != z1:
        raise Exception("Not travelling on same depth!!") 
    
    t = t1 - (t1%time_resolution) + time_resolution
    while t<t2: 
        x = np.interp(t, (t1, t2), (x1, x2))
        y = np.interp(t, (t1, t2), (y1, y2))
        z = np.interp(t, (t1, t2), (z1, z2))
        path.append((x,y,z))
        time.append(t)
        t=t+time_resolution
        
    path.append(point2)
    time.append(t2)
    return path, time

def get_xy_peaks(start_point, end_point, number_of_pulses, min_depth, max_depth, speed):
    
    (x1,y1,z1) = start_point
    (x2,y2,z2) = end_point
    peak_points = []
    path_points = []
    time = []
    
    peak_points.append((x1,y1))
    
    for i in range(number_of_pulses):
        x_top = x1+((x2-x1)/number_of_pulses)*(i+1)
        y_top = y1+((y2-y1)/number_of_pulses)*(i+1)
        peak_points.append((x_top,y_top))
        
        x_bottom = peak_points[-2][0] + ((peak_points[-1][0]-peak_points[-2][0])/2)
        y_bottom = peak_points[-2][1] + ((peak_points[-1][1]-peak_points[-2][1])/2)
        
        if start_point[2] == min_depth: #down 
            path_points.append((x_bottom,y_bottom,max_depth))
            t=math.dist(path_points[-1], start_point)/speed
            time.append(t)
            path_points.append((x_top,y_top,min_depth))
            t=math.dist(path_points[-1], start_point)/speed
            time.append(t)
            
        elif start_point[2] == max_depth: #up
            path_points.append((x_bottom,y_bottom,min_depth))
            t=math.dist(path_points[-1], start_point)/speed
            time.append(t)
            path_points.append((x_top,y_top,max_depth))
            t=math.dist(path_points[-1], start_point)/speed
            time.append(t)
            
        else: 
            raise Exception("Direction can not be determined!\n: Check if the waypoint depth matches the maxiumum/ minimum depth.") 
        start_point = path_points[-1]
            
    return path_points, time

def getKnownDepths_path(point1, point2,t1, z_resolution, speed):
    
    x1,y1,z1 = point1
    x2,y2,z2 = point2
    
    t2 = t1+math.dist(point1,point2)/speed
    time = []
    path_points = []
    
    if abs(z1) - abs(z2) < 0: #going down
        z_k = z1 - (z1 % z_resolution)+z_resolution
        while(z_k < z2):
            x,y,t = interpolate_xyt_byDepth(point1, point2, t1, t2, z_k) 
            path_points.append((x,y,z_k))
            time.append(t)
            z_k+=z_resolution
            
    elif abs(z1)-abs(z2) > 0: #going up
        if (z1 % z_resolution):
            z_k = z1 - (z1 % z_resolution)
        else:
            z_k = z1 - (z1 % z_resolution)
            z_k-=z_resolution
        while(z_k>z2):
            x,y,t = interpolate_xyt_byDepth(point1, point2, t1, t2, z_k)
            path_points.append((x,y,z_k))
            time.append(t)
            z_k -= z_resolution    
    else:
        raise Exception("Direction can not be determined!")
    return path_points,time, math.dist(point1, point2)

def yo_yo_path(start_point, end_point, start_time, min_depth, max_depth, z_resolution, t_resolution, horizontal_speed, triangle_speed): 
    
    (x1,y1,z1) = start_point
    (x2,y2,z2) = end_point
    
    time = []
    path_points = []
    peak_points = []
    
    #Pre-calculations
    angle_of_attack = math.atan(triangle_speed/horizontal_speed) #Take care of units   #To Do: Is an angle of attack within the allowed range?
    b = ((max_depth-min_depth)/math.tan(angle_of_attack)) #b = horizontal dispacement of half a pulse
    displacement = math.dist(start_point, end_point)
    number_of_pulses = int(displacement/(2*b))
    resultant_speed = triangle_speed/math.sin(angle_of_attack)

    #Collecting peak points of triangular pulse
    peak_points, peak_times = get_xy_peaks(start_point, end_point, number_of_pulses, min_depth, max_depth, resultant_speed)
    distance=0
    for i in range(len(peak_points)-1):
        path_z, time_z, yoyo_distance = getKnownDepths_path(peak_points[i], peak_points[i+1], start_time, z_resolution, resultant_speed)
        distance+= yoyo_distance
        path_points.extend(path_z)
        time.extend(time_z)
        start_time=time[-1]

    return path_points, time, distance
