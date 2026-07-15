# Manifest: Create `Combined.py` from Library + Wrapper

Use this manifest when rebuilding the end-user `Combined.py` from a professional library file such as `rockstar_lib.py` and an end-user wrapper file such as `rockstar_wrapper.py`.

## Goal

Create a fresh `Combined.py` by copying the library and wrapper logic into one file, while preserving the library behavior and exposing the wrapper's simple end-user API.

The current wrapper API is mostly asynchronous. Preserve that style: public wrapper functions that are currently `async def` should remain `async def` and should use `await` when calling copied library functions. Public wrapper functions that are currently synchronous, such as `initializeRobot(...)` and `resetEverything()`, should remain synchronous.

## Required Inputs

- Existing `Combined.py` may be ignored or discarded.
- `rockstar_lib.py` is the professional source library and should not be modified directly.
- `rockstar_wrapper.py` contains the desired end-user public API and should not be modified directly.
- No `RobotConfig` class is required for the current wrapper style.
- Motor ports are configured through `initializeRobot(name, mainPortLeft=LEFT_WHEEL_PORT, mainPortRight=RIGHT_WHEEL_PORT)`.

## Build Rules

1. Start from the library imports, constants, helper functions, and core async functions.
2. Use the combined import set needed by both files, but remove `import rockstar_lib as RL` because the library logic is copied directly into `Combined.py`.
3. Keep library constants public and unchanged:
   - `LARGE_MOTOR_MAX_VELOCITY`
   - `BLACK_LINE_LIGHT_REFLECTION`
   - `WHITE_LINE_LIGHT_REFLECTION`
   - `LEFT_WHEEL_PORT`
   - `RIGHT_WHEEL_PORT`
4. Rename copied library public functions with a leading underscore to avoid collisions with wrapper functions.
   - `pivotTurn(...)` becomes `_pivotTurn(...)`.
   - `spinTurn(...)` becomes `_spinTurn(...)`.
   - `proportionalPivotTurn(...)` becomes `_proportionalPivotTurn(...)`.
   - `proportionalSpinTurn(...)` becomes `_proportionalSpinTurn(...)`.
   - `moveForward(...)` becomes `_moveForward(...)`.
   - `moveStraightWheelRotation(...)` becomes `_moveStraightWheelRotation(...)`.
   - `moveStraightUntilLine(...)` becomes `_moveStraightUntilLine(...)`.
   - `getSecondLightSensorOnLine(...)` becomes `_getSecondLightSensorOnLine(...)`.
   - `squareUpOnBlackLine(...)` becomes `_squareUpOnBlackLine(...)`.
5. Keep internal helper functions private-style, such as `__turnCompleted(...)`, `__moveForwardProporational(...)`, `__moveBackwardProporational(...)`, `__blackLineFound(...)`, and `__whiteLineFound(...)`.
6. After renaming library functions, update any internal library references to renamed functions.
   - Inside copied `_squareUpOnBlackLine(...)`, calls to `getSecondLightSensorOnLine(...)` must become `_getSecondLightSensorOnLine(...)`.
7. Preserve the public wrapper function names and signatures from `rockstar_wrapper.py`:
   - `moveBackward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000)`
   - `moveForward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000)`
   - `displayMessage(messageToDisplay)`
   - `pivotTurnRight(degreesToTurn, velocityPercentage=25)`
   - `pivotTurnLeft(degreesToTurn, velocityPercentage=25)`
   - `spinTurnRight(degreesToTurn, velocityPercentage=25)`
   - `spinTurnLeft(degreesToTurn, velocityPercentage=25)`
   - `proportionalPivotTurnRight(degreesToTurn, velocityPercentage=40, timeout=2.0)`
   - `proportionalPivotTurnLeft(degreesToTurn, velocityPercentage=40, timeout=2.0)`
   - `proportionalSpinTurnRight(degreesToTurn, velocityPercentage=30, timeout=2.0)`
   - `proportionalSpinTurnLeft(degreesToTurn, velocityPercentage=30, timeout=2.0)`
   - `moveForwardGyro(stoppingRotations, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5)`
   - `moveBackwardGyro(stoppingRotations, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5)`
   - `moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine=False, velocityPercentage=25, acceleration=500)`
   - `getSecondLightSensorOnLine(leftLightSensorPort, rightLightSensorPort, lineColor, velocityPercentage=25, acceleration=500)`
   - `squareUpOnBlackLine(leftLightSensorPort, rightLightSensorPort, leftMoveFirst=True, velocityPercentage=10, acceleration=500)`
   - `resetEverything()`
   - `initializeRobot(name: str, mainPortLeft=LEFT_WHEEL_PORT, mainPortRight=RIGHT_WHEEL_PORT)`
