from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time

LARGE_MOTOR_MAX_VELOCITY = 1050

# function is like a MyBlock
def moveForward(degreesToMove):
    print("In moveForward function, degrees to move = " +  str(degreesToMove))

    #Velocity ranges for Spike motors
    #Small motor (Spike Essential): -660 to 660
    #Medium motor: -1110 to 1110
    #Large motor: -1050 to 1050
    #acceleration and deceleration default is 1000
    #determined velocity by taking large motor maximum/4 for roughly 25% power
    #call with optional parameters
    motor_pair.move_for_degrees(motor_pair.PAIR_1, degreesToMove, 0, velocity=263, stop=motor.BRAKE, acceleration=500, deceleration=1000)
    
    return


#display message on hub and move at same time
async def moveAndDisplayMessage(degreesToMove, messageToDisplay):
    print("In moveAndDisplayMessage function.")

    await light_matrix.write(str(messageToDisplay))  #await keyword waits for message to complete before continuing on
    moveForward(degreesToMove)
    
    return


#Returns true if the gyro yaw angle has reached the degreesToTurn value indicating that a turn has been completed.
def turnCompleted(degreesToTurn):
    #multiplying by -0.1 makes yaw angle match values in hub
    return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degreesToTurn)


#Completes a pivot turn up to 179 degrees.
#Input parameters:  degreesToTurn = positive value if turning to right and negative if turning to left
#                   velocity = In deg/sec; Large motor range = -1050 to 1050
async def pivotTurn(degreesToTurn, velocity):
    print("Pivot Turn")
    
    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    if(degreesToTurn > 0):
        motor_pair.move_tank(motor_pair.PAIR_1, velocity, 0) #right turn
        #motor_pair.move(motor_pair.PAIR_1, 50, velocity=velocity) #alternative way to pivot turn right
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, 0, velocity) #left turn
        #motor_pair.move(motor_pair.PAIR_1, -50, velocity=velocity) #alternative way to pivot turn left
        
    #lambda makes function with parameters callable since runloop.until() expects a function with no parameters
    await runloop.until(lambda: turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ",  motion_sensor.tilt_angles()[0] * -0.1)

    return


#Completes a spin turn up to 179 degrees.
#Input parameters:degreesToTurn = positive value if turning to right and negative if turning to left
#                velocity = In deg/sec; Large motor range = -1050 to 1050
async def spinTurn(degreesToTurn, velocity):
    print("Spin Turn")
    
    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    if(degreesToTurn > 0):
        motor_pair.move_tank(motor_pair.PAIR_1, velocity, -1*velocity) #right turn
        #motor_pair.move(motor_pair.PAIR_1, 100, velocity=velocity) #alternative way to spin turn right
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, -1*velocity, velocity) #left turn
        #motor_pair.move(motor_pair.PAIR_1, -100, velocity=velocity) #alternative way to spin turn left

    #lambda makes function with parameters callable since runloop.until() expects a function with no parameters
    await runloop.until(lambda: turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return


#TODO: test, convert timeout to seconds, and write a proportionalPivotTurn function
async def proportionalSpinTurn(degreesToTurn, velocityMultiplier, timeout):
    print("Proportional Spin Turn")
    
    
    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    startTime = time.ticks_ms()
    print("Start time: ", startTime)

    while (time.ticks_diff(time.ticks_ms(), startTime) < timeout):
        
        if(degreesToTurn > 0):
            turnError = degreesToTurn - motion_sensor.tilt_angles()[0] * -0.1
        else:
            turnError = motion_sensor.tilt_angles()[0] * -0.1 - degreesToTurn

        turnPower = turnError * velocityMultiplier * LARGE_MOTOR_MAX_VELOCITY/50

        if(degreesToTurn > 0):
            motor_pair.move_tank(motor_pair.PAIR_1, int(turnPower), -1* int(turnPower)) #right turn
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, -1*int(turnPower), int(turnPower)) #left turn

        if(turnCompleted(degreesToTurn)):
            print("Turn completed!")
            break

    print("Time out!")
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return


async def checkTimer(timeout):
    startTime = time.ticks_ms()

    print("Start time: ", startTime)

    while time.ticks_diff(time.ticks_ms(), startTime) < timeout:
        continue
        #print("Time is: ", time.ticks_ms())
        #await runloop.sleep_ms(100)

    print("Time is up!")

    return


