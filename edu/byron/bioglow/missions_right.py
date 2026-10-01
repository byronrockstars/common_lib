from hub import port
import runloop
import color
import Combined as RW


async def _runMission7() -> None:
    #Mission 7 (Humongous Fungus)
    await RW.moveStraightUntilLine(leftLightSensorPort=port.E, rightLightSensorPort=port.F, lineColor=color.BLACK, velocityPercentage=30)
    #await RW.moveForwardGyro(stoppingRotations=2.5, velocityPercentage=30) #could use wheel rotations instead of black line

    await RW.moveBackwardGyro(stoppingRotations=0.45, velocityPercentage=25)
    await RW.proportionalSpinTurnRight(degreesToTurn=15)
    await RW.proportionalSpinTurnLeft(degreesToTurn=15)

    return


async def _runMission6() -> None:
    #Mission 6 (Leafcutter Frenzy)
    await RW.moveStraightUntilLine(leftLightSensorPort=port.E, rightLightSensorPort=port.F, lineColor=color.BLACK, velocityPercentage=50)
    await RW.proportionalSpinTurnLeft(degreesToTurn=90)

    #await RW.pidBlackLineFollow(1.4, lightSensorPort=port.F, midPointReflectionPercentage=60, edgeToFollow=RW.BLACK_LINE_LEFT_EDGE, proportionalCorrectionCoef=0.1, velocityPercentage=8) #before derivative correction
    await RW.pidBlackLineFollow(1.4, lightSensorPort=port.F, midPointReflectionPercentage=60, edgeToFollow=RW.BLACK_LINE_LEFT_EDGE, proportionalCorrectionCoef=0.1,  derivativeCorrectionCoef=3.0, velocityPercentage=8)
    await RW.proportionalSpinTurnLeft(degreesToTurn=85)
    await RW.moveBackward(0.75, velocityPercentage=10)
    await RW.moveForwardGyro(0.75, velocityPercentage=50, acceleration=400, brakeStartValue=0.8, correctionMultiplier=-3.5)

    return


async def _runMission11() -> None:
    #Mission 11 (Window to the Past)
    await RW.proportionalSpinTurnLeft(degreesToTurn=95, velocityPercentage=25)
    await RW.moveForwardGyro(4, velocityPercentage=75, acceleration=400, brakeStartValue=0.8, correctionMultiplier=-3.5)
    return


async def runMission7_6_11() -> None:
    await _runMission7()
    await _runMission6()
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
    await RW.proportionalPivotTurnRight(45)
    await RW.moveBackwardGyro(4, velocityPercentage=40)
    return



async def main():
    RW.initializeRobot(name="Misty", mainPortLeft=port.A, mainPortRight=port.B)

    #await runMission7_6_11()
    await _runMission13()
    await _runMission12()
    


runloop.run(main())