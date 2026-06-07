# Manifest: Create `Combined.py` from Library + Wrapper

Use this manifest when rebuilding the end-user `Combined.py` from a professional library file such as `rockstar_lib.py` and an end-user wrapper file such as `rockstar_wrapper.py`.

## Goal

Create a fresh `Combined.py` by copying the library and wrapper logic into one file, while preserving the library behavior and exposing simple end-user wrapper functions.

## Required Inputs

- Existing `Combined.py` may be ignored or discarded.
- `rockstar_lib.py` is the professional source library and should not be modified directly.
- `rockstar_wrapper.py` contains the desired end-user public API.
- Include any needed config class, such as `RobotConfig`, directly inside `Combined.py`.

## Build Rules

1. Start from the library imports, constants, helper functions, and core async functions.
2. Rename copied library functions with a leading underscore to avoid collisions with wrapper functions.
   - Example: `pivotTurn(...)` becomes `_pivotTurn(...)`.
   - Example: `moveForward(...)` becomes `_moveForward(...)`.
3. Keep internal helper functions private-style, such as `__turnCompleted(...)`.
4. Preserve the end-user wrapper function names without leading underscores.
   - Example: `moveForward(myConfig, rotations)` remains the public wrapper.
   - Example: `pivotTurnRight(myConfig, degreesToTurn)` remains public.
5. Fix wrapper-to-library argument mismatches inside `Combined.py` only.
   - Wrapper functions should accept `RobotConfig`.
   - Internal `_` library functions should receive the raw values they expect, such as rotations, degrees, velocity, velocity percentage, timeout, ports, or colors.
6. For async library functions, make the public wrapper functions async and use `await` when calling the internal `_` functions.
7. Use `RobotConfig` as the single place for user-facing configuration, including motor ports, motor velocities, and timeout.
8. Add only minimal comments: no more than one line comment per function, and remove unnecessary existing comments.
9. Do not change behavior beyond the required compatibility fixes.
10. Do not modify the original `rockstar_lib.py` or `rockstar_wrapper.py` files.

## Compatibility Pattern

Use this pattern when adapting wrapper calls:

```python
async def moveForward(myConfig: RobotConfig, rotations):
    if isinstance(rotations, (int, float)):
        await _moveForward(rotations, _velocityToPercent(myConfig.getMainMotorVelocity(), LARGE_MOTOR_MAX_VELOCITY))
    else:
        print("moveForward: rotations must be a number")
```

```python
async def pivotTurnRight(myConfig: RobotConfig, degreesToTurn):
    if isinstance(degreesToTurn, int):
        await _pivotTurn(degreesToTurn, myConfig.getMainMotorVelocity())
    else:
        print("pivotTurnRight: degreesToTurn must be a number")
```

## Output

Return the full replacement code for `Combined.py` in the chat, or save it as `Combined.py` if file output is requested.
