from hub import light_matrix, motion_sensor, port, sound
import hub
import runloop, motor, motor_pair, sys, time, color_sensor, color

#LARGE_MOTOR_MAX_VELOCITY = 1050
MEDIUM_MOTOR_MAX_VELOCITY = 1110
WHEEL_MOTOR_MAX_VELOCITY = MEDIUM_MOTOR_MAX_VELOCITY
LEFT_WHEEL_PORT = port.C
RIGHT_WHEEL_PORT = port.E
WHEEL_BASE_IN_CENTIMETERS = 8.8  #measured from center of each tire (tires are 2 cm thick)

BLACK_LINE_LIGHT_REFLECTION = 50
WHITE_LINE_LIGHT_REFLECTION = 95
BLACK_LINE_RIGHT_EDGE = "Right"
BLACK_LINE_LEFT_EDGE = "Left"


#Returns true if the gyro yaw angle has reached the degreesToTurn value indicating that a turn has been completed.
def __turnCompleted(degreesToTurn) -> bool:
    #multiplying by -0.1 makes yaw angle match values in hub
    return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degreesToTurn)


async def pivotTurn(degreesToTurn, velocity) -> None:
    '''Completes a pivot turn up to 179 degrees. \n
            Input parameters:
                degreesToTurn: positive value if turning to right and negative if turning to left
                velocity: (deg/sec) Medium motor range = -1110 to 1110
    '''
    
    print("In pivotTurn, degreesToTurn = " + str(degreesToTurn) + ", velocity = " + str(velocity) + ".")

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


async def spinTurn(degreesToTurn, velocity) -> None:
    '''Completes a spin turn up to 179 degrees. \n
            Input parameters:
                degreesToTurn: positive value if turning to right and negative if turning to left
                velocity: (deg/sec) Medium motor range = -1110 to 1110
    '''
    
    print("In spinTurn, degreesToTurn = " + str(degreesToTurn) + ", velocity = " + str(velocity) + ".")

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


async def arcTurn(radiusInCm, degreesToTurn, velocityPercentage=20) -> None:
    '''Completes an arc turn up to 179 degrees. \n 
            Input parameters:   
                radiusInCm: radius of circle (in centimeters) that robot moves while making its arc turn. A value of 0 equates to a spin turn (use dedicated spin turn functions instead).
                degreesToTurn: positive value if turning to right and negative if turning to left
                velocityPercentage (optional): how fast to complete the turn in percentage (1 to 100). Negative values move backward.
    '''
    
    print("Arc Turn. radiusInCm = " + str(radiusInCm) + ", degreesToTurn = " + str(degreesToTurn) + ", velocityPercentage = " + str(velocityPercentage) + ".")

    velocity = velocityPercentage/100 * WHEEL_MOTOR_MAX_VELOCITY

    halfWheelBase = WHEEL_BASE_IN_CENTIMETERS / 2.0
    innerWheelRadius = radiusInCm - halfWheelBase
    outerWheelRadius = radiusInCm + halfWheelBase
    wheelRadiusRatio = innerWheelRadius/outerWheelRadius  #-1.0 for a spin turn

    #steering is 0 when straight with a max of 100 (pivot turn). Higher values slow or reverse the inner wheel.
    steering = int((1 - wheelRadiusRatio) * 50)

    if degreesToTurn < 0: 
        steering = -steering

    motion_sensor.reset_yaw(0)
    time.sleep(0.1) #reset yaw can take a bit of time to complete
    motor_pair.move(motor_pair.PAIR_1, steering, velocity=int(velocity))

    #lambda makes function with parameters callable since runloop.until() expects a function with no parameters
    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)
    return


async def proportionalPivotTurn(degreesToTurn, velocityPercentage = 40, timeout = 2.0) -> None:
    '''Complete a pivot turn and slow down as the turn completes to ensure accuracy. \n
            Input parameters: 
                degreesToTurn: positive value if turning to right and negative if turning to left (-179 to 179)
                velocityPercentage (optional): how fast to complete the turn in percentage (1 to 100)
                timeout (optional): maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached.
    '''
    
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

        turnPower = turnError * velocityPercentage/100 * WHEEL_MOTOR_MAX_VELOCITY/40  #pivot turns are slower so take a larger percentage of the max velocity 

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


