from hub import port
import runloop
import color
import motor
import Combined as RW
import time


async def _runMission7Old() -> None:
    #Mission 7 (Humongous Fungus) -> Uses move forward until black line (no gyro)
    await RW.moveForwardGyro(stoppingRotations=3.5, velocityPercentage=30)
    await RW.moveStraightUntilLine(leftLightSensorPort=port.E, rightLightSensorPort=port.F, lineColor=color.BLACK, velocityPercentage=30)
    await RW.moveForwardGyro(0.03, velocityPercentage=5)
    await RW.moveBackwardGyro(stoppingRotations=0.6, velocityPercentage=10)
    await RW.proportionalSpinTurnRight(degreesToTurn=15, velocityPercentage=20)
    await RW.proportionalSpinTurnLeft(degreesToTurn=12, velocityPercentage=20)

    return


async def _runMission7Alt() -> None:
    #Mission 7 (Humongous Fungus)
    await RW.moveForwardGyro(stoppingRotations=4.02, velocityPercentage=30)
    await RW.moveBackwardGyro(stoppingRotations=0.7, velocityPercentage=10)
    await RW.proportionalSpinTurnRight(degreesToTurn=15, velocityPercentage=20)
    await RW.proportionalSpinTurnLeft(degreesToTurn=12, velocityPercentage=20)

    return

async def _runMission7() -> None:
    #Mission 7 (Humongous Fungus)

    motor.run_for_degrees(port.C, 500, 1110)
    await RW.moveForwardGyro(3.5000000000000, velocityPercentage=60)
    await motor.run_for_degrees(port.C, 1400, 1110)
    await RW.moveForwardGyro(0.2, velocityPercentage=40)
    motor.run_for_degrees(port.C, 600, 1110)
    await RW.moveBackwardGyro(stoppingRotations=0.4, velocityPercentage=50)
    return

async def _runMission6(forwardRotations=0.51) -> None:
    #Mission 6 (Leafcutter Frenzy)
    await RW.moveStraightUntilLine(leftLightSensorPort=port.E, rightLightSensorPort=port.F, lineColor=color.BLACK, velocityPercentage=50)
    await RW.proportionalSpinTurnLeft(degreesToTurn=90, velocityPercentage=20)

    #await RW.pidBlackLineFollow(1.4, lightSensorPort=port.F, midPointReflectionPercentage=60, edgeToFollow=RW.BLACK_LINE_LEFT_EDGE, proportionalCorrectionCoef=0.1, velocityPercentage=8) #before derivative correction
    await RW.pidBlackLineFollow(1.4, lightSensorPort=port.F, midPointReflectionPercentage=60, edgeToFollow=RW.BLACK_LINE_LEFT_EDGE, proportionalCorrectionCoef=0.1, derivativeCorrectionCoef=3.0, velocityPercentage=10)
    await RW.proportionalSpinTurnLeft(degreesToTurn=85)
    await RW.moveBackward(0.8, velocityPercentage=10)
    await RW.moveForwardGyro(forwardRotations, velocityPercentage=50, acceleration=400, brakeStartValue=0.8, correctionMultiplier=-3.5)

    return


async def _runMission11() -> None:
    #Mission 11 (Window to the Past)
    await RW.proportionalSpinTurnLeft(degreesToTurn=83, velocityPercentage=25)
    await RW.moveForwardGyro(4, velocityPercentage=75, acceleration=400, brakeStartValue=0.8, correctionMultiplier=-3.5)
    return


async def runMission7_6_11() -> None:
    await _runMission7()
    await _runMission6()
    await _runMission11()
    return



async def runMission6_11() -> None:
    #use if Mission 7 (Humongous Fungus) is not to be run
    await RW.moveForwardGyro(stoppingRotations=3.3, velocityPercentage=65)
    await RW.moveStraightUntilLine(leftLightSensorPort=port.E, rightLightSensorPort=port.F, lineColor=color.BLACK, velocityPercentage=30)

    await _runMission6(0.64)
    await _runMission11()
    return


async def _runMission13() -> None:
    #Mission 13 (Keystone Species)
    await RW.moveForwardGyro(3.7, velocityPercentage=40)
    await RW.proportionalPivotTurnRight(45)
    await RW.moveForwardGyro(0.25, velocityPercentage=30)
    return


async def _runMission12() -> None:
    #Mission 12 (Forest Elder)
    await motor.run_for_degrees(port.D, -120, 400)
    await RW.moveBackwardGyro(0.37, velocityPercentage=30)
    await RW.proportionalPivotTurnLeft(30)
    await RW.arcTurnRight(42, 85, velocityPercentage=-50)
    return


async def runMission13_12() -> None:
    await _runMission13()
    await _runMission12()

async def _runMission15() -> None:
    # Biocentric Architecture
    await RW.moveForwardGyro(1.2 , velocityPercentage=25)
    await RW.moveBackwardGyro(2, velocityPercentage=100)
    return
async def main():
    RW.initializeRobot(name="Misty", mainPortLeft=port.A, mainPortRight=port.B)
    # await _runMission15()
    # await _runMission7()
    # await _runMission6()
    await runMission7_6_11()
    # await runMission13_12()

    #await runMission6_11()

    #right home base to left home base
    #await RW.arcTurnLeft(32, 90, velocityPercentage=20)
    #await RW.moveForwardGyro(4, velocityPercentage=40)
    #await RW.proportionalSpinTurnLeft(45)
    #await RW.moveForward(1.4, velocityPercentage=40)

runloop.run(main())