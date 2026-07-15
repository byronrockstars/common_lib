from hub import light_matrix, motion_sensor, port, sound
import hub
import runloop, motor, motor_pair, sys, time, color_sensor, color
LARGE_MOTOR_MAX_VELOCITY = 1050
BLACK_LINE_LIGHT_REFLECTION = 50
WHITE_LINE_LIGHT_REFLECTION = 95
LEFT_WHEEL_PORT = port.A
RIGHT_WHEEL_PORT = port.E

def __turnCompleted(degreesToTurn) -> bool:
    return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degreesToTurn)

async def _pivotTurn(degreesToTurn, velocity) -> None:
    print('Pivot Turn')
    motion_sensor.reset_yaw(0)
    time.sleep(0.1)
    if degreesToTurn > 0:
        motor_pair.move_tank(motor_pair.PAIR_1, velocity, 0)
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, 0, velocity)
    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)
    print('Degrees turned: ', motion_sensor.tilt_angles()[0] * -0.1)
    return

async def _spinTurn(degreesToTurn, velocity) -> None:
    print('Spin Turn')
    motion_sensor.reset_yaw(0)
    time.sleep(0.1)
    if degreesToTurn > 0:
        motor_pair.move_tank(motor_pair.PAIR_1, velocity, -1 * velocity)
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, -1 * velocity, velocity)
    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)
    print('Degrees turned: ', motion_sensor.tilt_angles()[0] * -0.1)
    return

async def _proportionalPivotTurn(degreesToTurn, velocityPercentage=40, timeout=2.0) -> None:
    print('Proportional Pivot Turn. DegreesToTurn = ' + str(degreesToTurn) + '. velocityPercentage = ' + str(velocityPercentage) + ', timeout(seconds) = ' + str(timeout))
    motion_sensor.reset_yaw(0)
    time.sleep(0.1)
    startTime = time.ticks_ms()
    print('Start time: ', startTime)
    while time.ticks_diff(time.ticks_ms(), startTime) < timeout * 1000:
        if degreesToTurn > 0:
            turnError = degreesToTurn - motion_sensor.tilt_angles()[0] * -0.1
        else:
            turnError = motion_sensor.tilt_angles()[0] * -0.1 - degreesToTurn
        turnPower = turnError * velocityPercentage / 100 * LARGE_MOTOR_MAX_VELOCITY / 40
        if degreesToTurn > 0:
            motor_pair.move_tank(motor_pair.PAIR_1, int(turnPower), 0)
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, 0, int(turnPower))
        if __turnCompleted(degreesToTurn):
            print('Turn completed!')
            break
    print('Time out!')
    motor_pair.stop(motor_pair.PAIR_1)
    print('Degrees turned: ', motion_sensor.tilt_angles()[0] * -0.1)
    return

async def _proportionalSpinTurn(degreesToTurn, velocityPercentage=30, timeout=2.0) -> None:
    print('Proportional Spin Turn. DegreesToTurn = ' + str(degreesToTurn) + '. velocityPercentage = ' + str(velocityPercentage) + ', timeout(seconds) = ' + str(timeout))
    motion_sensor.reset_yaw(0)
    time.sleep(0.1)
    startTime = time.ticks_ms()
    print('Start time: ', startTime)
    while time.ticks_diff(time.ticks_ms(), startTime) < timeout * 1000:
        if degreesToTurn > 0:
            turnError = degreesToTurn - motion_sensor.tilt_angles()[0] * -0.1
        else:
            turnError = motion_sensor.tilt_angles()[0] * -0.1 - degreesToTurn
        turnPower = turnError * velocityPercentage / 100 * LARGE_MOTOR_MAX_VELOCITY / 50
        if degreesToTurn > 0:
            motor_pair.move_tank(motor_pair.PAIR_1, int(turnPower), -1 * int(turnPower))
        else:
            motor_pair.move_tank(motor_pair.PAIR_1, -1 * int(turnPower), int(turnPower))
        if __turnCompleted(degreesToTurn):
            print('Turn completed!')
            break
    motor_pair.stop(motor_pair.PAIR_1)
    print('Time out!')
    print('Degrees turned: ', motion_sensor.tilt_angles()[0] * -0.1)
    return