async def __moveForwardProporational(rotations, velocity):
    print("Move Forward Proportional. Rotations = " + str(rotations) + ". Velocity = " + str(velocity))

    #this value will be different for each robot
    CORRECTION_MULTIPLIER = -2.5

    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    degrees = rotations * 360
    motor.reset_relative_position(port.E, 0) #using port E as its relative position is positive while moving forward on test robot

    while (motor.relative_position(port.E) < degrees):
        error = motion_sensor.tilt_angles()[0] * -0.1  #gyro reading should be 0 if robot is moving straight
        correction = int(error * CORRECTION_MULTIPLIER)
        #print("Relative position = " + str(motor.relative_position(port.E)))
        #print("Correction = " + str(correction))

        #motor_pair.move(motor_pair.PAIR_1, correction, velocity=velocity)
        motor_pair.move_tank(motor_pair.PAIR_1, velocity + correction, velocity - correction, acceleration=500)

        #this won't work because it will run for the number of degrees without reading the gyro
        #motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, degrees, left_velocity=velocity + correction, right_velocity=velocity - correction)
        
    motor_pair.stop(motor_pair.PAIR_1)
    print("Final relative position = " + str(motor.relative_position(port.E)))  

    return


async def __moveBackwardProporational(rotations, velocity):
    print("Move Backward Proportional. Rotations = " + str(rotations) + ". Velocity = " + str(velocity))

    #this value will be different for each robot
    CORRECTION_MULTIPLIER = -2.5

    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    degrees = rotations * 360
    motor.reset_relative_position(port.E, 0) #using port E as its relative position is positive while moving forward on test robot

    while (motor.relative_position(port.E) > degrees):
        error = motion_sensor.tilt_angles()[0] * -0.1#gyro reading should be 0 if robot is moving straight
        correction = int(error * CORRECTION_MULTIPLIER)
        #print("Relative position = " + str(motor.relative_position(port.E)))
        #print("Correction = " + str(correction))

        #motor_pair.move(motor_pair.PAIR_1, correction, velocity=velocity)
        motor_pair.move_tank(motor_pair.PAIR_1, velocity + correction, velocity - correction, acceleration=500)

    motor_pair.stop(motor_pair.PAIR_1)
    print("Final relative position = " + str(motor.relative_position(port.E)))

    return


#Moves straight using the gyro sensor to correct drift. 
#Input parameters:stoppingRotations = positive value if going forward and negative if going backward
#                velocity = In deg/sec; Large motor range = -1050 to 1050
async def __moveStraightWheelRotation(stoppingRotations, velocity):
    print("MoveStraightWheelRotations. Stopping Rotations =  " + str(stoppingRotations) + ". Velocity = " + str(velocity))

    if(stoppingRotations > 0):
        await __moveForwardProporational(stoppingRotations, velocity)
    else:
        await __moveBackwardProporational(stoppingRotations, velocity * -1)

    #motor_pair.move_for_degrees(motor_pair.PAIR_1, degreesToMove, 0, velocity=263, stop=motor.BRAKE, acceleration=500, deceleration=1000)
    #motor_pair.move_tank_for_degrees(motor_pair.PAIR_1, velocity + correction, velocity - correction)


#Moves straight using the gyro sensor to correct drift.
#Input parameters:stoppingRotations = positive value if going forward and negative if going backward
#                velocityPercentage = -100 to +100. Negative valu
async def moveStraightWheelRotation(stoppingRotations, velocityPercentage):
    print("MoveStraightWheelRotations. Stopping Rotations =" + str(stoppingRotations) + ". Velocity % = " + str(velocityPercentage))
    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage/100
    await __moveStraightWheelRotation(stoppingRotations, int(velocity))


# Gyro reset 
async def __gyroReset():
    print("Resetting Gyro")
    
    motion_sensor.reset_yaw(0)
    await motion_sensor.stable()
    return
 
# Sensor reset
async def allSensorReset():
    __gyroReset()
    
    # can display values from other sensors     
    print("Stopping sound")
    await sound.stop()    
    
    print("Clearing lights")
    await light_matrix.clear()
    
    return
    
