# Combined.py End-User API Manifest

Use this manifest when writing end-user robot programs that import and use `Combined.py`.

## IMPORT

```python
from hub import port
import Combined as RL
```

## BASIC SETUP

Create and initialize your robot before calling movement functions.

```python
myRobot = RL.initializeRobot(
    name="Pez",
    mainPortLeft=port.A,
    mainPortRight=port.E,
)
```

`myRobot` stores the robot configuration, including motor ports, motor velocity, attachment motor velocity, and timeout.

## INITIALIZE

```python
myRobot = RL.initializeRobot(name, mainPortLeft, mainPortRight)
```

Example:

```python
myRobot = RL.initializeRobot(
    name="Pez",
    mainPortLeft=port.A,
    mainPortRight=port.E,
)
```

## RESET

```python
RL.resetEverything(myRobot)
```

Example:

```python
RL.resetEverything(myRobot)
```

## SHOW CONFIGURATION

```python
myRobot.showMyRobotConfig()
```

Example:

```python
myRobot.showMyRobotConfig()
```

## DISPLAY

```python
RL.displayMessage(myRobot, messageToDisplay)
```

Example:

```python
RL.displayMessage(myRobot, "Go")
```

## MOVEMENT

Move forward or backward without gyro correction.

```python
RL.moveForward(myRobot, rotations)
RL.moveBackward(myRobot, rotations)
```

Examples:

```python
RL.moveForward(myRobot, 1)
RL.moveBackward(myRobot, 1)
```

Move forward or backward with gyro correction.

```python
RL.moveForwardGyro(myRobot, stoppingRotations)
RL.moveBackwardGyro(myRobot, stoppingRotations)
```

Examples:

```python
RL.moveForwardGyro(myRobot, 1)
RL.moveBackwardGyro(myRobot, 1)
```

## TURN

Pivot turns move one wheel while the other wheel stays stopped.

```python
RL.pivotTurnRight(myRobot, degreesToTurn)
RL.pivotTurnLeft(myRobot, degreesToTurn)
```

Examples:

```python
RL.pivotTurnRight(myRobot, 90)
RL.pivotTurnLeft(myRobot, 90)
```

Spin turns move both wheels in opposite directions.

```python
RL.spinTurnRight(myRobot, degreesToTurn)
RL.spinTurnLeft(myRobot, degreesToTurn)
```

Examples:

```python
RL.spinTurnRight(myRobot, 90)
RL.spinTurnLeft(myRobot, 90)
```

Proportional spin turns slow down near the target angle for better accuracy.

```python
RL.proportionalSpinTurnRight(myRobot, degreesToTurn)
RL.proportionalSpinTurnLeft(myRobot, degreesToTurn)
```

Examples:

```python
RL.proportionalSpinTurnRight(myRobot, 90)
RL.proportionalSpinTurnLeft(myRobot, 90)
```

## LINE DETECTION

Move straight until either light sensor detects a black line.

```python
triggeredSensorPort = RL.moveStraightUntilBlackLine(
    myRobot,
    leftLightSensorPort,
    rightLightSensorPort,
)
```

Example:

```python
triggeredSensorPort = RL.moveStraightUntilBlackLine(
    myRobot,
    port.B,
    port.D,
)
```

Move straight until either light sensor detects a white line.

```python
triggeredSensorPort = RL.moveStraightUntilWhiteLine(
    myRobot,
    leftLightSensorPort,
    rightLightSensorPort,
)
```

Example:

```python
triggeredSensorPort = RL.moveStraightUntilWhiteLine(
    myRobot,
    port.B,
    port.D,
)
```

## CHANGE SETTINGS

Change the main drive motor speed.

```python
myRobot.changeMainMotorVelocity(velocityPercent)
```

Example:

```python
myRobot.changeMainMotorVelocity(40)
```

Change the attachment motor speed.

```python
myRobot.changeAttachMotorVelocity(velocityPercent)
```

Example:

```python
myRobot.changeAttachMotorVelocity(30)
```

Change the turn timeout used by proportional turn functions.

```python
myRobot.changeTimeout(timeout)
```

Example:

```python
myRobot.changeTimeout(3)
```

Change the main drive motor ports.

```python
myRobot.changeMainPorts(portLeft, portRight)
```

Example:

```python
myRobot.changeMainPorts(port.A, port.E)
```

## COMPLETE STARTER PROGRAM

```python
from hub import port
import Combined as RL


def main():
    myRobot = RL.initializeRobot(
        name="Pez",
        mainPortLeft=port.A,
        mainPortRight=port.E,
    )

    myRobot.showMyRobotConfig()

    RL.displayMessage(myRobot, "Go")

    RL.moveForward(myRobot, 1)
    RL.pivotTurnRight(myRobot, 90)
    RL.moveBackward(myRobot, 1)


main()
```

## IMPORTANT NOTES

The end-user wrapper functions in `Combined.py` are synchronous.

Do not use `await` when calling these functions:

```python
RL.moveForward(myRobot, 1)
RL.pivotTurnRight(myRobot, 90)
RL.moveForwardGyro(myRobot, 1)
```

Do not wrap the whole user program in `runloop.run(main())`.

Use normal function calls from a normal `main()` function:

```python
def main():
    myRobot = RL.initializeRobot(
        name="Pez",
        mainPortLeft=port.A,
        mainPortRight=port.E,
    )

    RL.moveForward(myRobot, 1)


main()
```