async def _moveForward(stoppingRotations, velocityPercentage, acceleration=500, deceleration=1000) -> None:
    print('In moveForward function, rotations to move = ' + str(stoppingRotations) + ', velocityPercentage = ' + str(velocityPercentage) + ', acceleration = ' + str(acceleration) + ', deceleration = ' + str(deceleration) + '.')
    degreesToMove = stoppingRotations * 360
    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage / 100
    await motor_pair.move_for_degrees(motor_pair.PAIR_1, degreesToMove, 0, velocity=int(velocity), stop=motor.BRAKE, acceleration=acceleration, deceleration=deceleration)
    return

async def __moveForwardProporational(rotations, velocity, acceleration=500, brakeStartPercentage=0.9, correctionMultiplier=-1.5) -> None:
    print('Move Forward Proportional. Rotations = ' + str(rotations) + ', Velocity = ' + str(velocity) + ', Acceleration = ' + str(acceleration) + ', Brake = ' + str(brakeStartPercentage) + ', Correction Multiplier = ' + str(correctionMultiplier))
    motion_sensor.reset_yaw(0)
    degrees = rotations * 360
    motor.reset_relative_position(RIGHT_WHEEL_PORT, 0)
    brakeStartDistance = degrees * brakeStartPercentage
    endSpeed = LARGE_MOTOR_MAX_VELOCITY * 0.1
    while motor.relative_position(RIGHT_WHEEL_PORT) < degrees:
        error = motion_sensor.tilt_angles()[0] * -0.1
        correction = int(error * correctionMultiplier)
        deceleration = 0
        degreesTraveled = motor.relative_position(RIGHT_WHEEL_PORT)
        if degreesTraveled > brakeStartDistance:
            deceleration = min(velocity * degreesTraveled / degrees, velocity - endSpeed)
        motor_pair.move_tank(motor_pair.PAIR_1, velocity + correction - int(deceleration), velocity - correction - int(deceleration), acceleration=acceleration)
    motor_pair.stop(motor_pair.PAIR_1)
    print('Final relative position = ' + str(motor.relative_position(RIGHT_WHEEL_PORT)))
    return

async def __moveBackwardProporational(rotations, velocity, acceleration=500, brakeStartPercentage=0.9, correctionMultiplier=-3.5) -> None:
    print('Move Backward Proportional. Rotations = ' + str(rotations) + ', Velocity = ' + str(velocity) + ', Acceleration = ' + str(acceleration) + ', Brake = ' + str(brakeStartPercentage) + ', Correction Multiplier = ' + str(correctionMultiplier))
    motion_sensor.reset_yaw(0)
    degrees = rotations * 360
    motor.reset_relative_position(RIGHT_WHEEL_PORT, 0)
    brakeStartDistance = degrees * brakeStartPercentage
    endSpeed = LARGE_MOTOR_MAX_VELOCITY * 0.1
    while motor.relative_position(RIGHT_WHEEL_PORT) > degrees:
        error = motion_sensor.tilt_angles()[0] * -0.1
        correction = int(error * correctionMultiplier)
        deceleration = 0
        degreesTraveled = motor.relative_position(RIGHT_WHEEL_PORT)
        if degreesTraveled < brakeStartDistance:
            deceleration = max(velocity * degreesTraveled / degrees, velocity + endSpeed)
        motor_pair.move_tank(motor_pair.PAIR_1, velocity + correction - int(deceleration), velocity - correction - int(deceleration), acceleration=acceleration)
    motor_pair.stop(motor_pair.PAIR_1)
    print('Final relative position = ' + str(motor.relative_position(RIGHT_WHEEL_PORT)))
    return

async def _moveStraightWheelRotation(stoppingRotations, velocityPercentage, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5) -> None:
    print('MoveStraightWheelRotations. Stopping Rotations =' + str(stoppingRotations) + '. Velocity % = ' + str(velocityPercentage) + ', Acceleration = ' + str(acceleration) + ', Brake Start Value = ' + str(brakeStartValue) + ', Correction Multiplier = ' + str(correctionMultiplier) + '.')
    velocity = LARGE_MOTOR_MAX_VELOCITY * abs(velocityPercentage) / 100
    if stoppingRotations > 0:
        await __moveForwardProporational(stoppingRotations, int(velocity), acceleration, brakeStartValue, correctionMultiplier)
    else:
        await __moveBackwardProporational(stoppingRotations, int(velocity * -1), acceleration, brakeStartValue, correctionMultiplier)
    return

def __blackLineFound(leftLightSensorPort, rightLightSensorPort, bothSensorsOnLine) -> bool:
    if bothSensorsOnLine:
        return color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION and color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION
    else:
        return color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION or color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION

