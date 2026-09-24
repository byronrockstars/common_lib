from hub import port
import runloop
import color
import Combined as RW


async def runMission3() -> None:
    #Mission 3 (Flip the Rock)
    # Works 100% of the time even with interesting obstacles sometimes
    await RW.moveForward(rotations=2.38, velocityPercentage=40)
    await RW.moveBackward(rotations=2.35, velocityPercentage=100, acceleration=10000, deceleration=4000) #acceleration/deceleration of 10,000 is max
    return  


async def main():

    robot = RW.initializeRobot(
        name="Misty",
        mainPortLeft=port.A,
        mainPortRight=port.B,
    )

    await runMission3()

runloop.run(main())