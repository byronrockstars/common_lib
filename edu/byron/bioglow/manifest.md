# Combined.py End-User API Manifest

Use this manifest when writing end-user robot programs that import and use `Combined.py`.

## IMPORT

```python
from hub import port
import runloop
import color
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

`myRobot` stores the robot name and main motor ports returned by the wrapper.

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
RL.resetEverything()
```

Example:

```python
RL.resetEverything()
```

## SHOW CONFIGURATION

The updated wrapper returns a simple robot configuration dictionary from `initializeRobot`.

```python
print(myRobot)
```

Example:

```python
print(myRobot)
```

## DISPLAY

```python
await RL.displayMessage(messageToDisplay)
```

Example:

```python
await RL.displayMessage("Go")
```

## MOVEMENT

Move forward or backward without gyro correction.

```python
await RL.moveForward(rotations)
await RL.moveBackward(rotations)
```

Examples:

```python
await RL.moveForward(1)
await RL.moveBackward(1)
```

Optional movement settings can be supplied directly to the movement call.

```python
await RL.moveForward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000)
await RL.moveBackward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000)
```

Move forward or backward with gyro correction.

```python
await RL.moveForwardGyro(stoppingRotations)
await RL.moveBackwardGyro(stoppingRotations)
```

Examples:

```python
await RL.moveForwardGyro(1)
await RL.moveBackwardGyro(1)
```

Optional gyro movement settings can be supplied directly to the gyro movement call.

```python
await RL.moveForwardGyro(stoppingRotations, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5)
await RL.moveBackwardGyro(stoppingRotations, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5)
```

## TURN

Pivot turns move one wheel while the other wheel stays stopped.

```python
await RL.pivotTurnRight(degreesToTurn)
await RL.pivotTurnLeft(degreesToTurn)
```

Examples:

```python
await RL.pivotTurnRight(90)
await RL.pivotTurnLeft(90)
```

Spin turns move both wheels in opposite directions.

```python
await RL.spinTurnRight(degreesToTurn)
await RL.spinTurnLeft(degreesToTurn)
```

Examples:

```python
await RL.spinTurnRight(90)
await RL.spinTurnLeft(90)
```

Proportional pivot turns slow down near the target angle for better accuracy.

```python
await RL.proportionalPivotTurnRight(degreesToTurn)
await RL.proportionalPivotTurnLeft(degreesToTurn)
```

Examples:

```python
await RL.proportionalPivotTurnRight(90)
await RL.proportionalPivotTurnLeft(90)
```

Proportional spin turns slow down near the target angle for better accuracy.

```python
await RL.proportionalSpinTurnRight(degreesToTurn)
await RL.proportionalSpinTurnLeft(degreesToTurn)
```

Examples:

```python
await RL.proportionalSpinTurnRight(90)
await RL.proportionalSpinTurnLeft(90)
```

Optional turn settings can be supplied directly to the turn call.

```python
await RL.pivotTurnRight(degreesToTurn, velocityPercentage=25)
await RL.spinTurnRight(degreesToTurn, velocityPercentage=25)
await RL.proportionalPivotTurnRight(degreesToTurn, velocityPercentage=40, timeout=2.0)
await RL.proportionalSpinTurnRight(degreesToTurn, velocityPercentage=30, timeout=2.0)
```

## LINE DETECTION

Move straight until either light sensor detects the requested line color.

```python
triggeredSensorPort = await RL.moveStraightUntilLine(
    leftLightSensorPort,
    rightLightSensorPort,
    lineColor,
)
```

Example:

```python
triggeredSensorPort = await RL.moveStraightUntilLine(
    port.B,
    port.D,
    color.BLACK,
)
```

Move straight until both light sensors detect the requested line color.

```python
triggeredSensorPort = await RL.moveStraightUntilLine(
    leftLightSensorPort,
    rightLightSensorPort,
    lineColor,
    bothSensorsOnLine=True,
)
```

Example:

```python
triggeredSensorPort = await RL.moveStraightUntilLine(
    port.B,
    port.D,
    color.WHITE,
    bothSensorsOnLine=True,
)
```

After one light sensor is already on a line, move until the second light sensor reaches the same line color.

```python
await RL.getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, lineColor)
```

Example:

```python
await RL.getSecondLightSensorOnLine(port.B, port.D, color.BLACK)
```

Square up on a black line using two light sensors.

```python
await RL.squareUpOnBlackLine(leftLightSensorPort, rightLightSensorPort)
```

Example:

```python
await RL.squareUpOnBlackLine(port.B, port.D)
```

## CHANGE SETTINGS

Change the main drive motor speed by passing `velocityPercentage` to movement and turn functions.

```python
await RL.moveForward(rotations, velocityPercentage=40)
await RL.pivotTurnRight(degreesToTurn, velocityPercentage=40)
```

Example:

```python
await RL.moveForward(1, velocityPercentage=40)
```

Change acceleration or deceleration by passing optional movement parameters.

```python
await RL.moveForward(rotations, acceleration=500, deceleration=1000)
```

Example:

```python
await RL.moveForward(1, acceleration=500, deceleration=1000)
```

Change the proportional turn timeout by passing `timeout` to proportional turn functions.

```python
await RL.proportionalSpinTurnRight(degreesToTurn, timeout=2.0)
```

Example:

```python
await RL.proportionalSpinTurnRight(90, timeout=3)
```

Change the main drive motor ports when initializing the robot.

```python
myRobot = RL.initializeRobot(name, mainPortLeft, mainPortRight)
```

Example:

```python
myRobot = RL.initializeRobot("Pez", port.A, port.E)
```

## COMPLETE STARTER PROGRAM

```python
from hub import port
import runloop
import Combined as RL


async def main():
    myRobot = RL.initializeRobot(
        name="Pez",
        mainPortLeft=port.A,
        mainPortRight=port.E,
    )

    print(myRobot)

    await RL.displayMessage("Go")

    await RL.moveForward(1)
    await RL.pivotTurnRight(90)
    await RL.moveBackward(1)


runloop.run(main())
```

## IMPORTANT NOTES

The end-user wrapper functions in `Combined.py` that control robot actions are asynchronous.

Use `await` when calling these functions from an `async` function:

```python
await RL.moveForward(1)
await RL.pivotTurnRight(90)
await RL.moveForwardGyro(1)
```

Run the whole user program with `runloop.run(main())`.

Use an async `main()` function:

```python
async def main():
    myRobot = RL.initializeRobot(
        name="Pez",
        mainPortLeft=port.A,
        mainPortRight=port.E,
    )

    await RL.moveForward(1)


runloop.run(main())
```

`initializeRobot()` and `resetEverything()` are normal functions and do not use `await`.

```python
myRobot = RL.initializeRobot("Pez", port.A, port.E)
RL.resetEverything()
```