def __whiteLineFound(leftLightSensorPort, rightLightSensorPort, bothSensorsOnLine) -> bool:
    if bothSensorsOnLine:
        return color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION and color_sensor.reflection(rightLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION
    else:
        return color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION or color_sensor.reflection(rightLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION

async def _moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine=False, velocityPercentage=25, acceleration=500) -> int:
    print('In moveStraightUntilLine function, left light sensor port = ' + str(leftLightSensorPort) + ', right light sensor port = ' + str(rightLightSensorPort) + ', line color = ' + str(lineColor) + ', velocityPercentage = ' + str(velocityPercentage) + ', acceleration = ' + str(acceleration) + '.')
    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage / 100
    motor_pair.move(motor_pair.PAIR_1, 0, velocity=int(velocity), acceleration=acceleration)
    triggeredSensorPort = -1
    if lineColor == color.BLACK:
        await runloop.until(lambda: __blackLineFound(leftLightSensorPort, rightLightSensorPort, bothSensorsOnLine))
        if color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION:
            triggeredSensorPort = leftLightSensorPort
        else:
            triggeredSensorPort = rightLightSensorPort
    elif lineColor == color.WHITE:
        await runloop.until(lambda: __whiteLineFound(leftLightSensorPort, rightLightSensorPort, bothSensorsOnLine))
        if color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION:
            triggeredSensorPort = leftLightSensorPort
        else:
            triggeredSensorPort = rightLightSensorPort
    else:
        print('Line color of ' + str(lineColor) + ' is invalid.')
    motor_pair.stop(motor_pair.PAIR_1)
    print('Triggered Sensor Port = ', triggeredSensorPort)
    print('Left light sensor reflection = ' + str(color_sensor.reflection(leftLightSensorPort)))
    print('Right light sensor reflection = ' + str(color_sensor.reflection(rightLightSensorPort)))
    return triggeredSensorPort

async def _getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage=25, acceleration=500) -> None:
    print('In getSecondLightSensorOnLine function, left light sensor port = ' + str(leftLightSensorPort) + ', right light sensor port = ' + str(rightLightSensorPort) + ', line color = ' + str(lineColor) + ', velocityPercentage = ' + str(velocityPercentage) + ', acceleration = ' + str(acceleration) + '.')
    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage / 100
    if lineColor == color.BLACK:
        if color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION:
            print('Before movement, left light sensor on black line = ', color_sensor.reflection(leftLightSensorPort))
            motor_pair.move_tank(motor_pair.PAIR_1, 0, int(velocity), acceleration=acceleration)
            await runloop.until(lambda: color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION)
        else:
            print('Before movement, left light sensor NOT on black = ', color_sensor.reflection(leftLightSensorPort))
            motor_pair.move_tank(motor_pair.PAIR_1, int(velocity), 0, acceleration=acceleration)
            await runloop.until(lambda: color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION)
    elif lineColor == color.WHITE:
        if color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION:
            print('Before movement, left light sensor on white line = ', color_sensor.reflection(leftLightSensorPort))
            motor_pair.move_tank(motor_pair.PAIR_1, 0, int(velocity), acceleration=acceleration)
            await runloop.until(lambda: color_sensor.reflection(rightLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION)
        else:
            print('Before movement, left light sensor NOT on white line = ', color_sensor.reflection(leftLightSensorPort))
            motor_pair.move_tank(motor_pair.PAIR_1, int(velocity), 0, acceleration=acceleration)
            await runloop.until(lambda: color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION)
    else:
        print('Line color of ' + str(lineColor) + ' is invalid.')
    motor_pair.stop(motor_pair.PAIR_1)
    print('Left light sensor reflection = ' + str(color_sensor.reflection(leftLightSensorPort)))
    print('Right light sensor reflection = ' + str(color_sensor.reflection(rightLightSensorPort)))
    return

async def _squareUpOnBlackLine(leftLightSensorPort, rightLightSensorPort, leftMoveFirst=True, velocityPercentage=10, acceleration=500) -> None:
    print('In squareUpOnBlackLine function, left light sensor port = ' + str(leftLightSensorPort) + ', right light sensor port = ' + str(rightLightSensorPort) + ', leftMoveFirst = ' + str(leftMoveFirst) + ', velocityPercentage = ' + str(velocityPercentage) + ', acceleration = ' + str(acceleration) + '.')
    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage / 100
    if leftMoveFirst:
        await _getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.WHITE, -1 * velocityPercentage)
        time.sleep(0.1)
        await _getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.WHITE, -1 * velocityPercentage)
        time.sleep(0.1)
        await _getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.BLACK, velocityPercentage)
        time.sleep(0.1)
        await _getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.BLACK, velocityPercentage)
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, 0, int(-1 * velocity), acceleration=acceleration)
        await runloop.until(lambda: color_sensor.reflection(rightLightSensorPort) > BLACK_LINE_LIGHT_REFLECTION)
        motor_pair.stop(motor_pair.PAIR_1)
        time.sleep(0.1)
        await _getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.WHITE, -1 * velocityPercentage)
        time.sleep(0.1)
        motor_pair.move_tank(motor_pair.PAIR_1, 0, int(velocity), acceleration=acceleration)
        await runloop.until(lambda: color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION)
        motor_pair.stop(motor_pair.PAIR_1)
        time.sleep(0.1)
        await _getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, color.BLACK, velocityPercentage)
    return


