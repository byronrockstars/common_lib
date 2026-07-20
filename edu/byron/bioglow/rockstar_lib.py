from hub import light_matrix, motion_sensor, port, sound
import hub
import runloop, motor, motor_pair, sys, time, color_sensor, color

#LARGE_MOTOR_MAX_VELOCITY = 1050
LARGE_MOTOR_MAX_VELOCITY = 1110 #this is actually a medium motor being used to power the wheels
BLACK_LINE_LIGHT_REFLECTION = 50
WHITE_LINE_LIGHT_REFLECTION = 95
LEFT_WHEEL_PORT = port.A
RIGHT_WHEEL_PORT = port.E
BLACK_LINE_RIGHT_EDGE = "Right"
BLACK_LINE_LEFT_EDGE = "Left"


#Returns true if the gyro yaw angle has reached the degreesToTurn value indicating that a turn has been completed.
def __turnCompleted(degreesToTurn) -> bool:
    #multiplying by -0.1 makes yaw angle match values in hub
    return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degreesToTurn)


#Completes a pivot turn up to 179 degrees.
#Input parameters:  degreesToTurn: positive value if turning to right and negative if turning to left
#                   velocity: (deg/sec) Large motor range = -1050 to 1050
async def pivotTurn(degreesToTurn, velocity) -> None:
    print("Pivot Turn")

    motion_sensor.reset_yaw(0)
    time.sleep(0.1) #reset yaw can take a bit of time to complete
    #await runloop.until(motion_sensor.stable) #commented out because this check was taking too long each call for little gain

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
async def spinTurn(degreesToTurn, velocity) -> None:
    print("Spin Turn")

    motion_sensor.reset_yaw(0)
    time.sleep(0.1) #reset yaw can take a bit of time to complete
    #await runloop.until(motion_sensor.stable)

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


#Complete a pivot turn and slow down as the turn completes to ensure accuracy. 
#Input parameters: degreesToTurn: positive value if turning to right and negative if turning to left (-180 to 180)
#                  velocityPercentage (optional): how fast to complete the turn in percentage (1 to 100) 
#                  timeout (optional): maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached. 
async def proportionalPivotTurn(degreesToTurn, velocityPercentage = 40, timeout = 2.0) -> None:
    print("Proportional Pivot Turn. DegreesToTurn = " + str(degreesToTurn) + ". velocityPercentage = " + str(velocityPercentage) + ", timeout(seconds) = " + str(timeout))

    motion_sensor.reset_yaw(0)
    time.sleep(0.1) #reset yaw can take a bit of time to complete
    #await runloop.until(motion_sensor.stable)

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


#Complete a spin turn and slow down as the turn completes to ensure accuracy.
#Input parameters:degreesToTurn: positive value if turning to right and negative if turning to left (-180 to 180)
#                velocityPercentage (optional): how fast to complete the turn in percentage (1 to 100)
#                timeout (optional): maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached.
async def proportionalSpinTurn(degreesToTurn, velocityPercentage = 30, timeout = 2.0) -> None:
    print("Proportional Spin Turn. DegreesToTurn = " + str(degreesToTurn) + ". velocityPercentage = " + str(velocityPercentage) + ", timeout(seconds) = " + str(timeout))

    motion_sensor.reset_yaw(0)
    time.sleep(0.1) #reset yaw can take a bit of time to complete
    #await runloop.until(motion_sensor.stable)

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


#Moves straight (without using the gyro sensor).
#Input parameters:stoppingRotations: positive value if going forward and negative if going backward
#                velocityPercentage: 0% to 100%.
#                acceleration (optional): (deg/sec^2) Default is 500.
#                deceleration (optional): (deg/sec^2) Default is 1000.
async def moveForward(stoppingRotations, velocityPercentage, acceleration = 500, deceleration = 1000) -> None:
    print("In moveForward function, rotations to move = " + str(stoppingRotations) + ", velocityPercentage = " + str(velocityPercentage) + ", acceleration = " + str(acceleration) + ", deceleration = " + str(deceleration) + ".")

    degreesToMove = stoppingRotations * 360
    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage/100

    await motor_pair.move_for_degrees(motor_pair.PAIR_1, degreesToMove, 0, velocity=int(velocity), stop=motor.BRAKE, acceleration=acceleration, deceleration=deceleration)
    return


