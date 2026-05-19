from hub import light_matrix, motion_sensor, port, sound
import hub
import runloop, motor, motor_pair, sys, time
import rockstar_classes

LARGE_MOTOR_MAX_VELOCITY = 1050
LEFT_WHEEL_PORT = port.A
RIGHT_WHEEL_PORT = port.E


#Returns true if the gyro yaw angle has reached the degreesToTurn value indicating that a turn has been completed.
def __turnCompleted(degreesToTurn) -> bool:
    #multiplying by -0.1 makes yaw angle match values in hub
    return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degreesToTurn)


#TODO: sdc: should RobotConfig have separate velocity variables for pivotTurns, spinTurns, and moving straight since these defaults are likely different?
#Completes a pivot turn up to 179 degrees.
#Input parameters:  degreesToTurn: positive value if turning to right and negative if turning to left
#                   velocity: (deg/sec) Large motor range = -1050 to 1050
async def pivotTurn(myConfig:RobotConfig, degreesToTurn) -> None:
    print("Pivot Turn")

    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    velocity = int(myConfig.getMainMotorVelocity())

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
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return


#Completes a spin turn up to 179 degrees.
#Input parameters:  degreesToTurn: positive value if turning to right and negative if turning to left
#                   velocity: (deg/sec) Large motor range = -1050 to 1050
async def spinTurn(myConfig:RobotConfig, degreesToTurn) -> None:
    print("Spin Turn")

    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)
    
    velocity = int(myConfig.getMainMotorVelocity())

    if(degreesToTurn > 0):
        motor_pair.move_tank(motor_pair.PAIR_1, velocity, -1 * velocity) #right turn
        #motor_pair.move(motor_pair.PAIR_1, 100, velocity=velocity) #alternative way to spin turn right
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, -1 * velocity, velocity) #left turn
        #motor_pair.move(motor_pair.PAIR_1, -100, velocity=velocity) #alternative way to spin turn left

    #lambda makes function with parameters callable since runloop.until() expects a function with no parameters
    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return


#TODO: velocity parameter types may be off (float versus int). Determine during testing
#Complete a pivot turn and slow down as the turn completes to ensure accuracy. 
#Input parameters: degreesToTurn: positive value if turning to right and negative if turning to left (-180 to 180)
#                  velocityPercentage (optional): how fast to complete the turn in percentage (1 to 100) 
#                  timeout (optional): maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached. 
async def proportionalPivotTurn(myConfig:RobotConfig, degreesToTurn) -> None:
    
    velocityPercentage = (myConfig.getMainMotorVelocity()/myConfig.LARGE_MOTOR_MAX_VELOCITY)*100
    timeout = myConfig.getTimeout()
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

#TODO: velocity parameter types may be off (float versus int) Determine during testing.
#Complete a spin turn and slow down as the turn completes to ensure accuracy.
#Input parameters:degreesToTurn: positive value if turning to right and negative if turning to left (-180 to 180)
#                velocityPercentage (optional): how fast to complete the turn in percentage (1 to 100)
#                timeout (optional): maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached.
async def proportionalSpinTurn(myConfig:RobotConfig, degreesToTurn) -> None:
    
    velocityPercentage = (myConfig.getMainMotorVelocity()/myConfig.LARGE_MOTOR_MAX_VELOCITY)*100
    timeout = myConfig.getTimeout()
    print("Proportional Spin Turn. DegreesToTurn = " + str(degreesToTurn) + ". velocityPercentage = " + str(velocityPercentage) + ", timeout(seconds) = " + str(timeout))
    
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

        turnPower = turnError * velocityPercentage/100 * LARGE_MOTOR_MAX_VELOCITY/50

        if(degreesToTurn > 0):
            motor_pair.move_tank(motor_pair.PAIR_1, int(turnPower), -1* int(turnPower)) #right turn
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, -1*int(turnPower), int(turnPower)) #left turn

        if(__turnCompleted(degreesToTurn)):
            print("Turn completed!")
            break

    motor_pair.stop(motor_pair.PAIR_1)
    print("Time out!")

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return


#TODO: sdc: should acceleration and deceleration be added to RobotConfig?
#TODO: test case where both velocity and stopping rotations are negative
#Moves straight (without using the gyro sensor).
#Input parameters:stoppingRotations: positive value if going forward and negative if going backward
#                velocityPercentage: 0% to 100%.
#                acceleration (optional): (deg/sec^2) Default is 500.
#                deceleration (optional): (deg/sec^2) Default is 1000.
async def moveForward(myConfig:RobotConfig, stoppingRotations, acceleration = 500, deceleration = 1000) -> None:
    velocity = int(myConfig.getMainMotorVelocity())
    print("In moveForward function, rotations to move = " + str(stoppingRotations) + ", velocity = " + str(velocity) + ", acceleration = " + str(acceleration) + ", deceleration = " + str(deceleration) + ".")

    degreesToMove = stoppingRotations * 360

    await motor_pair.move_for_degrees(motor_pair.PAIR_1, degreesToMove, 0, velocity=int(velocity), stop=motor.BRAKE, acceleration=acceleration, deceleration=deceleration)
    return


