"""my_controller controller."""
from controller import Robot
import pandas as pd
import numpy as np


def getGPS():
    gps_vals = gps.getValues()
    gps_x = gps_vals[0]
    gps_y = gps_vals[1]
    
    f_gps_vals = front_gps.getValues()
    f_gps_x = f_gps_vals[0]
    f_gps_y = f_gps_vals[1]
    
    return gps_x, gps_y, f_gps_x, f_gps_y


def getHeadings(goal_x, goal_y, gps_x, gps_y, f_gps_x, f_gps_y):
    x = goal_x - gps_x
    y = goal_y - gps_y
    f_x = f_gps_x - gps_x
    f_y = f_gps_y - gps_y

    required_heading = np.arctan2(y, x)
    current_heading = np.arctan2(f_y, f_x)
    
    if required_heading < 0 :
        required_heading = np.pi + (np.pi - abs(required_heading))

    if current_heading < 0 :
        current_heading = np.pi + (np.pi - abs(current_heading))
    
    print('curr head', "%.2f" % current_heading, 'req head', \
        "%.2f" % required_heading)

    return required_heading, current_heading


def refreshGPS():
    gps_x, gps_y, f_gps_x, f_gps_y = getGPS()
    required_heading, current_heading = getHeadings(goal_x, goal_y,\
        gps_x, gps_y, f_gps_x, f_gps_y)
    
    return required_heading, current_heading


# Setup:
if __name__ == "__main__":
    
    # Robot instance.
    robot = Robot()
    
    # Set the time step of the current world.
    timestep = 16
    
    max_speed = 6.28
    
    # Motor instances (defining where to send motor instructions)
    left_motor = robot.getDevice('motor_2')
    left_motor.setPosition(float('inf'))
    left_motor.setVelocity(0.0)
    
    right_motor = robot.getDevice('motor_1')
    right_motor.setPosition(float('inf'))
    right_motor.setVelocity(0.0)
    
    # LIDAR instance 
    lidar = robot.getDevice('lidar')
    lidar.enable(timestep)
    lidar.enablePointCloud()

    # GPS instance
    gps = robot.getDevice('gps')
    gps.enable(timestep)
    
    front_gps = robot.getDevice('front_gps')
    front_gps.enable(timestep)

    waypoints = pd.read_excel('trajectory.xlsx')
    wp = np.array(waypoints)

    x_wp = wp[:, 0]
    y_wp = wp[:, 1]
    
    L = 0.1
    
    
# Main loop:
while robot.step(timestep) != -1:
    robot.step(timestep)
    
    gps_x, gps_y, f_gps_x, f_gps_y = getGPS()
    
        
# 1 - Find next waypoint
    dist = ( x_wp - gps_x ) ** 2 + ( y_wp - gps_y ) ** 2 ;

    i_closest_wp = np.argmin(dist)
    
    next_wp = wp[i_closest_wp + 1]

    next_x = next_wp[0]
    next_y = next_wp[1]

    #print(gps_x, gps_y)
    #print(x_wp, y_wp)
    
    
# 2 - Find goal on lookahead circle
    dist_to_next = np.sqrt((next_x - gps_x)**2 + (next_y - gps_y)**2)
    
    t = L / dist_to_next
    
    goal_x = (1 - t)*gps_x + t* next_x
    goal_y = (1 - t)*gps_y + t* next_y

    #print(goal_x, goal_y)
    
    
# 3 - Align with required heading if not almost already
    required_heading, current_heading = getHeadings(goal_x, goal_y,\
        gps_x, gps_y, f_gps_x, f_gps_y)

    if (current_heading - required_heading) > 0.1 :
        while abs(current_heading - required_heading) > 0.1 :
            robot.step(timestep)
            left_speed = 0.25 * max_speed
            right_speed = -0.25 * max_speed
    
            left_motor.setVelocity(left_speed)
            right_motor.setVelocity(right_speed)
            #print('a')
            
            required_heading, current_heading = refreshGPS()
    
    elif (required_heading - current_heading) > 0.1 :
        while abs(current_heading - required_heading) > 0.1 :
            robot.step(timestep)
            left_speed = -0.25 * max_speed
            right_speed = 0.25 * max_speed
    
            left_motor.setVelocity(left_speed)
            right_motor.setVelocity(right_speed)
            #print('b')
            
            required_heading, current_heading = refreshGPS()
        

# 4 - Go forwards
    left_speed = 0.25 * max_speed
    right_speed = 0.25 * max_speed
    
    left_motor.setVelocity(left_speed)
    right_motor.setVelocity(right_speed)
    #print('c')