8. Preserve the wrapper helper `__velocity(velocityPercentage)`, but update it to use the copied constant directly instead of `RL.LARGE_MOTOR_MAX_VELOCITY`.
9. Fix wrapper-to-library references inside `Combined.py` only.
   - Replace `RL.moveForward(...)` with `_moveForward(...)`.
   - Replace `RL.pivotTurn(...)` with `_pivotTurn(...)`.
   - Replace `RL.spinTurn(...)` with `_spinTurn(...)`.
   - Replace `RL.proportionalPivotTurn(...)` with `_proportionalPivotTurn(...)`.
   - Replace `RL.proportionalSpinTurn(...)` with `_proportionalSpinTurn(...)`.
   - Replace `RL.moveStraightWheelRotation(...)` with `_moveStraightWheelRotation(...)`.
   - Replace `RL.moveStraightUntilLine(...)` with `_moveStraightUntilLine(...)`.
   - Replace `RL.getSecondLightSensorOnLine(...)` with `_getSecondLightSensorOnLine(...)`.
   - Replace `RL.squareUpOnBlackLine(...)` with `_squareUpOnBlackLine(...)`.
   - Replace `RL.LEFT_WHEEL_PORT` with `LEFT_WHEEL_PORT`.
   - Replace `RL.RIGHT_WHEEL_PORT` with `RIGHT_WHEEL_PORT`.
10. Keep public async wrappers asynchronous and call copied async library functions with `await`. Do not wrap public async wrappers in `runloop.run(...)`.
11. Keep `initializeRobot(...)` as the public setup function that pairs the main motors and returns a simple dictionary containing `name`, `mainPortLeft`, and `mainPortRight`.
12. Keep `resetEverything()` as a public synchronous helper that resets yaw and wheel relative positions.
13. Add only minimal comments: no more than one line comment per function, and remove unnecessary existing comments.
14. Do not change behavior beyond the required compatibility fixes.
15. Do not modify the original `rockstar_lib.py` or `rockstar_wrapper.py` files.

## Compatibility Pattern

Use this pattern when adapting wrapper calls from `rockstar_wrapper.py` into `Combined.py`.

```python
def __velocity(velocityPercentage):
    return int(LARGE_MOTOR_MAX_VELOCITY * velocityPercentage / 100)
```

```python
async def moveBackward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000):
    await _moveForward(-1 * rotations, velocityPercentage, acceleration, deceleration)
    return
```

```python
async def moveForward(rotations, velocityPercentage=25, acceleration=500, deceleration=1000):
    await _moveForward(rotations, velocityPercentage, acceleration, deceleration)
    return
```

```python
async def pivotTurnRight(degreesToTurn, velocityPercentage=25):
    await _pivotTurn(degreesToTurn, __velocity(velocityPercentage))
    return
```

```python
async def pivotTurnLeft(degreesToTurn, velocityPercentage=25):
    await _pivotTurn(-1 * degreesToTurn, __velocity(velocityPercentage))
    return
```

```python
async def moveForwardGyro(stoppingRotations, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5):
    await _moveStraightWheelRotation(stoppingRotations, velocityPercentage, acceleration, brakeStartValue, correctionMultiplier)
    return
```

```python
async def moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine=False, velocityPercentage=25, acceleration=500):
    return await _moveStraightUntilLine(leftLightSensorPort, rightLightSensorPort, lineColor, bothSensorsOnLine, velocityPercentage, acceleration)
```

```python
def resetEverything():
    motion_sensor.reset_yaw(0); motor.reset_relative_position(LEFT_WHEEL_PORT, 0); motor.reset_relative_position(RIGHT_WHEEL_PORT, 0)
    print("resetEverything: Complete")
    return
```

```python
def initializeRobot(name: str, mainPortLeft=LEFT_WHEEL_PORT, mainPortRight=RIGHT_WHEEL_PORT):
    motor_pair.pair(motor_pair.PAIR_1, mainPortLeft, mainPortRight)
    print("initializeRobot: Complete")
    return {"name": name, "mainPortLeft": mainPortLeft, "mainPortRight": mainPortRight}
```

## End-User Run Pattern

Because the public movement wrappers are asynchronous, user code should call them from an async `main()` and start that main function with `runloop.run(...)`.

```python
async def main():
    initializeRobot("Robot")
    await moveForward(2)
    await pivotTurnRight(90)

runloop.run(main())
```

## Output

Return the full replacement code for `Combined.py` in the chat, or save it as `Combined.py` if file output is requested.
