import sys, os

libraryFile = 'rockstar_lib.py'
classesFile = "rockstar_classes.py"

libCode: str = """
from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time

LARGE_MOTOR_MAX_VELOCITY = 1050
LEFT_WHEEL_PORT = port.A
RIGHT_WHEEL_PORT = port.E

#Returns true if the gyro yaw angle has reached the degreesToTurn value indicating that a turn has been completed.
def __turnCompleted(degreesToTurn):
    #multiplying by -0.1 makes yaw angle match values in hub
    return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degreesToTurn)


#Completes a pivot turn up to 179 degrees.
#Input parameters:degreesToTurn = positive value if turning to right and negative if turning to left
#                velocity = In deg/sec; Large motor range = -1050 to 1050
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
    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ",motion_sensor.tilt_angles()[0] * -0.1)

    return


#Complete a spin turn and slow down as the turn completes to ensure accuracy.
#Input parameters: degreesToTurn = positive value if turning to right and negative if turning to left (-180 to 180)
#                velocityPercentage (optional) = how fast to complete the turn in percentage (1 to 100)
#                timeout (optional) = maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached.
async def proportionalSpinTurn(degreesToTurn, velocityPercentage = 30, timeout = 2):
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

    print("Time out!")
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return


#Complete a pivot turn and slow down as the turn completes to ensure accuracy.
#Input parameters: degreesToTurn = positive value if turning to right and negative if turning to left (-180 to 180)
#                velocityPercentage (optional) = how fast to complete the turn in percentage (1 to 100)
#                timeout (optional) = maximum number of seconds to allow turn to complete. If turn doesn't complete in this time, stop the turn when timeout is reached.
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

        turnPower = turnError * velocityPercentage/100 * LARGE_MOTOR_MAX_VELOCITY/40#pivot turns are slower so take a larger percentage of the max velocity

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
            deceleration = max(velocity * degreesTraveled/degrees, velocity + endSpeed)#deceleration is negative when moving backwards
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
async def moveStraightWheelRotation(stoppingRotations, velocityPercentage, brakeStartValue = 0.9):
    print("MoveStraightWheelRotations. Stopping Rotations =" + str(stoppingRotations) + ". Velocity % = " + str(velocityPercentage))
    velocity = LARGE_MOTOR_MAX_VELOCITY * abs(velocityPercentage)/100#negative values for velocity are not allowed so take absolute value

    if(stoppingRotations > 0):
        await __moveForwardProporational(stoppingRotations, int(velocity), brakeStartValue)
    else:
        await __moveBackwardProporational(stoppingRotations, int(velocity * -1), brakeStartValue)
"""


classesCode: str = """
class RobotConfig:
    LARGE_MOTOR_MAX_VELOCITY = 1050
    MEDIUM_MOTOR_MAX_VELOCITY = 1110

    DEFAULT_VELOCITY_PERCENT = 25 #percentage
    DEFAULT_TIMEOUT_SEC = 2 #seconds

    def __init__(
        self,
        name: str,
        mainPortLeft,
        mainPortRight,
        mainMotorVelocity: int = LARGE_MOTOR_MAX_VELOCITY * DEFAULT_VELOCITY_PERCENT/100,
        attachMotorVelocity: int = MEDIUM_MOTOR_MAX_VELOCITY * DEFAULT_VELOCITY_PERCENT/100,
        timeout: int = DEFAULT_TIMEOUT_SEC,
    ):
        self.name = name

        self.changeMainPorts(mainPortLeft, mainPortRight)
        self.mainMotorVelocity = mainMotorVelocity
        self.changeMainMotorVelocity(mainMotorVelocity)
        self.attachMotorVelocity = attachMotorVelocity
        self.changeAttachMotorVelocity(attachMotorVelocity)
        self.changeTimeout(timeout)

        self.showMyRobotConfig()

        return

    def showMyRobotConfig(self) -> None:
        print("Motor Config for: ", self.name)

        print("mainPortLeft: ", self.mainPortLeft)
        print("mainPortRight: ", self.mainPortRight)
        print("mainMotorVelocity: ", self.mainMotorVelocity)
        print("attachMotorVelocity: ", self.attachMotorVelocity)
        print("timeout: ", self.timeout)

        return

    def changeMainPorts(self, portLeft, portRight) -> None:
        self.mainPortLeft = portLeft
        self.mainPortRight = portRight
        print("changeMainPorts: ports changed to: ", portLeft, ", ", portRight)
        return

    def changeMainMotorVelocity(self, velocityPercent: int) -> None:
        if (10 <= velocityPercent <= 90):
            self.mainMotorVelocity = self.LARGE_MOTOR_MAX_VELOCITY * velocityPercent/100
            print("changeMainMotorVelocity: velocity updated to ", velocityPercent, "%")
        else:
            print("changeMainMotorVelocity: velocityPercent should be between 10 and 90\\nLeft Unchanged")
        return
    
    def getMainMotorVelocity(self) -> int:
        return self.mainMotorVelocity

    def changeAttachMotorVelocity(self, velocityPercent: int) -> None:
        if (10 <= velocityPercent <= 90):
            self.attachMotorVelocity = self.MEDIUM_MOTOR_MAX_VELOCITY * velocityPercent/100
            print("setAttachMotorVelocity: velocity updated to ", velocityPercent, "%")
        else:
            print("setAttachMotorVelocity: velocityPercent should be between 10 and 90\\nLeft Unchanged")
        return

    def getAttachMotorVelocity(self) -> int:
        return self.attachMotorVelocity

    def changeTimeout(self, timeout: int) -> None:
        self.timeout = timeout
        print("changeTimeout: timeout updated to ", timeout, " seconds")

    def getTimeout(self) -> int:
        return self.timeout
"""

def exportLibrary():
    global libCode
    global libraryFile
    global classesFile

    deleteLibrary()

    libFile = open(libraryFile, 'w+')
    libFile.write(libCode)
    libFile.close()
    print("Export of library complete.")

    classesConfigFile = open(classesFile, 'w+')
    classesConfigFile.write(classesCode)
    classesConfigFile.close()
    print("Export of classes complete.")


#TODO: add error handling for file open/close issues
def readLibrary():
    #libFile = open(libraryFile, 'r')
    #contents = libFile.read()
    #print(contents)
    #libFile.close()

    print("\n\n")

    classesConfigFile = open(classesFile, 'r')
    contents = classesConfigFile.read()
    print(contents)
    classesConfigFile.close()


def deleteLibrary():
    try:
        os.remove(libraryFile) #remove any existing custom library with the same name
    except:
        pass

    try:
        os.remove(classesFile) #remove any existing classes file with the same name
    except:
        pass


def readDirectory():
    print("Directory contents: ")
    dirContents = os.listdir('/flash')
    print(dirContents)


os.chdir('/flash') #change directory to root
#readDirectory()
#deleteLibrary()
#readDirectory()
exportLibrary()
readLibrary()
readDirectory()
sys.exit(0)