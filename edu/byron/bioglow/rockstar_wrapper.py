from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time, color_sensor, color
import rockstar_lib as RL


def __velocity(velocityPercentage):
    return int(RL.LARGE_MOTOR_MAX_VELOCITY * velocityPercentage / 100)


async def moveBackward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000):
    await RL.moveForward(-1 * rotations, velocityPercentage, acceleration, deceleration)
    return


async def moveForward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000):
    await RL.moveForward(rotations, velocityPercentage, acceleration, deceleration)
    return


async def displayMessage(messageToDisplay):
    light_matrix.write(str(messageToDisplay))
    return


async def pivotTurnRight(degreesToTurn, velocityPercentage=25):
    await RL.pivotTurn(degreesToTurn, __velocity(velocityPercentage))
    return


async def pivotTurnLeft(degreesToTurn, velocityPercentage=25):
    await RL.pivotTurn(-1 * degreesToTurn, __velocity(velocityPercentage))
    return


async def spinTurnRight(degreesToTurn, velocityPercentage=25):
    await RL.spinTurn(degreesToTurn, __velocity(velocityPercentage))
    return


async def spinTurnLeft(degreesToTurn, velocityPercentage=25):
    await RL.spinTurn(-1 * degreesToTurn, __velocity(velocityPercentage))
    return


async def proportionalPivotTurnRight(degreesToTurn, velocityPercentage=40, timeout=2.0):
    await RL.proportionalPivotTurn(degreesToTurn, velocityPercentage, timeout)
    return


async def proportionalPivotTurnLeft(degreesToTurn, velocityPercentage=40, timeout=2.0):
    await RL.proportionalPivotTurn(-1 * degreesToTurn, velocityPercentage, timeout)
    return


async def proportionalSpinTurnRight(degreesToTurn, velocityPercentage=30, timeout=2.0):
    await RL.proportionalSpinTurn(degreesToTurn, velocityPercentage, timeout)
    return


async def proportionalSpinTurnLeft(degreesToTurn, velocityPercentage=30, timeout=2.0):
    await RL.proportionalSpinTurn(-1 * degreesToTurn, velocityPercentage, timeout)
    return


async def moveForwardGyro(stoppingRotations, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5):
    await RL.moveStraightWheelRotation(stoppingRotations, velocityPercentage, acceleration, brakeStartValue, correctionMultiplier)
    return


async def moveBackwardGyro(stoppingRotations, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5):
    await RL.moveStraightWheelRotation(-1 * stoppingRotations, velocityPercentage, acceleration, brakeStartValue, correctionMultiplier)
    return


async def moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine=False, velocityPercentage=25, acceleration=500):
    return await RL.moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine, velocityPercentage, acceleration)


async def getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage=25, acceleration=500):
    await RL.getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage, acceleration)
    return


async def squareUpOnBlackLine(leftLightSensorPort, rightLightSensorPort, leftMoveFirst=True, velocityPercentage=10, acceleration=500):
    await RL.squareUpOnBlackLine(leftLightSensorPort, rightLightSensorPort, leftMoveFirst, velocityPercentage, acceleration)
    return


def resetEverything():
    motion_sensor.reset_yaw(0); motor.reset_relative_position(RL.LEFT_WHEEL_PORT, 0); motor.reset_relative_position(RL.RIGHT_WHEEL_PORT, 0)
    print("resetEverything: Complete")
    return


def initializeRobot(name: str, mainPortLeft=RL.LEFT_WHEEL_PORT, mainPortRight=RL.RIGHT_WHEEL_PORT):
    motor_pair.pair(motor_pair.PAIR_1, mainPortLeft, mainPortRight)
    print("initializeRobot: Complete")
    return {"name": name, "mainPortLeft": mainPortLeft, "mainPortRight": mainPortRight}
