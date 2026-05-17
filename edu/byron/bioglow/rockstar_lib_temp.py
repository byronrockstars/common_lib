from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time
from myClasses import RobotConfig

LEFT_WHEEL_PORT = port.A
RIGHT_WHEEL_PORT = port.E

def moveForward(myConfig:RobotConfig, degreesToMove):
    print("In moveForward function")

    #Velocity ranges for Spike motors
    #Small motor (Spike Essential): -660 to 660
    #Medium motor: -1110 to 1110
    #Large motor: -1050 to 1050
    #acceleration and deceleration default is 1000
    #determined velocity by taking large motor maximum/4 for roughly 25% power
    #call with optional parameters
    velocity = myConfig.getMainMotorVelocity()
    motor_pair.move_for_degrees(motor_pair.PAIR_1, degreesToMove, 0, velocity=velocity, stop=motor.BRAKE, acceleration=500, deceleration=1000)
    
    return


#display message on hub and move at same time
#VKM: I did not change this
async def moveAndDisplayMessage(degreesToMove, messageToDisplay):
    print("In moveAndDisplayMessage function.")

    await light_matrix.write(str(messageToDisplay))  #await keyword waits for message to complete before continuing on
    moveForward(degreesToMove)
    
    return


#Returns true if the gyro yaw angle has reached the degreesToTurn value indicating that a turn has been completed.
def __turnCompleted(degreesToTurn):
    #multiplying by -0.1 makes yaw angle match values in hub
    return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degreesToTurn)


#Completes a pivot turn up to 179 degrees.
#Input parameters:  degreesToTurn = positive value if turning to right and negative if turning to left
#                   velocity = In deg/sec; Large motor range = -1050 to 1050
async def pivotTurn(myConfig:RobotConfig, degreesToTurn):
    print("Pivot Turn")
    
    velocity = myConfig.getMainMotorVelocity()
    
    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    if(degreesToTurn > 0):
        motor_pair.move_tank(motor_pair.PAIR_1, velocity, 0) #right turn
        #motor_pair.move(motor_pair.PAIR_1, 50, velocity=velocity) #alternative way to pivot turn right
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, 0, velocity) #left turn
        #motor_pair.move(motor_pair.PAIR_1, -50, velocity=velocity) #alternative way to pivot turn left
        
    #lambda makes function with parameters callable since runloop.until() expects a function with no parameters
    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ",  motion_sensor.tilt_angles()[0] * -0.1)

    return


#Completes a spin turn up to 179 degrees.
#Input parameters:degreesToTurn = positive value if turning to right and negative if turning to left
#                velocity = In deg/sec; Large motor range = -1050 to 1050
async def spinTurn(myConfig:RobotConfig, degreesToTurn):
    print("Spin Turn")
    
    velocity = myConfig.getMainMotorVelocity()
    
    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    if(degreesToTurn > 0):
        motor_pair.move_tank(motor_pair.PAIR_1, velocity, -1*velocity) #right turn
        #motor_pair.move(motor_pair.PAIR_1, 100, velocity=velocity) #alternative way to spin turn right
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, -1*velocity, velocity) #left turn
        #motor_pair.move(motor_pair.PAIR_1, -100, velocity=velocity) #alternative way to spin turn left

    #lambda makes function with parameters callable since runloop.until() expects a function with no parameters
    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return


#Complete a spin turn and slow down as the turn completes to ensure accuracy.
#Input parameters: degreesToTurn = positive value if turning to right and negative if turning to left (-180 to 180)
#                velocityPercentage (optional) = how fast to complete the turn in percentage (1 to 100)
#                timeout (optional) = maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached.
async def proportionalSpinTurn(myConfig:RobotConfig, degreesToTurn):
    print("Proportional Spin Turn")

    velocityPercentage = (myConfig.getMainMotorVelocity()/myConfig.LARGE_MOTOR_MAX_VELOCITY)*100
    timeout = myConfig.getTimeout()
    
    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    startTime = time.ticks_ms()
    print("Start time: ", startTime)

    #convert timeout (in seconds) to milliseconds and compare to amount of time that has gone by
    while (time.ticks_diff(time.ticks_ms(), startTime) < timeout * 1000):

        if(degreesToTurn > 0):
            turnError = degreesToTurn - motion_sensor.tilt_angles()[0] * -0.1
        else:
            turnError = motion_sensor.tilt_angles()[0] * -0.1 - degreesToTurn

        turnPower = turnError * velocityPercentage/100 * myConfig.LARGE_MOTOR_MAX_VELOCITY/50

        if(degreesToTurn > 0):
            motor_pair.move_tank(motor_pair.PAIR_1, int(turnPower), -1* int(turnPower)) #right turn
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, -1*int(turnPower), int(turnPower)) #left turn

        if(__turnCompleted(degreesToTurn)):
            print("Turn completed!")
            break

    print("Time out!")
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return