async def proportionalSpinTurn(degreesToTurn, velocityPercentage = 30, timeout = 2.0) -> None:
    '''Complete a spin turn and slow down as the turn completes to ensure accuracy. \n
        Input parameters:
            degreesToTurn: positive value if turning to right and negative if turning to left (-179 to 179)
            velocityPercentage (optional): how fast to complete the turn in percentage (1 to 100)
            timeout (optional): maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached.
    '''
    
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

        turnPower = turnError * velocityPercentage/100 * WHEEL_MOTOR_MAX_VELOCITY/50

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


async def moveForward(stoppingRotations, velocityPercentage, acceleration = 500, deceleration = 1000) -> None:
    '''Moves straight (without using the gyro sensor). \n
            Input parameters:
                stoppingRotations: positive value if going forward and negative if going backward
                velocityPercentage: 0% to 100%.
                acceleration (optional): (deg/sec^2) Default is 500.
                deceleration (optional): (deg/sec^2) Default is 1000.
    '''

    print("In moveForward function, rotations to move = " + str(stoppingRotations) + ", velocityPercentage = " + str(velocityPercentage) + ", acceleration = " + str(acceleration) + ", deceleration = " + str(deceleration) + ".")

    degreesToMove = stoppingRotations * 360
    velocity = WHEEL_MOTOR_MAX_VELOCITY * velocityPercentage/100

    await motor_pair.move_for_degrees(motor_pair.PAIR_1, int(degreesToMove), 0, velocity=int(velocity), stop=motor.BRAKE, acceleration=acceleration, deceleration=deceleration)
    return


async def __moveForwardProporational(rotations, velocity, acceleration = 500, brakeStartPercentage = 0.9, correctionMultiplier = -1.5) -> None:
    print("Move Forward Proportional. Rotations = " + str(rotations) + ", Velocity = " + str(velocity) + ", Acceleration = " + str(acceleration) + ", Brake = " + str(brakeStartPercentage) + ", Correction Multiplier = " + str(correctionMultiplier))

    motion_sensor.reset_yaw(0)
    #await runloop.until(motion_sensor.stable)

    degrees = rotations * 360
    motor.reset_relative_position(RIGHT_WHEEL_PORT, 0) #using right wheel port as its relative position is positive while moving forward on test robot
    brakeStartDistance = degrees * brakeStartPercentage
    endSpeed = WHEEL_MOTOR_MAX_VELOCITY * .1 #10% speed is slowest to go in order for motor to complete distance

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
    endSpeed = WHEEL_MOTOR_MAX_VELOCITY * .1 #10% speed is slowest to go in order for motor to complete distance

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