async def __moveForwardProporational(rotations, velocity, acceleration = 500, brakeStartPercentage = 0.9, correctionMultiplier = -1.5) -> None:
    print("Move Forward Proportional. Rotations = " + str(rotations) + ", Velocity = " + str(velocity) + ", Acceleration = " + str(acceleration) + ", Brake = " + str(brakeStartPercentage) + ", Correction Multiplier = " + str(correctionMultiplier))

    motion_sensor.reset_yaw(0)
    #await runloop.until(motion_sensor.stable)

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
    #await runloop.until(motion_sensor.stable)

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


#Moves straight using the gyro sensor to correct drift.
#Input parameters:  stoppingRotations: positive value if going forward and negative if going backward
#                   velocityPercentage: 0 to +100. 
#                   acceleration (optional): (deg/sec^2) Default is 500.
#                   brakeStartValue (optional): Decimal percentage of the driven distance after which the robot starts braking.
#                   correctionMultiplier (optional): Used to determine how sharply to correct drift. Must be negative, and lower values make sharper corrections. 
#                                                    Typical values are -1 to -5. 
async def moveStraightWheelRotation(stoppingRotations, velocityPercentage, acceleration=500, brakeStartValue = 0.9, correctionMultiplier = -3.5) -> None:
    print("MoveStraightWheelRotations. Stopping Rotations =" + str(stoppingRotations) + ". Velocity % = " + str(velocityPercentage) + ", Acceleration = " + str(acceleration) + ", Brake Start Value = " + str(brakeStartValue) + ", Correction Multiplier = " + str(correctionMultiplier) + ".")
    velocity = LARGE_MOTOR_MAX_VELOCITY * abs(velocityPercentage)/100  #negative values for velocity are not allowed so take absolute value
    
    if(stoppingRotations > 0):
        await __moveForwardProporational(stoppingRotations, int(velocity), acceleration, brakeStartValue, correctionMultiplier)
    else:
        await __moveBackwardProporational(stoppingRotations, int(velocity * -1), acceleration, brakeStartValue, correctionMultiplier)
    
    return


def __blackLineFound(leftLightSensorPort, rightLightSensorPort, bothSensorsOnLine) -> bool:
    #print("Left sensor reflection value: ", color_sensor.reflection(leftLightSensorPort))
    #print("Right sensor reflection value: ", color_sensor.reflection(rightLightSensorPort))
    
    #alternate way to determine black line but may not work as consistently as light reflection
    #color_sensor.color(leftLightSensorPort) == color.BLACK or color_sensor.color(rightLightSensorPort) == color.BLACK

    if bothSensorsOnLine:
        return (color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION and color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION)
    else:
        return (color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION or color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION)