#VKM: I did not change this
#Complete a pivot turn and slow down as the turn completes to ensure accuracy. 
#Input parameters: degreesToTurn = positive value if turning to right and negative if turning to left (-180 to 180)
#                  velocityPercentage (optional) = how fast to complete the turn in percentage (1 to 100) 
#                  timeout (optional) = maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached. 
async def proportionalPivotTurn(degreesToTurn, velocityPercentage = 40, timeout = 2):
    print("Proportional Pivot Turn. DegreesToTurn = " + str(degreesToTurn) + ". velocityPercentage = " + str(velocityPercentage) + ", timeout(seconds) = " + str(timeout))

    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    startTime = time.ticks_ms()
    print("Start time: ", startTime)

    #convert timeout (in seconds) to milliseconds and compare to amount of time that has gone by
    while (time.ticks_diff(time.ticks_ms(), startTime) < timeout * 1000):

        if(degreesToTurn > 0):
            turnError = degreesToTurn - motion_sensor.tilt_angles()[0] * -0.1
        else:
            turnError = motion_sensor.tilt_angles()[0] * -0.1 - degreesToTurn

        turnPower = turnError * velocityPercentage/100 * LARGE_MOTOR_MAX_VELOCITY/40  #pivot turns are slower so take a larger percentage of the max velocity 

        if(degreesToTurn > 0):
            motor_pair.move_tank(motor_pair.PAIR_1, int(turnPower), 0) #right turn
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 0, int(turnPower)) #left turn

        if(__turnCompleted(degreesToTurn)):
            print("Turn completed!")
            break

    print("Time out!")
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return

#VKM: I did not change this
async def __moveForwardProporational(rotations, velocity, brakeStartPercentage):
    print("Move Forward Proportional. Rotations = " + str(rotations) + ", Velocity = " + str(velocity) + ", Brake = " + str(brakeStartPercentage))

    #this value will be different for each robot
    CORRECTION_MULTIPLIER = -1.5

    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    degrees = rotations * 360
    motor.reset_relative_position(RIGHT_WHEEL_PORT, 0) #using right wheel port as its relative position is positive while moving forward on test robot
    brakeStartDistance = degrees * brakeStartPercentage
    endSpeed = LARGE_MOTOR_MAX_VELOCITY * .1 #10% speed is slowest to go in order for motor to complete distance

    while (motor.relative_position(RIGHT_WHEEL_PORT) < degrees):
        error = motion_sensor.tilt_angles()[0] * -0.1 #gyro reading should be 0 if robot is moving straight
        correction = int(error * CORRECTION_MULTIPLIER)
        #print("Correction = " + str(correction))
 
        deceleration = 0
        degreesTraveled = motor.relative_position(RIGHT_WHEEL_PORT)
        
        if(degreesTraveled > brakeStartDistance): 
            deceleration = min(velocity * degreesTraveled/degrees, velocity - endSpeed)

        motor_pair.move_tank(motor_pair.PAIR_1, velocity + correction - int(deceleration), velocity - correction - int(deceleration), acceleration=500)
        
    motor_pair.stop(motor_pair.PAIR_1)
    print("Final relative position = " + str(motor.relative_position(RIGHT_WHEEL_PORT)))
    return

#VKM: I did not change this
async def __moveBackwardProporational(rotations, velocity, brakeStartPercentage):
    print("Move Backward Proportional. Rotations = " + str(rotations) + ". Velocity = " + str(velocity) + ", Brake = " + str(brakeStartPercentage))

    #this value will be different for each robot
    CORRECTION_MULTIPLIER = -3.5

    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    degrees = rotations * 360
    motor.reset_relative_position(RIGHT_WHEEL_PORT, 0) #using right wheel port as its relative position is positive while moving forward on test robot
    brakeStartDistance = degrees * brakeStartPercentage
    endSpeed = LARGE_MOTOR_MAX_VELOCITY * .1 #10% speed is slowest to go in order for motor to complete distance

    while (motor.relative_position(RIGHT_WHEEL_PORT) > degrees):
        error = motion_sensor.tilt_angles()[0] * -0.1 #gyro reading should be 0 if robot is moving straight
        correction = int(error * CORRECTION_MULTIPLIER)
        #print("Correction = " + str(correction))

        deceleration = 0
        degreesTraveled = motor.relative_position(RIGHT_WHEEL_PORT)

        if(degreesTraveled < brakeStartDistance):
            deceleration = max(velocity * degreesTraveled/degrees, velocity + endSpeed)  #deceleration is negative when moving backwards
        #print("Deceleration = ", deceleration)
        #print("Speed = ", velocity + correction - int(deceleration))

        motor_pair.move_tank(motor_pair.PAIR_1, velocity + correction - int(deceleration), velocity - correction - int(deceleration), acceleration=500)

    motor_pair.stop(motor_pair.PAIR_1)
    print("Final relative position = " + str(motor.relative_position(RIGHT_WHEEL_PORT)))

    return


#Moves straight using the gyro sensor to correct drift.
#Input parameters:stoppingRotations = positive value if going forward and negative if going backward
#                velocityPercentage = 0 to +100. 
#                brakeStartValue (optional): Decimal percentage of the driven distance after which the robot starts braking.
async def moveStraightWheelRotation(myConfig:RobotConfig, stoppingRotations, brakeStartValue = 0.9):
    print("MoveStraightWheelRotations")
    
    velocity = myConfig.getMainMotorVelocity()
    
    if(stoppingRotations > 0):
        await __moveForwardProporational(stoppingRotations, int(velocity), brakeStartValue)
    else:
        await __moveBackwardProporational(stoppingRotations, int(velocity * -1), brakeStartValue)


# Gyro reset 
async def __gyroReset():
    motion_sensor.reset_yaw(0)
    await motion_sensor.stable()
    return
 
# Sensor reset
async def allSensorReset():
    print("Sensor check/reset start---")
    print("\tResetting Gyro...")
    __gyroReset()
    
    # can display values from other sensors     
    print("\tStopping sound...")
    await sound.stop()    
    
    print("\tClearing lights...")
    await light_matrix.clear()
    print("Sensor check/reset complete---")
    return
    
