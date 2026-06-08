import sys, os

libraryFile = 'Combined.py'

libCode: str = """
from hub import light_matrix, motion_sensor, port, sound
import hub
import runloop, motor, motor_pair, sys, time, color_sensor, color

LARGE_MOTOR_MAX_VELOCITY = 1050
MEDIUM_MOTOR_MAX_VELOCITY = 1110

BLACK_LINE_LIGHT_REFLECTION = 50
WHITE_LINE_LIGHT_REFLECTION = 95

DEFAULT_VELOCITY_PERCENT = 25
DEFAULT_TIMEOUT_SEC = 2

LEFT_WHEEL_PORT = port.A
RIGHT_WHEEL_PORT = port.E


class RobotConfig:
    def __init__(
        self,
        name: str,
        mainPortLeft,
        mainPortRight,
        mainMotorVelocity: int = LARGE_MOTOR_MAX_VELOCITY * DEFAULT_VELOCITY_PERCENT / 100,
        attachMotorVelocity: int = MEDIUM_MOTOR_MAX_VELOCITY * DEFAULT_VELOCITY_PERCENT / 100,
        timeout: int = DEFAULT_TIMEOUT_SEC
    ):
        self.name = name
        self.mainMotorVelocity = mainMotorVelocity
        self.attachMotorVelocity = attachMotorVelocity
        self.timeout = timeout
        self.mainPortLeft = mainPortLeft
        self.mainPortRight = mainPortRight

    def showMyRobotConfig(self) -> None:
        print("Motor Config for: ", self.name)
        print("mainPortLeft: ", self.mainPortLeft)
        print("mainPortRight: ", self.mainPortRight)
        print("mainMotorVelocity: ", self.mainMotorVelocity)
        print("attachMotorVelocity: ", self.attachMotorVelocity)
        print("timeout: ", self.timeout)

    def changeMainPorts(self, portLeft, portRight) -> None:
        self.mainPortLeft = portLeft
        self.mainPortRight = portRight
        print("changeMainPorts: ports changed to: ", portLeft, ", ", portRight)

    def changeMainMotorVelocity(self, velocityPercent: int) -> None:
        if 10 <= velocityPercent <= 90:
            self.mainMotorVelocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercent / 100
            print("changeMainMotorVelocity: velocity updated to ", velocityPercent, "%")
        else:
            print("changeMainMotorVelocity: velocityPercent should be between 10 and 90")
            print("Left Unchanged")

    def getMainMotorVelocity(self) -> int:
        return self.mainMotorVelocity

    def changeAttachMotorVelocity(self, velocityPercent: int) -> None:
        if 10 <= velocityPercent <= 90:
            self.attachMotorVelocity = MEDIUM_MOTOR_MAX_VELOCITY * velocityPercent / 100
            print("changeAttachMotorVelocity: velocity updated to ", velocityPercent, "%")
        else:
            print("changeAttachMotorVelocity: velocityPercent should be between 10 and 90")
            print("Left Unchanged")

    def getAttachMotorVelocity(self) -> int:
        return self.attachMotorVelocity

    def changeTimeout(self, timeout: int) -> None:
        self.timeout = timeout
        print("changeTimeout: timeout updated to ", timeout, " seconds")

    def getTimeout(self) -> int:
        return self.timeout


def _velocityToPercent(velocity, maxVelocity) -> int:
    return int(abs(velocity) * 100 / maxVelocity)


def __turnCompleted(degreesToTurn) -> bool:
    return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degreesToTurn)


async def _pivotTurn(degreesToTurn, velocity) -> None:
    print("Pivot Turn")

    motion_sensor.reset_yaw(0)

    if degreesToTurn > 0:
        motor_pair.move_tank(motor_pair.PAIR_1, int(velocity), 0)
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, 0, int(velocity))

    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)


async def _spinTurn(degreesToTurn, velocity) -> None:
    print("Spin Turn")

    motion_sensor.reset_yaw(0)

    if degreesToTurn > 0:
        motor_pair.move_tank(motor_pair.PAIR_1, int(velocity), -1 * int(velocity))
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, -1 * int(velocity), int(velocity))

    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)


async def _proportionalPivotTurn(degreesToTurn, velocityPercentage=40, timeout=2.0) -> None:
    print("Proportional Pivot Turn. DegreesToTurn = " + str(degreesToTurn) + ". velocityPercentage = " + str(velocityPercentage) + ", timeout(seconds) = " + str(timeout))

    motion_sensor.reset_yaw(0)

    startTime = time.ticks_ms()
    print("Start time: ", startTime)

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
            print("Turn completed!")
            break

    motor_pair.stop(motor_pair.PAIR_1)

    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)


async def _proportionalSpinTurn(degreesToTurn, velocityPercentage=30, timeout=2.0) -> None:
    print("Proportional Spin Turn. DegreesToTurn = " + str(degreesToTurn) + ". velocityPercentage = " + str(velocityPercentage) + ", timeout(seconds) = " + str(timeout))

    motion_sensor.reset_yaw(0)

    startTime = time.ticks_ms()
    print("Start time: ", startTime)

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
            print("Turn completed!")
            break

    motor_pair.stop(motor_pair.PAIR_1)

    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)


async def _moveForward(stoppingRotations, velocityPercentage, acceleration=500, deceleration=1000) -> None:
    print("In moveForward function, rotations to move = " + str(stoppingRotations) + ", velocityPercentage = " + str(velocityPercentage) + ", acceleration = " + str(acceleration) + ", deceleration = " + str(deceleration) + ".")

    degreesToMove = stoppingRotations * 360
    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage / 100

    await motor_pair.move_for_degrees(
        motor_pair.PAIR_1,
        int(degreesToMove),
        0,
        velocity=int(velocity),
        stop=motor.BRAKE,
        acceleration=acceleration,
        deceleration=deceleration
    )


async def __moveForwardProporational(rotations, velocity, acceleration=500, brakeStartPercentage=0.9, correctionMultiplier=-1.5) -> None:
    print("Move Forward Proportional. Rotations = " + str(rotations) + ", Velocity = " + str(velocity) + ", Acceleration = " + str(acceleration) + ", Brake = " + str(brakeStartPercentage) + ", Correction Multiplier = " + str(correctionMultiplier))

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

        motor_pair.move_tank(
            motor_pair.PAIR_1,
            velocity + correction - int(deceleration),
            velocity - correction - int(deceleration),
            acceleration=acceleration
        )

    motor_pair.stop(motor_pair.PAIR_1)
    print("Final relative position = " + str(motor.relative_position(RIGHT_WHEEL_PORT)))


async def __moveBackwardProporational(rotations, velocity, acceleration=500, brakeStartPercentage=0.9, correctionMultiplier=-3.5) -> None:
    print("Move Backward Proportional. Rotations = " + str(rotations) + ", Velocity = " + str(velocity) + ", Acceleration = " + str(acceleration) + ", Brake = " + str(brakeStartPercentage) + ", Correction Multiplier = " + str(correctionMultiplier))

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

        motor_pair.move_tank(
            motor_pair.PAIR_1,
            velocity + correction - int(deceleration),
            velocity - correction - int(deceleration),
            acceleration=acceleration
        )

    motor_pair.stop(motor_pair.PAIR_1)
    print("Final relative position = " + str(motor.relative_position(RIGHT_WHEEL_PORT)))


async def _moveStraightWheelRotation(stoppingRotations, velocityPercentage, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5) -> None:
    print("MoveStraightWheelRotations. Stopping Rotations =" + str(stoppingRotations) + ". Velocity % = " + str(velocityPercentage) + ", Acceleration = " + str(acceleration) + ", Brake Start Value = " + str(brakeStartValue) + ", Correction Multiplier = " + str(correctionMultiplier) + ".")

    velocity = LARGE_MOTOR_MAX_VELOCITY * abs(velocityPercentage) / 100

    if stoppingRotations > 0:
        await __moveForwardProporational(stoppingRotations, int(velocity), acceleration, brakeStartValue, correctionMultiplier)
    else:
        await __moveBackwardProporational(stoppingRotations, int(velocity * -1), acceleration, brakeStartValue, correctionMultiplier)


def __blackLineFound(leftLightSensorPort, rightLightSensorPort) -> bool:
    return color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION or color_sensor.reflection(rightLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION


def __whiteLineFound(leftLightSensorPort, rightLightSensorPort) -> bool:
    return color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION or color_sensor.reflection(rightLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION


async def _moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage=25, acceleration=500) -> int:
    print("In moveStraightUntilLine function, left light sensor port = " + str(leftLightSensorPort) + ", right light sensor port = " + str(rightLightSensorPort) + ", line color = " + str(lineColor) + ", velocityPercentage = " + str(velocityPercentage) + ", acceleration = " + str(acceleration) + ".")

    velocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercentage / 100
    motor_pair.move(motor_pair.PAIR_1, 0, velocity=int(velocity), acceleration=acceleration)

    triggeredSensorPort = -1

    if lineColor == color.BLACK:
        await runloop.until(lambda: __blackLineFound(leftLightSensorPort, rightLightSensorPort))

        if color_sensor.reflection(leftLightSensorPort) < BLACK_LINE_LIGHT_REFLECTION:
            print("Left light sensor found black line. Reflection = " + str(color_sensor.reflection(leftLightSensorPort)))
            triggeredSensorPort = leftLightSensorPort
        else:
            print("Right light sensor found black line. Reflection = " + str(color_sensor.reflection(rightLightSensorPort)))
            triggeredSensorPort = rightLightSensorPort

    elif lineColor == color.WHITE:
        await runloop.until(lambda: __whiteLineFound(leftLightSensorPort, rightLightSensorPort))

        if color_sensor.reflection(leftLightSensorPort) > WHITE_LINE_LIGHT_REFLECTION:
            print("Left light sensor found white line. Reflection = " + str(color_sensor.reflection(leftLightSensorPort)))
            triggeredSensorPort = leftLightSensorPort
        else:
            print("Right light sensor found white line. Reflection = " + str(color_sensor.reflection(rightLightSensorPort)))
            triggeredSensorPort = rightLightSensorPort

    else:
        print("Line color of " + str(lineColor) + " is invalid.")

    motor_pair.stop(motor_pair.PAIR_1)
    return triggeredSensorPort


def _allSensorReset() -> None:
    motion_sensor.reset_yaw(0)


def moveBackward(myConfig: RobotConfig, rotations):
    if isinstance(rotations, (int, float)):
        runloop.run(_moveForward(
            -1 * rotations,
            _velocityToPercent(myConfig.getMainMotorVelocity(), LARGE_MOTOR_MAX_VELOCITY)
        ))
    else:
        print("moveBackward: rotations must be a number")


def moveForward(myConfig: RobotConfig, rotations):
    if isinstance(rotations, (int, float)):
        runloop.run(_moveForward(
            rotations,
            _velocityToPercent(myConfig.getMainMotorVelocity(), LARGE_MOTOR_MAX_VELOCITY)
        ))
    else:
        print("moveForward: rotations must be a number")


def displayMessage(myConfig: RobotConfig, messageToDisplay):
    light_matrix.write(str(messageToDisplay))


def pivotTurnRight(myConfig: RobotConfig, degreesToTurn):
    if isinstance(degreesToTurn, int):
        runloop.run(_pivotTurn(degreesToTurn, myConfig.getMainMotorVelocity()))
    else:
        print("pivotTurnRight: degreesToTurn must be a number")


def pivotTurnLeft(myConfig: RobotConfig, degreesToTurn):
    if isinstance(degreesToTurn, int):
        runloop.run(_pivotTurn(-1 * degreesToTurn, myConfig.getMainMotorVelocity()))
    else:
        print("pivotTurnLeft: degreesToTurn must be a number")


def spinTurnRight(myConfig: RobotConfig, degreesToTurn):
    if isinstance(degreesToTurn, int):
        runloop.run(_spinTurn(degreesToTurn, myConfig.getMainMotorVelocity()))
    else:
        print("spinTurnRight: degreesToTurn must be a number")


def spinTurnLeft(myConfig: RobotConfig, degreesToTurn):
    if isinstance(degreesToTurn, int):
        runloop.run(_spinTurn(-1 * degreesToTurn, myConfig.getMainMotorVelocity()))
    else:
        print("spinTurnLeft: degreesToTurn must be a number")


def proportionalSpinTurnLeft(myConfig: RobotConfig, degreesToTurn):
    if isinstance(degreesToTurn, int):
        runloop.run(_proportionalSpinTurn(
            -1 * degreesToTurn,
            _velocityToPercent(myConfig.getMainMotorVelocity(), LARGE_MOTOR_MAX_VELOCITY),
            myConfig.getTimeout()
        ))
    else:
        print("proportionalSpinTurnLeft: degreesToTurn must be a number")


def proportionalSpinTurnRight(myConfig: RobotConfig, degreesToTurn):
    if isinstance(degreesToTurn, int):
        runloop.run(_proportionalSpinTurn(
            degreesToTurn,
            _velocityToPercent(myConfig.getMainMotorVelocity(), LARGE_MOTOR_MAX_VELOCITY),
            myConfig.getTimeout()
        ))
    else:
        print("proportionalSpinTurnRight: degreesToTurn must be a number")


def moveForwardGyro(myConfig: RobotConfig, stoppingRotations):
    if isinstance(stoppingRotations, (int, float)):
        runloop.run(_moveStraightWheelRotation(
            stoppingRotations,
            _velocityToPercent(myConfig.getMainMotorVelocity(), LARGE_MOTOR_MAX_VELOCITY)
        ))
    else:
        print("moveForwardGyro: stoppingRotations must be a number")


def moveBackwardGyro(myConfig: RobotConfig, stoppingRotations):
    if isinstance(stoppingRotations, (int, float)):
        runloop.run(_moveStraightWheelRotation(
            -1 * stoppingRotations,
            _velocityToPercent(myConfig.getMainMotorVelocity(), LARGE_MOTOR_MAX_VELOCITY)
        ))
    else:
        print("moveBackwardGyro: stoppingRotations must be a number")


def moveStraightUntilBlackLine(myConfig: RobotConfig, leftLightSensorPort, rightLightSensorPort):
    return runloop.run(_moveStraightUntilLine(
        leftLightSensorPort,
        rightLightSensorPort,
        color.BLACK,
        _velocityToPercent(myConfig.getMainMotorVelocity(), LARGE_MOTOR_MAX_VELOCITY)
    ))


def moveStraightUntilWhiteLine(myConfig: RobotConfig, leftLightSensorPort, rightLightSensorPort):
    return runloop.run(_moveStraightUntilLine(
        leftLightSensorPort,
        rightLightSensorPort,
        color.WHITE,
        _velocityToPercent(myConfig.getMainMotorVelocity(), LARGE_MOTOR_MAX_VELOCITY)
    ))


def resetEverything(myConfig: RobotConfig):
    _allSensorReset()

    newConfig = RobotConfig(
        myConfig.name,
        mainPortLeft=myConfig.mainPortLeft,
        mainPortRight=myConfig.mainPortRight
    )

    myConfig.mainMotorVelocity = newConfig.getMainMotorVelocity()
    myConfig.attachMotorVelocity = newConfig.getAttachMotorVelocity()
    myConfig.timeout = newConfig.getTimeout()

    print("resetEverything: Complete")


def initializeRobot(
    name: str,
    mainPortLeft,
    mainPortRight
) -> RobotConfig:
    newConfig = RobotConfig(
        name=name,
        mainPortLeft=mainPortLeft,
        mainPortRight=mainPortRight
    )

    _allSensorReset()

    motor_pair.pair(
        motor_pair.PAIR_1,
        newConfig.mainPortLeft,
        newConfig.mainPortRight
    )

    print("initializeRobot: Complete")

    return newConfig
"""

def exportLibrary():
    global libCode
    global libraryFile

    deleteLibrary()

    libFile = open(libraryFile, 'w+')
    libFile.write(libCode)
    libFile.close()
    print("Export of library complete.")

#TODO: add error handling for file open/close issues
def readLibrary():
    libFile = open(libraryFile, 'r')
    contents = libFile.read()
    print(contents)
    libFile.close()

    print("\n\n")

def deleteLibrary():
    try:
        os.remove(libraryFile) #remove any existing custom library with the same name
    except:
        print("No current library to delete")
        pass


def readDirectory():
    print("Directory contents: ")
    dirContents = os.listdir('/flash')
    print(dirContents)


os.chdir('/flash') #change directory to root
readDirectory()
deleteLibrary()
readDirectory()
exportLibrary()
#readLibrary()
readDirectory()
sys.exit(0)