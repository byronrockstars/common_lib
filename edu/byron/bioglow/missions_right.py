from hub import port
import runloop
import color
import Combined as RW


async def _runMission7() -> None:
    #Mission 7 (Humongous Fungus)
    await RW.moveStraightUntilLine(
        leftLightSensorPort=port.E,
        rightLightSensorPort=port.F,
        lineColor=color.BLACK,
        velocityPercentage=30,
    )
    
    #await moveStraightWheelRotation(2.5, velocityPercentage=30) #could use wheel rotations instead of black line

    #TODO: moveBackwardGyro has a bug
    await RW.moveBackwardGyro(stoppingRotations=0.45, velocityPercentage=25)
    await RW.proportionalSpinTurnRight(degreesToTurn=15)
    await RW.proportionalSpinTurnLeft(degreesToTurn=15)
    
    return


#TODO: these missions need to be converted to wrapper
async def _runMission6() -> None:
    #Mission 6 (Leafcutter Frenzy)
    await moveStraightUntilLine(port.E, port.F, color.BLACK, velocityPercentage=50)

    await proportionalSpinTurn(-90)
    #await pidBlackLineFollow(1.4, port.A, 60, BLACK_LINE_LEFT_EDGE, 0.1, velocityPercentage=8) #before derivative correction
    await pidBlackLineFollow(1.4, port.F, 60, BLACK_LINE_LEFT_EDGE, 0.1, derivativeCorrectionCoef=3.0, velocityPercentage=8)
    await proportionalSpinTurn(-85)
    await moveForward(-0.75, 10)
    await moveStraightWheelRotation(.75, 50, correctionMultiplier=-3.5, brakeStartValue=0.8, acceleration=400)
    return


async def _runMission11() -> None:
    #Mission 11 (Window to the Past)
    await moveStraightWheelRotation(.75, 50, correctionMultiplier=-3.5, brakeStartValue=0.8, acceleration=400)
    await proportionalSpinTurn(-95)
    await moveStraightWheelRotation(4, 75, correctionMultiplier=-3.5, brakeStartValue=0.8, acceleration=400)
    return


async def runMission7_6_11() -> None:
    await _runMission7()
    await _runMission6()
    await _runMission11()
    return
    
    
async def _runMission13() -> None:
    #Mission 13 (Keystone Species)
    await moveStraightWheelRotation(3.7, velocityPercentage=40)
    await proportionalPivotTurn(45)
    await moveStraightWheelRotation(0.25, velocityPercentage=30)
    await moveStraightWheelRotation(-0.37, velocityPercentage=30)
    return


async def main():

    robot = RW.initializeRobot(
        name="Misty",
        mainPortLeft=port.A,
        mainPortRight=port.B,
    )

    _runMission7()


runloop.run(main())