async def moveStraightWheelRotation(stoppingRotations, velocityPercentage, acceleration=500, brakeStartValue = 0.9, correctionMultiplier = -3.5) -> None:
    '''Moves straight using the gyro sensor to correct drift. \n
        Input parameters:
            stoppingRotations: positive value if going forward and negative if going backward
            velocityPercentage: 0 to +100.
            acceleration (optional): (deg/sec^2) Default is 500.
            brakeStartValue (optional): Decimal percentage of the driven distance after which the robot starts braking.
            correctionMultiplier (optional): Used to determine how sharply to correct drift. Must be negative, and lower values make sharper corrections.
                                             Typical values are -1 to -5.
    '''
    
    print("MoveStraightWheelRotations. Stopping Rotations =" + str(stoppingRotations) + ". Velocity % = " + str(velocityPercentage) + ", Acceleration = " + str(acceleration) + ", Brake Start Value = " + str(brakeStartValue) + ", Correction Multiplier = " + str(correctionMultiplier) + ".")
    velocity = WHEEL_MOTOR_MAX_VELOCITY * abs(velocityPercentage)/100  #negative values for velocity are not allowed so take absolute value
    
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
async def moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine=False, velocityPercentage=25, acceleration=500) -> int:
    '''Moves straight ahead until one of the two light sensors finds the line with the inputted line color. \n
        Input parameters:
            leftLightSensorPort: port number of left light sensor (ex port.B)
            rightLightSensorPort: port number of right light sensor (ex. port.D)
            lineColor: color of line to stop at (color.BLACK or color.WHITE)
            bothSensorsOnLine (optional): True if robot should run until both light sensors are on line. False if robot should stop once first light sensor is on line.
            velocityPercentage (optional): how fast (-100% to 100%) to move in a straight line. Negative values move backwards.
            acceleration (optional): (deg/sec^2) Default is 500.
            Note: ideal height of light sensor off of ground is 16mm (2 Lego blocks)
    '''
    
    print("In moveStraightUntilLine function, left light sensor port = " + str(leftLightSensorPort) + ", right light sensor port = " + str(rightLightSensorPort) + ", line color = " + 
            str(lineColor) + ", velocityPercentage = " + str(velocityPercentage)  + ", acceleration = " + str(acceleration) + ".")

    velocity = WHEEL_MOTOR_MAX_VELOCITY * velocityPercentage/100
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


async def getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage=25, acceleration=500) -> None: 
    '''@deprecated("Use squareUpOnLine instead.")
        Rotates robot until second light sensor finds the colored line.
            Input parameters:
                leftLightSensorPort: port where left light sensor is connected (ex. port.B)
                rightLightSensorPort: port where right light sensor is connected (ex. port.D)
                lightColor: color of line to search for (color.BLACK or color.WHITE)
                velocityPercentage (optional): 0% to 100%.
                acceleration (optional): (deg/sec^2) Default is 500.
    '''
    
    print("In getSecondLightSensorOnLine function, left light sensor port = " + str(leftLightSensorPort) + ", right light sensor port = " + str(rightLightSensorPort) + ", line color = " +
            str(lineColor) + ", velocityPercentage = " + str(velocityPercentage)+ ", acceleration = " + str(acceleration) + ".")

    velocity = WHEEL_MOTOR_MAX_VELOCITY * velocityPercentage/100

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