def __whiteLineFound(leftLightSensorPort, rightLightSensorPort, bothSensorsOnLine) -> bool:
    #print("Left sensor reflection value: ", color_sensor.reflection(leftLightSensorPort))
    #print("Right sensor reflection value: ", color_sensor.reflection(rightLightSensorPort))
    
    if bothSensorsOnLine:
        return (color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION and color_sensor.reflection(rightLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION)
    else:
        return (color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION or color_sensor.reflection(rightLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION)


#TODO: allow for using gyro sensor to move
#Moves straight ahead until one of the two light sensors finds the line with the inputted line color.
#Input parameters:  leftLightSensorPort: port number of left light sensor (ex port.B)
#                   rightLightSensorPort: port number of right light sensor (ex. port.D)
#                   lineColor: color of line to stop at (color.BLACK or color.WHITE)
#                   bothSensorsOnLine (optional): True if robot should run until both light sensors are on line. False if robot should stop once first light sensor is on line.
#                   velocityPercentage (optional): how fast (-100% to 100%) to move in a straight line. Negative values move backwards.
#                   acceleration (optional): (deg/sec^2) Default is 500.
#Note: ideal height of light sensor off of ground is 16mm (2 Lego blocks)
async def moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine=False, velocityPercentage=25, acceleration=500) -> int:
    print("In moveStraightUntilLine function, left light sensor port = " + str(leftLightSensorPort) + ", right light sensor port = " + str(rightLightSensorPort) + ", line color = " + 
            str(lineColor) + ", velocityPercentage = " + str(velocityPercentage)  + ", acceleration = " + str(acceleration) + ".")

    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage/100
    motor_pair.move(motor_pair.PAIR_1, 0, velocity=int(velocity), acceleration=acceleration)  

    triggeredSensorPort = -1

    if(lineColor == color.BLACK):
        #lambda makes function with parameters callable since runloop.until() expects a function with no parameters
        await runloop.until(lambda: __blackLineFound(leftLightSensorPort, rightLightSensorPort, bothSensorsOnLine))

        if(color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION):
            triggeredSensorPort = leftLightSensorPort
        else:
            triggeredSensorPort = rightLightSensorPort
    elif(lineColor == color.WHITE):
        await runloop.until(lambda: __whiteLineFound(leftLightSensorPort, rightLightSensorPort, bothSensorsOnLine))

        if(color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION):
            triggeredSensorPort = leftLightSensorPort
        else:
            triggeredSensorPort = rightLightSensorPort
    else:
        print("Line color of " + str(lineColor) + " is invalid.")

    # stop and exit
    motor_pair.stop(motor_pair.PAIR_1)
    print("Triggered Sensor Port = ", triggeredSensorPort)
    print("Left light sensor reflection = " + str(color_sensor.reflection(leftLightSensorPort)))
    print("Right light sensor reflection = " + str(color_sensor.reflection(rightLightSensorPort)))

    return triggeredSensorPort


#Rotates robot until second light sensor finds the colored line.
#Input parameters:  leftLightSensorPort: port where left light sensor is connected (ex. port.B)
#                   rightLightSensorPort: port where right light sensor is connected (ex. port.D)
#                   lightColor: color of line to search for (color.BLACK or color.WHITE)
#                   velocityPercentage (optional): 0% to 100%.
#                   acceleration (optional): (deg/sec^2) Default is 500.
async def getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage=25, acceleration=500) -> None: 
    print("In getSecondLightSensorOnLine function, left light sensor port = " + str(leftLightSensorPort) + ", right light sensor port = " + str(rightLightSensorPort) + ", line color = " +
            str(lineColor) + ", velocityPercentage = " + str(velocityPercentage)+ ", acceleration = " + str(acceleration) + ".")

    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage/100

    if(lineColor == color.BLACK):
        if(color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION):
            print("Before movement, left light sensor on black line = ", color_sensor.reflection(leftLightSensorPort))
            #since left light sensor is already on black line, must move to the left to get right sensor on black line
            motor_pair.move_tank(motor_pair.PAIR_1, 0, int(velocity), acceleration=acceleration) 
            await runloop.until(lambda: color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION)
        else: 
            print("Before movement, left light sensor NOT on black = ", color_sensor.reflection(leftLightSensorPort))
            #since right light sensor is already on black line, must move to the right to get left sensor on black line
            motor_pair.move_tank(motor_pair.PAIR_1, int(velocity), 0, acceleration=acceleration)
            await runloop.until(lambda: color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION)
    elif(lineColor == color.WHITE):
        if(color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION):
            print("Before movement, left light sensor on white line = ", color_sensor.reflection(leftLightSensorPort))
            #since left light sensor is already on white line, must move to the left to get right sensor on white line
            motor_pair.move_tank(motor_pair.PAIR_1, 0, int(velocity), acceleration=acceleration)
            await runloop.until(lambda: color_sensor.reflection(rightLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION)
        else:
            print("Before movement, left light sensor NOT on white line = ", color_sensor.reflection(leftLightSensorPort))
            #since right light sensor is already on white line, must move to the right to get left sensor on white line
            motor_pair.move_tank(motor_pair.PAIR_1, int(velocity), 0, acceleration=acceleration)
            await runloop.until(lambda: color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION)
    else:
        print("Line color of " + str(lineColor) + " is invalid.")

    motor_pair.stop(motor_pair.PAIR_1)
    print("Left light sensor reflection = " + str(color_sensor.reflection(leftLightSensorPort)))
    print("Right light sensor reflection = " + str(color_sensor.reflection(rightLightSensorPort)))

    return


#Squares up robot on black line by moving off the line and then back on. 
#Input parameters:  leftLightSensorPort: port where left light sensor is connected (ex. port.B)
#                   rightLightSensorPort: port where right light sensor is connected (ex. port.D)
#                   leftMoveFirst (optional): If true, left wheel of robot will move first (best if left light sensor was first to find black line originally)
#                                  If false, right wheel of robot will move first (best if right light sensor was first to find black line originally)
#                   velocityPercentage (optional): 0% to 100%.
#                   acceleration (optional): (deg/sec^2) Default is 500.
async def squareUpOnBlackLine(leftLightSensorPort, rightLightSensorPort, leftMoveFirst = True, velocityPercentage=10, acceleration=500) -> None:
    print("In squareUpOnBlackLine function, left light sensor port = " + str(leftLightSensorPort) + ", right light sensor port = " + str(rightLightSensorPort) +
            ", leftMoveFirst = " + str(leftMoveFirst) + ", velocityPercentage = " + str(velocityPercentage) + ", acceleration = " + str(acceleration) + ".")

    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage/100
    
    if(leftMoveFirst):
        #back left wheel off black line
        await getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.WHITE, -1 * velocityPercentage)
        time.sleep(0.1)

        #back right wheel off black line
        await getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.WHITE, -1 * velocityPercentage)
        time.sleep(0.1)

        #move left wheel forward on black line
        await getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.BLACK, velocityPercentage)
        time.sleep(0.1)

        #move right wheel forward on black line
        await getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.BLACK, velocityPercentage)
    else:
        #back right wheel off black line
        motor_pair.move_tank(motor_pair.PAIR_1, 0, int(-1 * velocity), acceleration=acceleration)
        await runloop.until(lambda: color_sensor.reflection(rightLightSensorPort) > BLACK_LINE_LIGHT_REFLECTION)
        motor_pair.stop(motor_pair.PAIR_1)
        time.sleep(0.1)

        #back left wheel off black line
        await getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.WHITE, -1 * velocityPercentage)
        time.sleep(0.1)

        #move right wheel forward on black line   
        motor_pair.move_tank(motor_pair.PAIR_1, 0, int(velocity), acceleration=acceleration)
        await runloop.until(lambda: color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION)
        motor_pair.stop(motor_pair.PAIR_1)
        time.sleep(0.1)

        #move left wheel forward on black line
        await getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.BLACK, velocityPercentage)

    return


