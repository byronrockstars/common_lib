from hub import port
import runloop
import color
import Combined as RW


async def main():
    # Mission 7 (Humongous Fungus)

    robot = RW.initializeRobot(
        name="Misty",
        mainPortLeft=port.A,
        mainPortRight=port.B,
    )

    await RW.moveStraightUntilLine(
        leftLightSensorPort=port.E,
        rightLightSensorPort=port.F,
        lineColor=color.BLACK,
        velocityPercentage=30,
    )

    await RW.moveBackwardGyro(stoppingRotations=0.45, velocityPercentage=25)
    await RW.proportionalSpinTurnRight(degreesToTurn=15)
    await RW.proportionalSpinTurnLeft(degreesToTurn=15)


runloop.run(main())