def __velocity(velocityPercentage):
    return int(LARGE_MOTOR_MAX_VELOCITY * velocityPercentage / 100)


async def moveBackward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000):
    await _moveForward(-1 * rotations, velocityPercentage, acceleration, deceleration)
    return


async def moveForward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000):
    await _moveForward(rotations, velocityPercentage, acceleration, deceleration)
    return


async def displayMessage(messageToDisplay):
    light_matrix.write(str(messageToDisplay))
    return


async def pivotTurnRight(degreesToTurn, velocityPercentage=25):
    await _pivotTurn(degreesToTurn, __velocity(velocityPercentage))
    return


async def pivotTurnLeft(degreesToTurn, velocityPercentage=25):
    await _pivotTurn(-1 * degreesToTurn, __velocity(velocityPercentage))
    return


async def spinTurnRight(degreesToTurn, velocityPercentage=25):
    await _spinTurn(degreesToTurn, __velocity(velocityPercentage))
    return


async def spinTurnLeft(degreesToTurn, velocityPercentage=25):
    await _spinTurn(-1 * degreesToTurn, __velocity(velocityPercentage))
    return


async def proportionalPivotTurnRight(degreesToTurn, velocityPercentage=40, timeout=2.0):
    await _proportionalPivotTurn(degreesToTurn, velocityPercentage, timeout)
    return


async def proportionalPivotTurnLeft(degreesToTurn, velocityPercentage=40, timeout=2.0):
    await _proportionalPivotTurn(-1 * degreesToTurn, velocityPercentage, timeout)
    return


async def proportionalSpinTurnRight(degreesToTurn, velocityPercentage=30, timeout=2.0):
    await _proportionalSpinTurn(degreesToTurn, velocityPercentage, timeout)
    return


async def proportionalSpinTurnLeft(degreesToTurn, velocityPercentage=30, timeout=2.0):
    await _proportionalSpinTurn(-1 * degreesToTurn, velocityPercentage, timeout)
    return


async def moveForwardGyro(stoppingRotations, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5):
    await _moveStraightWheelRotation(stoppingRotations, velocityPercentage, acceleration, brakeStartValue, correctionMultiplier)
    return


async def moveBackwardGyro(stoppingRotations, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5):
    await _moveStraightWheelRotation(-1 * stoppingRotations, velocityPercentage, acceleration, brakeStartValue, correctionMultiplier)
    return


async def moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine=False, velocityPercentage=25, acceleration=500):
    return await _moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine, velocityPercentage, acceleration)


async def getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage=25, acceleration=500):
    await _getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage, acceleration)
    return


async def squareUpOnBlackLine(leftLightSensorPort, rightLightSensorPort, leftMoveFirst=True, velocityPercentage=10, acceleration=500):
    await _squareUpOnBlackLine(leftLightSensorPort, rightLightSensorPort, leftMoveFirst, velocityPercentage, acceleration)
    return


def resetEverything():
    motion_sensor.reset_yaw(0)
    motor.reset_relative_position(LEFT_WHEEL_PORT, 0)
    motor.reset_relative_position(RIGHT_WHEEL_PORT, 0)
    print("resetEverything: Complete")
    return


def initializeRobot(name: str, mainPortLeft=LEFT_WHEEL_PORT, mainPortRight=RIGHT_WHEEL_PORT):
    motor_pair.pair(motor_pair.PAIR_1, mainPortLeft, mainPortRight)
    print("initializeRobot: Complete")
    return {"name": name, "mainPortLeft": mainPortLeft, "mainPortRight": mainPortRight}