#Follows black line using the light sensor.
#Input parameters:  lightSensorPort: port where light sensor to use for following black line is connected (ex. port.B)
#                   midPointReflectionPercentage: Average of white and black reflection readings (in percentage) from the light sensor on the board.
#                   edgeToFollow: whether to follow the black line on the left (BLACK_LINE_LEFT_EDGE) or right (BLACK_LINE_RIGHT_EDGE)
#                   correctionCoef: value between 0 and 1 that determines how aggressively to make corrections to movement
#                   velocityPercentage (optional): 0% to 100%.
#                   acceleration (optional): (deg/sec^2) Default is 500.
async def proportionalBlackLineFollow(lightSensorPort, midPointReflectionPercentage, edgeToFollow, correctionCoef=0.4, velocityPercentage=10, acceleration=500) -> None:
    print("In proportionalBlackLineFollow function, lightSensorPort = " + str(lightSensorPort) + ", midPointReflectionPercentage = " + str(midPointReflectionPercentage) + 
            ", edgeToFollow = " + str(edgeToFollow) + ", correctionCoef = " + str(correctionCoef) + ", velocityPercentage = " + str(velocityPercentage) + 
            ", acceleration = " + str(acceleration) + ".")

    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage/100

    #TODO: add stopping condition    
    while(1):
        turnCorrectionPercentage = correctionCoef * (midPointReflectionPercentage - color_sensor.reflection(lightSensorPort))
        turnCorrectionAmount = LARGE_MOTOR_MAX_VELOCITY * turnCorrectionPercentage/100
        
        if(edgeToFollow == BLACK_LINE_RIGHT_EDGE):
            motor_pair.move_tank(motor_pair.PAIR_1, int(velocity + turnCorrectionAmount), int(velocity - turnCorrectionAmount), acceleration=acceleration)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, int(velocity - turnCorrectionAmount), int(velocity + turnCorrectionAmount), acceleration=acceleration)