async def __moveForwardProporational(rotations, velocity, acceleration = 500, brakeStartPercentage = 0.9, correctionMultiplier = -1.5) -> None:
    print("Move Forward Proportional. Rotations = " + str(rotations) + ", Velocity = " + str(velocity) + ", Acceleration = " + str(acceleration) + ", Brake = " + str(brakeStartPercentage) + ", Correction Multiplier = " + str(correctionMultiplier))

    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    degrees = rotations * 360
    motor.reset_relative_position(RIGHT_WHEEL_PORT, 0) #using right wheel port as its relative position is positive while moving forward on test robot
    brakeStartDistance = degrees * brakeStartPercentage
    endSpeed = LARGE_MOTOR_MAX_VELOCITY * .1 #10% speed is slowest to go in order for motor to complete distance

    while (motor.relative_position(RIGHT_WHEEL_PORT) < degrees):
        error = motion_sensor.tilt_angles()[0] * -0.1 #gyro reading should be 0 if robot is moving straight
        correction = int(error * correctionMultiplier)
        #print("Correction = " + str(correction))
 
        deceleration = 0
        degreesTraveled = motor.relative_position(RIGHT_WHEEL_PORT)
        
        if(degreesTraveled > brakeStartDistance): 
            deceleration = min(velocity * degreesTraveled/degrees, velocity - endSpeed)

        motor_pair.move_tank(motor_pair.PAIR_1, velocity + correction - int(deceleration), velocity - correction - int(deceleration), acceleration=acceleration)
        
    motor_pair.stop(motor_pair.PAIR_1)
    print("Final relative position = " + str(motor.relative_position(RIGHT_WHEEL_PORT)))
    return


async def __moveBackwardProporational(rotations, velocity, acceleration = 500, brakeStartPercentage = 0.9, correctionMultiplier = -3.5) -> None:
    print("Move Backward Proportional. Rotations = " + str(rotations) + ", Velocity = " + str(velocity) + ", Acceleration = " + str(acceleration) + ", Brake = " + str(brakeStartPercentage) + ", Correction Multiplier = " + str(correctionMultiplier))

    motion_sensor.reset_yaw(0)
    await runloop.until(motion_sensor.stable)

    degrees = rotations * 360
    motor.reset_relative_position(RIGHT_WHEEL_PORT, 0) #using right wheel port as its relative position is positive while moving forward on test robot
    brakeStartDistance = degrees * brakeStartPercentage
    endSpeed = LARGE_MOTOR_MAX_VELOCITY * .1 #10% speed is slowest to go in order for motor to complete distance

    while (motor.relative_position(RIGHT_WHEEL_PORT) > degrees):
        error = motion_sensor.tilt_angles()[0] * -0.1 #gyro reading should be 0 if robot is moving straight
        correction = int(error * correctionMultiplier)
        #print("Correction = " + str(correction))

        deceleration = 0
        degreesTraveled = motor.relative_position(RIGHT_WHEEL_PORT)

        if(degreesTraveled < brakeStartDistance):
            deceleration = max(velocity * degreesTraveled/degrees, velocity + endSpeed)  #deceleration is negative when moving backwards
        #print("Deceleration = ", deceleration)
        #print("Speed = ", velocity + correction - int(deceleration))

        motor_pair.move_tank(motor_pair.PAIR_1, velocity + correction - int(deceleration), velocity - correction - int(deceleration), acceleration=acceleration)

    motor_pair.stop(motor_pair.PAIR_1)
    print("Final relative position = " + str(motor.relative_position(RIGHT_WHEEL_PORT)))

    return


#TODO: sdc: needs to handle case where both stoppingRotations and velocity are negative. Code expects stoppingRotations to be only one that can be negative on initial call.
#TODO: should correctionMultiplier be added to RobotConfig? Different correction multipliers may be best for forward versus backward movement.
#TODO: should acceleration and brakeStartValue be added to RobotConfig?
#Moves straight using the gyro sensor to correct drift.
#Input parameters:  stoppingRotations: positive value if going forward and negative if going backward
#                   velocityPercentage: 0 to +100. 
#                   acceleration (optional): (deg/sec^2) Default is 500.
#                   brakeStartValue (optional): Decimal percentage of the driven distance after which the robot starts braking.
#                   correctionMultiplier (optional): Used to determine how sharply to correct drift. Must be negative, and lower values make sharper corrections. 
#                                                    Typical values are -1 to -5. 
async def moveStraightWheelRotation(myConfig:RobotConfig, stoppingRotations, acceleration=500, brakeStartValue = 0.9, correctionMultiplier = -3.5) -> None:
    velocity = int(myConfig.getMainMotorVelocity())
    print("MoveStraightWheelRotations. Stopping Rotations =" + str(stoppingRotations) + ". Velocity = " + str(velocity) + ", Acceleration = " + str(acceleration) + ", Brake Start Value = " + str(brakeStartValue) + ", Correction Multiplier = " + str(correctionMultiplier) + ".")
    
    #velocity = LARGE_MOTOR_MAX_VELOCITY * abs(velocityPercentage)/100  #negative values for velocity are not allowed so take absolute value
    
    if(stoppingRotations > 0):
        await __moveForwardProporational(stoppingRotations, int(velocity), acceleration, brakeStartValue, correctionMultiplier)
    else:
        await __moveBackwardProporational(stoppingRotations, int(velocity * -1), acceleration, brakeStartValue, correctionMultiplier)
    
    return