async def squareUpOnLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage=15, acceleration=500) -> None: 
    '''Squares up robot on black line by stopping each motor as its corresponding light sensor sees the black line. For best results, 
       run at lower speeds and back robot off line after first call and run a second time.
        Input parameters:
            leftLightSensorPort: port where left light sensor is connected (ex. port.B)
            rightLightSensorPort: port where right light sensor is connected (ex. port.D)
            lineColor: color of line to stop at (color.BLACK or color.WHITE)
            velocityPercentage (optional): 0% to 100%.
            acceleration (optional): (deg/sec^2) Default is 500.
    '''
    
    print("squareUpOnLine leftLightSensorPort = " + str(leftLightSensorPort) + ", rightLightSensorPort = " + str(rightLightSensorPort) + ", lineColor = " + str(lineColor) + 
            ", velocityPercentage = " + str(velocityPercentage) + ", acceleration = " + str(acceleration) + ".")
    
    velocity = WHEEL_MOTOR_MAX_VELOCITY * velocityPercentage/100
    motor.run(LEFT_WHEEL_PORT, int(-velocity), acceleration=acceleration)  #left wheel uses negative velocity due to mirrored placement of motor
    motor.run(RIGHT_WHEEL_PORT, int(velocity), acceleration=acceleration)

    leftSensorFoundLine = False
    rightSensorFoundLine = False
 
    # wait for color sensors to detect black or white line and stop matching motor
    while (not leftSensorFoundLine or not rightSensorFoundLine):
        if(lineColor == color.BLACK):
            if(color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION):
                motor.stop(LEFT_WHEEL_PORT)
                leftSensorFoundLine = True
            if(color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION):
                motor.stop(RIGHT_WHEEL_PORT)
                rightSensorFoundLine = True
        elif(lineColor == color.WHITE):
            if(color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION):
                motor.stop(LEFT_WHEEL_PORT)
                leftSensorFoundLine = True
            if(color_sensor.reflection(rightLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION):
                motor.stop(RIGHT_WHEEL_PORT)
                rightSensorFoundLine = True
        else:
            print("Line color of " + str(lineColor) + " is invalid.")
    
    return


async def pidBlackLineFollow(rotationsToMove, lightSensorPort, midPointReflectionPercentage, edgeToFollow, proportionalCorrectionCoef=0.15, integralCorrectionCoef = 0.0, derivativeCorrectionCoef = 0.0, velocityPercentage=10, acceleration=500) -> None:
    '''Follows black line using the light sensor. Meant to be used for forward movement only currently. \n
        Input parameters:
            rotationsToMove: Number of rotations to move while following line.
            lightSensorPort: port where light sensor to use for following black line is connected (ex. port.B)
            midPointReflectionPercentage: Average of white and black reflection readings (in percentage) from the light sensor on the board.
            edgeToFollow: whether to follow the black line on the left (BLACK_LINE_LEFT_EDGE) or right (BLACK_LINE_RIGHT_EDGE)
            proportionalCorrectionCoef: value between 0 and 1 that determines how aggressively to make corrections to movement (Tune this first.)
            integralCorrectionCoef: corrects steady drift (Tune this last. Should be small value ex. 0.05)
            derivativeCorrectionCoef: smoothes overcorrections (Tune this second after proportionalCorrectionCoef. Ex. 3.0)
            velocityPercentage (optional): 0% to 100%.
            acceleration (optional): (deg/sec^2) Default is 500.
    '''
    
    print("In pidBlackLineFollow, rotationsToMove = " + str(rotationsToMove) + ", lightSensorPort = " + str(lightSensorPort) + ", midPointReflectionPercentage = " + str(midPointReflectionPercentage) +
            ", edgeToFollow = " + str(edgeToFollow) + ", proportionalCorrectionCoef = " + str(proportionalCorrectionCoef) + ", integralCorrectionCoef = " + 
            str(integralCorrectionCoef) + ", derivativeCorrectionCoef = " + str(derivativeCorrectionCoef) + ", velocity% = " + str(velocityPercentage) +
            ", acceleration = " + str(acceleration) + ".")

    velocity = WHEEL_MOTOR_MAX_VELOCITY * velocityPercentage/100
    degreesToMove = rotationsToMove * 360
    motor.reset_relative_position(RIGHT_WHEEL_PORT, 0)
    
    lastError = 0.0 #stores previous light sensor error reading
    integral = 0.0

    #stop following line after wheel moves the inputted degrees
    while(abs(motor.relative_position(RIGHT_WHEEL_PORT)) < abs(degreesToMove)):
        error = midPointReflectionPercentage - color_sensor.reflection(lightSensorPort)
       
        #corrects steady drift (tune this last after proportional and derivative values)
        integral = integral + error #adds error to previous integral drift
        integral = max(-100, min(100, integral)) #keeps intregal between -100 and 100 so that drift doesn't pile up
        
        #smoothes overcorrections (tune this second after proportional error term)
        derivative = error - lastError 
        
        lastError = error #reset previous error value after it has been used in calculation
        
        turnCorrectionPercentage = proportionalCorrectionCoef * error + integralCorrectionCoef * integral + derivativeCorrectionCoef * derivative
        turnCorrectionAmount = WHEEL_MOTOR_MAX_VELOCITY * turnCorrectionPercentage/100

        if(edgeToFollow == BLACK_LINE_RIGHT_EDGE):
            motor_pair.move_tank(motor_pair.PAIR_1, int(velocity + turnCorrectionAmount), int(velocity - turnCorrectionAmount), acceleration=acceleration)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, int(velocity - turnCorrectionAmount), int(velocity + turnCorrectionAmount), acceleration=acceleration)
        
        #runloop.sleep_ms(5)

    motor_pair.stop(motor_pair.PAIR_1)
    print("Degrees moved = ", motor.relative_position(RIGHT_WHEEL_PORT))
